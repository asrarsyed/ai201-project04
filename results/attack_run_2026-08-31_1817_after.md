# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-08-31 18:17
- Auto-marked BROKE (5xx, crash, no response): **1**
- Left for you to judge: **55**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `502e2170-85ce-40b2-a7b8-56a0bf1ed699` | human | 0.472 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `6cfefae5-1211-42b5-977a-e55386328d6a` | unsure | 0.181 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `7d3eb974-0060-475d-96da-8cb2ea936e7c` | unsure | 0.019 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `2aca5a6e-df49-4ee9-af0a-6a1d9309f4a4` | unsure | 0.074 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `6894aae9-fbc5-40f1-a35b-b33d07d9ef24` | human | 0.352 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `3d52cba8-0ed0-4d94-91b1-9dc07a0d32ae` | unsure | 0.285 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `468cfecd-3e6a-467b-859a-3b7a32fa5423` | unsure | 0.057 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `5c0c0d76-4628-4373-8895-e5313b878b20` | human | 0.474 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `1734604e-270f-44e6-b23e-4a8a73904eac` | unsure | 0.081 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `d53e8ad3-0e59-4ea1-b27a-f49ba91e8aed` | ai | 0.331 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `430c7aa8-fde4-41bc-b5f9-624fdb3e2430` | unsure | 0.119 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `f35b427b-6453-424e-9b58-c2f5a6171b28` | unsure | 0.062 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `b9dad510-9cdf-4b52-808f-28bef4d1120d` | unsure | 0.089 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `f645b953-3251-4f45-be64-ed5d6b3ca837` | unsure | 0.078 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `69c0ae17-3186-46db-9911-da3dea67906a` | ai | 0.139 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `6a814235-eb8c-4196-8e03-e036acb8991b` | unsure | 0.091 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `059b3957-3516-44b7-b5ee-38d4782dde7c` | unsure | 0.094 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `9ceb38ce-07a8-415a-8b17-8097d07eff0a` | human | 0.454 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `24c8abc5-2e10-4343-963e-fcff95d5c0b3` | human | 0.387 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `183a36d8-ada5-46af-b186-f833c17e4071` | human | 0.508 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `7cdacf0d-62e1-452b-a17d-2235e0b348c4` | unsure | 0.038 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `2ff2bfd3-0a07-4db3-bdd2-710895bcba22` | unsure | 0.246 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `9e255ee5-0d48-418c-b5b3-2a678967bff0` | unsure | 0.128 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `ad7bd03e-3225-4454-8d53-baee1ec9a67d` | unsure | 0.168 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `3c560a35-d285-42e9-9ef2-a8589dcb3e1c` | human | 0.600 |  |
| MF04 | malformed | text is only punctuation | 200 | `bb560ed6-627c-4199-bdc4-6b519ad83a47` | human | 0.323 |  |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — |  |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — |  |
| MF07 | malformed | text is right-to-left script | 200 | `4ba5b276-eec5-446b-ae73-27c281ec6fe1` | ai | 0.482 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `34fcec3c-9c60-4e58-bbdc-2bb648dcf237` | ai | 0.411 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 200 | `f340b6b4-f93a-41b2-9218-3d387bf57d08` | human | 0.384 |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 200 | `a5b9e96f-fd7d-43ad-8064-c50e88f407c9` | human | 0.556 |  |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9075b8cb-60ca-4642-8a79-f29069e3b84d` | human | 0.574 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2571528e-f6a8-423c-bbfc-c76765e72c75` | human | 0.574 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `d61bbb4c-fab8-43ff-9f50-c65f72b4fcc5` | human | 0.574 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `ca3fece6-7553-4a4d-bc00-3791213b3323` | human | 0.574 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `a502f029-b13f-43b2-a142-948272c4a611` | human | 0.574 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `3c71db61-25ef-4674-b15c-58708dc008ff` | human | 0.574 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 1 | 19 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "502e2170-85ce-40b2-a7b8-56a0bf1ed699",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.4719,
  "model_score": 0.1635,
  "style_score": 0.4762,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "6cfefae5-1211-42b5-977a-e55386328d6a",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.1809,
  "model_score": 0.5943,
  "style_score": 0.3553,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "7d3eb974-0060-475d-96da-8cb2ea936e7c",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.0195,
  "model_score": 0.6662,
  "style_score": 0.5249,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "2aca5a6e-df49-4ee9-af0a-6a1d9309f4a4",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.0737,
  "model_score": 0.6114,
  "style_score": 0.4701,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "6894aae9-fbc5-40f1-a35b-b33d07d9ef24",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3517,
  "model_score": 0.3212,
  "style_score": 0.449,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "3d52cba8-0ed0-4d94-91b1-9dc07a0d32ae",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.2846,
  "model_score": 0.5727,
  "style_score": 0.25,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "468cfecd-3e6a-467b-859a-3b7a32fa5423",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.0573,
  "model_score": 0.5862,
  "style_score": 0.6621,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "5c0c0d76-4628-4373-8895-e5313b878b20",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.4736,
  "model_score": 0.2452,
  "style_score": 0.3821,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "1734604e-270f-44e6-b23e-4a8a73904eac",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.0813,
  "model_score": 0.7042,
  "style_score": 0.3562,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "d53e8ad3-0e59-4ea1-b27a-f49ba91e8aed",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.3312,
  "model_score": 0.9792,
  "style_score": 0.5624,
  "label": "We think this was probably written by AI.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "430c7aa8-fde4-41bc-b5f9-624fdb3e2430",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.119,
  "model_score": 0.6175,
  "style_score": 0.4065,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "f35b427b-6453-424e-9b58-c2f5a6171b28",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.0619,
  "model_score": 0.7387,
  "style_score": 0.4963,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "b9dad510-9cdf-4b52-808f-28bef4d1120d",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.0891,
  "model_score": 0.8051,
  "style_score": 0.4556,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "f645b953-3251-4f45-be64-ed5d6b3ca837",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.0783,
  "model_score": 0.8329,
  "style_score": 0.4109,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "69c0ae17-3186-46db-9911-da3dea67906a",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.1386,
  "model_score": 0.8005,
  "style_score": 0.5227,
  "label": "We think this was probably written by AI.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "6a814235-eb8c-4196-8e03-e036acb8991b",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.091,
  "model_score": 0.8814,
  "style_score": 0.3722,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "059b3957-3516-44b7-b5ee-38d4782dde7c",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.0944,
  "model_score": 0.8816,
  "style_score": 0.3762,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "9ceb38ce-07a8-415a-8b17-8097d07eff0a",
  "creator_id": "attacker_FP08",
  "guess": "human",
  "confidence": 0.4543,
  "model_score": 0.3223,
  "style_score": 0.3196,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "24c8abc5-2e10-4343-963e-fcff95d5c0b3",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.3869,
  "model_score": 0.4625,
  "style_score": 0.2461,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "183a36d8-ada5-46af-b186-f833c17e4071",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.5079,
  "model_score": 0.2044,
  "style_score": 0.3852,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "7cdacf0d-62e1-452b-a17d-2235e0b348c4",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.0381,
  "model_score": 0.5943,
  "style_score": 0.5338,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "2ff2bfd3-0a07-4db3-bdd2-710895bcba22",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.2458,
  "model_score": 0.4998,
  "style_score": 0.3805,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "9e255ee5-0d48-418c-b5b3-2a678967bff0",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.1278,
  "model_score": 0.6401,
  "style_score": 0.3702,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "ad7bd03e-3225-4454-8d53-baee1ec9a67d",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.1682,
  "model_score": 0.5583,
  "style_score": 0.4117,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "3c560a35-d285-42e9-9ef2-a8589dcb3e1c",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.6,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "bb560ed6-627c-4199-bdc4-6b519ad83a47",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.3233,
  "model_score": 0.0112,
  "style_score": 0.8333,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "4ba5b276-eec5-446b-ae73-27c281ec6fe1",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.4824,
  "model_score": 0.9064,
  "style_score": 0.8333,
  "label": "We think this was probably written by AI.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "34fcec3c-9c60-4e58-bbdc-2bb648dcf237",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.4111,
  "model_score": 0.9876,
  "style_score": 0.6528,
  "label": "We think this was probably written by AI.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "f340b6b4-f93a-41b2-9218-3d387bf57d08",
  "creator_id": null,
  "guess": "human",
  "confidence": 0.3844,
  "model_score": 0.2395,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "a5b9e96f-fd7d-43ad-8064-c50e88f407c9",
  "creator_id": {
    "id": "x"
  },
  "guess": "human",
  "confidence": 0.5557,
  "model_score": 0.0492,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 500,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;list&#39; object has no attribute &#39;get&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes",
  "verdict": "BROKE"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "9075b8cb-60ca-4642-8a79-f29069e3b84d",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "2571528e-f6a8-423c-bbfc-c76765e72c75",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "d61bbb4c-fab8-43ff-9f50-c65f72b4fcc5",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "ca3fece6-7553-4a4d-bc00-3791213b3323",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "a502f029-b13f-43b2-a142-948272c4a611",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "3c71db61-25ef-4674-b15c-58708dc008ff",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
