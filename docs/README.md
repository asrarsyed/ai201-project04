# Documentation

Start with [PROJECT.md](PROJECT.md).

| Document | What's in it |
|---|---|
| [PROJECT.md](PROJECT.md) | What the service is, why it exists, what it's trying to do, and what it deliberately isn't. Start here. |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Layout, request flow, what each of the three signals measures and where it's blind, the shape of the runtime data, and the known limitations. |
| [DECISIONS.md](DECISIONS.md) | Every significant design decision and the reasoning behind it. Weights, thresholds, label wording, how rate limiting is keyed, and two signals that were built and then rejected. |
| [RESEARCH.md](RESEARCH.md) | The evidence. Calibration data, the 56-attack run before and after the reweight, the acceptance-criteria results, and both rejected signal investigations in full. |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Functional and non-functional requirements, plus the five acceptance criteria with their targets and current results. |
| [REFERENCES.md](REFERENCES.md) | Terms used across these docs, plus data sources and libraries. |

## Where to start, depending on what you want

**"Does this actually work?"** Read [RESEARCH.md](RESEARCH.md), then the
known limitations at the end of [ARCHITECTURE.md](ARCHITECTURE.md).

**"Why is it built this way?"** Read [DECISIONS.md](DECISIONS.md).

**"I need to change something."** Read [ARCHITECTURE.md](ARCHITECTURE.md)
to find where the code lives, then check [DECISIONS.md](DECISIONS.md) to
see whether the thing you're about to change was already argued about.

The history of changes is in `git log`. These documents describe the
service as it stands now.
