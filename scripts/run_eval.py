#!/usr/bin/env python3
"""
Runs the acceptance criteria in docs/REQUIREMENTS.md against a running
service, three trials each (the model signal can score identical input
differently between runs, which is why repeats matter).

    python -m authentiwrite.app              # in one terminal
    python scripts/run_eval.py --label before  # in another
    python scripts/run_eval.py --label after

Scenarios live in src/authentiwrite/scenarios.py. This script sends
requests and records results. It does not decide pass or fail, which is read
against the criteria by hand, so the Verdict column comes back blank.
"""

import argparse
import datetime as dt
import json
import sys

from authentiwrite import config

# Windows consoles often run a codepage that can't print every character in
# this file's help text. Without this, `--help` ends in a UnicodeEncodeError
# traceback instead of the help, which is a miserable first thing to hit.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):  # not a normal text stream
        pass


DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"


def bodies_for(scenario):
    """
    The request bodies one scenario sends.

    A "texts" scenario gets a creator_id made up for it. A "bodies" scenario is
    sent exactly as written, which is how a bad-input criterion says things a
    string can't: no `text` field at all, a null, something enormous.
    """
    if scenario.get("bodies"):
        return list(scenario["bodies"])
    return [
        {"text": text, "creator_id": f"eval_{scenario['name'][:12]}_{i}"}
        for i, text in enumerate(scenario["texts"], 1)
    ]


def describe(body):
    """A short, readable note of what was sent, for the report."""
    if set(body) == {"text", "creator_id"} and isinstance(body.get("text"), str):
        text = body["text"]
        return text[:70] if text else "(empty text)"
    return json.dumps(body)[:120]


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("The `requests` package isn't installed.\n"
              "Run: pip install -e '.[dev]'", file=sys.stderr)
        sys.exit(1)

    from authentiwrite import scenarios

    problems = scenarios.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    try:
        requests.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it: python -m authentiwrite.app",
              file=sys.stderr)
        sys.exit(1)

    if args.trials < 3:
        print(f"!! {args.trials} trial(s), fewer than the usual three.\n")

    rows = []
    for scenario in scenarios.SCENARIOS:
        print(f"\n{scenario['name']}  (criterion {scenario.get('criterion') or '—'})")

        is_appeal = scenario.get("kind") == "appeal"

        trials = []
        for trial in range(1, args.trials + 1):
            results = []
            for i, body in enumerate(bodies_for(scenario), 1):
                preview = describe(body)
                try:
                    response = requests.post(f"{args.url}/submit", json=body,
                                             timeout=args.timeout)
                    payload = response.json() if response.content else {}
                    result = {
                        "status": response.status_code,
                        "guess": payload.get("guess"),
                        "confidence": payload.get("confidence"),
                        "model_score": payload.get("model_score"),
                        "style_score": payload.get("style_score"),
                        "label": payload.get("label"),
                        "sent": preview,
                    }

                    if is_appeal and payload.get("content_id"):
                        content_id = payload["content_id"]
                        status_before = payload.get("guess") and "decided"
                        appeal_response = requests.post(
                            f"{args.url}/appeal",
                            json={
                                "content_id": content_id,
                                "reasoning": "Evaluation scenario: testing the appeal path.",
                            },
                            timeout=args.timeout,
                        )
                        appeal_payload = (
                            appeal_response.json() if appeal_response.content else {}
                        )
                        log_response = requests.get(
                            f"{args.url}/content/{content_id}", timeout=args.timeout
                        )
                        log_payload = (
                            log_response.json() if log_response.content else {}
                        )
                        result["appeal_status_code"] = appeal_response.status_code
                        result["appeal_response_status"] = appeal_payload.get("status")
                        result["status_before"] = status_before
                        result["status_after"] = log_payload.get("status")
                        result["status_changed"] = (
                            status_before is not None
                            and log_payload.get("status") is not None
                            and log_payload.get("status") != status_before
                        )

                    results.append(result)
                except Exception as exc:  # noqa: BLE001
                    results.append({"status": None, "error": f"{type(exc).__name__}: {exc}",
                                    "sent": preview})

            trials.append(results)
            if is_appeal:
                changed = [str(r.get("status_changed")) for r in results]
                print(f"  trial {trial}: status_changed = {', '.join(changed)}")
            else:
                guesses = [r.get("guess") or "—" for r in results]
                print(f"  trial {trial}: {', '.join(guesses)}")

        rows.append({"scenario": scenario, "trials": trials})

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.trials
    headers = " | ".join(f"Run {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)

    lines = [
        f"# Run log{f': {args.label}' if args.label else ''}",
        "",
        "- Produced by: `scripts/run_eval.py::main`",
        "- Service: `authentiwrite/app.py::submit` · scoring: `authentiwrite/scoring.py::combine_signals`",
        f"- {n} trials per criterion · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Target/Verdict filled in from docs/REQUIREMENTS.md against the output below.",
        "",
        f"| Criterion | Target | {headers} | Verdict |",
        f"|---|---|{divider}|---|",
    ]

    for row in rows:
        scenario = row["scenario"]
        number = scenario.get("criterion")
        name = f"{number}. {scenario['name']}" if number else scenario["name"]
        lines.append(f"| {name} |  | {' | '.join([' '] * n)} |  |")

    lines += ["", "---", "", "## What actually came back", "",
              "The unedited response for every request in this run. This is the",
              "evidence behind the numbers quoted in docs/RESEARCH.md.", ""]

    for row in rows:
        scenario = row["scenario"]
        lines += [f"### {scenario['name']}", ""]
        for trial_number, results in enumerate(row["trials"], 1):
            lines += [f"**Trial {trial_number}**", "", "```json",
                      json.dumps(results, indent=2), "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")
    print("That file is the evidence this run actually happened.")


if __name__ == "__main__":
    main()
