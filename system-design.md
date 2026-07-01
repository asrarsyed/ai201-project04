# Project Structure

```
.
├── detection
│   ├── classifier.py           # signal 1: LLM-as-judge (Groq)
│   ├── scorer.py               # combines both signals -> confidence score
│   └── stylometrics.py         # signal 2: sentence variance, TTR, etc.
├── production
│   ├── appeals.py              # POST /appeal logic: status update + log entry
│   ├── auditor.py              # writes/reads audit log
│   └── responder.py            # score -> transparency label text
├── storage/
│   └── audit.jsonl             # append-only structured audit log
├── .envrc                      # GROQ_API_KEY, loaded via direnv, not committed
├── app.py                      # Flask app: /submit, /appeal, /log routes
├── config.py                   # rate limits, score thresholds, model name
├── planning.md                 # required at root by name - final architecture
├── README.md                   # required deliverable - signals, labels, limits, AI usage
├── requirements.txt            # flask, flask-limiter, groq
└── system-design.md            # scratch spec / pre-planning.md draft
```
```
```
```
