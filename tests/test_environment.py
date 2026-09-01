#!/usr/bin/env python3
"""
Environment check: Python version, virtual environment, dependencies from
pyproject.toml, disk/RAM headroom for the local model, and whether the
service starts and answers /ping.

    python tests/test_environment.py

No API key needed, because everything runs locally.
"""

import importlib
import importlib.metadata as md
import os
import platform
import shutil
import sys
import tomllib
from pathlib import Path

MIN_PYTHON = (3, 11)
MAX_PYTHON = (3, 14)  # exclusive, because 3.14 breaks the pinned packages
MIN_DISK_GB = 9   # torch is most of it; the detector model adds ~550 MB
MIN_RAM_GB = 4

# Distribution name on PyPI -> module name actually imported.
IMPORT_NAMES = {
    "flask-limiter": "flask_limiter",
    "scikit-learn": "sklearn",
    "pyyaml": "yaml",
    "pillow": "PIL",
}

ROOT = Path(__file__).resolve().parent.parent

passed, failed, warned, skipped = [], [], [], []


def report(status, name, detail=""):
    line = f"[{status:<4}] {name}"
    if detail:
        line += f"\n         {detail}"
    print(line)
    {"PASS": passed, "FAIL": failed, "WARN": warned, "SKIP": skipped}[status].append(name)


# --- 1. Python --------------------------------------------------------------

def check_python():
    v = sys.version_info
    actual = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) < MIN_PYTHON:
        return report("FAIL", "Python version", f"Found {actual}. This project needs 3.11 or newer.")
    if (v.major, v.minor) >= MAX_PYTHON:
        return report(
            "FAIL",
            "Python version",
            f"Found {actual}. The pinned packages do not support 3.14 yet. "
            f"install 3.13 and rebuild your virtual environment.",
        )
    report("PASS", "Python version", f"{actual} on {platform.system()}")


def check_venv():
    active = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    if not active:
        return report(
            "FAIL",
            "Virtual environment",
            "Not active. Run the activate command for your OS, then try again. "
            "Installing into your system Python is the most common cause of "
            "'it worked yesterday'.",
        )
    report("PASS", "Virtual environment", sys.prefix)


# --- 2. Packages ------------------------------------------------------------

def parse_dependencies(path):
    """Distribution names from pyproject.toml's [project.dependencies]."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    deps = data.get("project", {}).get("dependencies", [])
    names = []
    for spec in deps:
        name = spec.split("[")[0]
        for sep in ("==", ">=", "<=", "~=", "!=", ">", "<"):
            name = name.split(sep)[0]
        names.append(name.strip())
    return names


def check_packages():
    pyproject = ROOT / "pyproject.toml"
    if not pyproject.exists():
        return report("FAIL", "pyproject.toml", "Not found at the repo root.")

    missing = []
    for dist in parse_dependencies(pyproject):
        module = IMPORT_NAMES.get(dist.lower(), dist.replace("-", "_"))
        try:
            importlib.import_module(module)
        except Exception as e:
            missing.append(f"{dist} ({type(e).__name__})")

    if missing:
        return report(
            "FAIL",
            "Dependencies",
            "Could not import: " + ", ".join(missing) + "\n         Fix: pip install -e .",
        )
    report("PASS", "Dependencies", f"all {len(parse_dependencies(pyproject))} import cleanly")


# --- 3. Machine -------------------------------------------------------------

def total_ram_gb():
    try:
        if hasattr(os, "sysconf") and "SC_PAGE_SIZE" in os.sysconf_names:
            return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024**3
        if sys.platform == "win32":
            import ctypes

            class MemStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

            stat = MemStatus()
            stat.dwLength = ctypes.sizeof(MemStatus)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return stat.ullTotalPhys / 1024**3
    except Exception:
        pass
    return None


def check_machine():
    free_gb = shutil.disk_usage(ROOT).free / 1024**3
    if free_gb < MIN_DISK_GB:
        report("FAIL", "Free disk space",
               f"{free_gb:.1f} GB free, need about {MIN_DISK_GB} GB. "
               f"PyTorch and the detector model cache are most of it.")
    else:
        report("PASS", "Free disk space", f"{free_gb:.1f} GB")

    ram = total_ram_gb()
    if ram is None:
        report("SKIP", "Memory", "Could not read total RAM on this OS. Check it by hand.")
    elif ram < MIN_RAM_GB:
        report("WARN", "Memory",
               f"{ram:.1f} GB total, {MIN_RAM_GB} GB recommended. Things will run, "
               f"but close other apps while the model is loaded.")
    else:
        report("PASS", "Memory", f"{ram:.1f} GB")


# --- 4. What this pair actually runs ----------------------------------------

def check_torch():
    """Signal one runs a model on this machine."""
    try:
        import torch
    except ImportError:
        return report("FAIL", "PyTorch", "Not installed. Run: pip install -e .")
    report("PASS", "PyTorch", torch.__version__)


def check_flask():
    """The web service and its rate limiter."""
    try:
        import flask  # noqa: F401
    except ImportError as exc:
        return report("FAIL", "Flask", f"Could not import: {exc}")
    try:
        import flask_limiter  # noqa: F401
    except ImportError:
        return report("WARN", "Flask", "flask-limiter missing")
    report("PASS", "Flask", "flask and flask-limiter both import")


def check_detector_model():
    """Is the ~550 MB model already downloaded?"""
    from pathlib import Path as _P

    cache = _P.home() / ".cache" / "huggingface" / "hub"
    if cache.exists() and any("gpt2" in p.name for p in cache.iterdir()):
        return report("PASS", "Detector model", "already downloaded")
    report(
        "WARN",
        "Detector model",
        "Not downloaded yet (~550 MB). Run: python -m authentiwrite.detector",
    )


def check_service():
    """Does the service start and does the example route answer?"""
    sys.path.insert(0, str(ROOT / "src"))
    try:
        from authentiwrite import app as appmod
    except Exception as exc:  # noqa: BLE001
        return report("FAIL", "The service", f"authentiwrite.app wouldn't import: {exc}")

    try:
        client = appmod.app.test_client()
        response = client.post("/ping", json={"message": "check"})
    except Exception as exc:  # noqa: BLE001
        return report("FAIL", "The service", f"/ping raised: {exc}")

    if response.status_code != 200:
        return report("FAIL", "The service", f"/ping returned {response.status_code}")
    report("PASS", "The service", "/ping answers")


def main():
    print("\nAuthentiWrite environment check\n" + "-" * 60)
    check_python()
    check_venv()
    check_packages()
    check_machine()
    check_torch()
    check_flask()
    check_detector_model()
    check_service()

    print("-" * 60)
    print(f"{len(passed)} passed, {len(failed)} failed, "
          f"{len(warned)} to look at, {len(skipped)} skipped\n")
    if failed:
        print("Not ready yet. Fix the FAIL lines above and run this again.\n")
        return 1
    print("Environment looks good.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
