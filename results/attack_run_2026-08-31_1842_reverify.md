# Attack run — reverify

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-08-31 18:42
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
| EV01 | evasion | signal two: typos raise word variety | 200 | `76656825-e592-4f24-9413-130e2cdf7a60` | human | 0.472 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `9d039181-c558-401e-8ad8-28a375958072` | unsure | 0.181 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `9b0485ca-59bc-48cc-a935-e3fe899b8e49` | unsure | 0.019 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `5432d13c-20a0-4f03-b2af-e78cc7466509` | unsure | 0.074 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `ddc4c7cd-5cf5-47a2-aa5a-a020af51cb39` | human | 0.352 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `e8dae76f-4248-43a2-ab56-c68fe1ce3f00` | unsure | 0.285 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `3126122e-88de-4f4d-a9a7-fa3c13b8bf6d` | unsure | 0.057 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `e1ced6c2-369f-4cb9-ad1e-100cfee1d557` | human | 0.474 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `8b8051b9-c9fe-4975-ab54-7d061483dc51` | unsure | 0.081 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `1cbf1fb3-b527-4a49-927c-a588699e9f64` | ai | 0.331 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `fbe4d80c-97fb-4d79-8fc6-4478040aae83` | unsure | 0.119 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `5d8a7b00-81a4-41f0-8ce4-cb65c7e61c0a` | unsure | 0.062 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `6d3e40c9-05bf-4c8e-b8a1-67b12210c2ad` | unsure | 0.089 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c1c0727e-c260-4afb-98be-43488e0d5b50` | unsure | 0.078 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `b3ea5e64-0a2c-49d8-93a0-6b4961b54b98` | ai | 0.139 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `e775a0e1-168e-4246-ba08-6b3eaeaf1d3e` | unsure | 0.091 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `27225ddc-9581-41c3-b3f8-2228a7a678e5` | unsure | 0.094 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `37dc4596-430e-4f94-a8b2-68ea6190fba4` | human | 0.454 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `813bae67-5546-49c2-a644-6c295d0efaf8` | human | 0.387 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c1c9d175-2fb9-4351-a9aa-8bd9d4fed951` | human | 0.508 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `51a8d62d-4e65-4b9e-99d7-5b9671fa9590` | unsure | 0.038 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `61d6ac8a-cb23-463e-a1d7-9cfc18964eee` | unsure | 0.246 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `08bb4c26-f827-48fe-98cf-3274a8c0689d` | unsure | 0.128 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `de4d142d-96fa-4d60-8c62-d441efa2dce0` | unsure | 0.168 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `7996e57d-b4d3-4d8a-846e-15298ad6f264` | human | 0.600 |  |
| MF04 | malformed | text is only punctuation | 200 | `2b730d32-fda8-4d83-a558-36482357f034` | human | 0.323 |  |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — |  |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — |  |
| MF07 | malformed | text is right-to-left script | 200 | `8d46c3b8-c8ad-4685-86a7-29948ede17ff` | ai | 0.482 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `07c06e04-6785-4a87-a3f7-f805179855a4` | ai | 0.411 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 200 | `2efbf2e6-4dd3-4e2f-b17b-0c01cdd2d2db` | human | 0.384 |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 200 | `e039593f-68c0-4a4a-aa55-e6fd9a33ecde` | human | 0.556 |  |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `36777482-9323-4b6b-bccd-e1433205ecb2` | human | 0.574 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `32e34078-91ec-4aa0-9902-2ec48f9f647e` | human | 0.574 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c7edc329-094d-48d9-83eb-449cf89fb037` | human | 0.574 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `e5369841-19f7-4999-8515-9d9472e307ac` | human | 0.574 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9de9a507-bd70-40de-af0a-086bef637a0e` | human | 0.574 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `9d4b8a1c-cb8f-4fbe-bf34-7de789a9173a` | human | 0.574 |  |
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
  "content_id": "76656825-e592-4f24-9413-130e2cdf7a60",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.4719,
  "model_score": 0.1635,
  "style_score": 0.4762,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "9d039181-c558-401e-8ad8-28a375958072",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.1809,
  "model_score": 0.5943,
  "style_score": 0.3553,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "9b0485ca-59bc-48cc-a935-e3fe899b8e49",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.0195,
  "model_score": 0.6662,
  "style_score": 0.5249,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "5432d13c-20a0-4f03-b2af-e78cc7466509",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.0737,
  "model_score": 0.6114,
  "style_score": 0.4701,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "ddc4c7cd-5cf5-47a2-aa5a-a020af51cb39",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3517,
  "model_score": 0.3212,
  "style_score": 0.449,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "e8dae76f-4248-43a2-ab56-c68fe1ce3f00",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.2846,
  "model_score": 0.5727,
  "style_score": 0.25,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "3126122e-88de-4f4d-a9a7-fa3c13b8bf6d",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.0573,
  "model_score": 0.5862,
  "style_score": 0.6621,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "e1ced6c2-369f-4cb9-ad1e-100cfee1d557",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.4736,
  "model_score": 0.2452,
  "style_score": 0.3821,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "8b8051b9-c9fe-4975-ab54-7d061483dc51",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.0813,
  "model_score": 0.7042,
  "style_score": 0.3562,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "1cbf1fb3-b527-4a49-927c-a588699e9f64",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.3312,
  "model_score": 0.9792,
  "style_score": 0.5624,
  "label": "We think this was probably written by AI. That's a guess from automated checks, not a finding \u2014 they're wrong sometimes. If you wrote this yourself, you can appeal and a person will look at it.",
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
  "content_id": "fbe4d80c-97fb-4d79-8fc6-4478040aae83",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.119,
  "model_score": 0.6175,
  "style_score": 0.4065,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "5d8a7b00-81a4-41f0-8ce4-cb65c7e61c0a",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.0619,
  "model_score": 0.7387,
  "style_score": 0.4963,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "6d3e40c9-05bf-4c8e-b8a1-67b12210c2ad",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.0891,
  "model_score": 0.8051,
  "style_score": 0.4556,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "c1c0727e-c260-4afb-98be-43488e0d5b50",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.0783,
  "model_score": 0.8329,
  "style_score": 0.4109,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "b3ea5e64-0a2c-49d8-93a0-6b4961b54b98",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.1386,
  "model_score": 0.8005,
  "style_score": 0.5227,
  "label": "We think this was probably written by AI. That's a guess from automated checks, not a finding \u2014 they're wrong sometimes. If you wrote this yourself, you can appeal and a person will look at it.",
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
  "content_id": "e775a0e1-168e-4246-ba08-6b3eaeaf1d3e",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.091,
  "model_score": 0.8814,
  "style_score": 0.3722,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "27225ddc-9581-41c3-b3f8-2228a7a678e5",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.0944,
  "model_score": 0.8816,
  "style_score": 0.3762,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "37dc4596-430e-4f94-a8b2-68ea6190fba4",
  "creator_id": "attacker_FP08",
  "guess": "human",
  "confidence": 0.4543,
  "model_score": 0.3223,
  "style_score": 0.3196,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "813bae67-5546-49c2-a644-6c295d0efaf8",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.3869,
  "model_score": 0.4625,
  "style_score": 0.2461,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "c1c9d175-2fb9-4351-a9aa-8bd9d4fed951",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.5079,
  "model_score": 0.2044,
  "style_score": 0.3852,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "51a8d62d-4e65-4b9e-99d7-5b9671fa9590",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.0381,
  "model_score": 0.5943,
  "style_score": 0.5338,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "61d6ac8a-cb23-463e-a1d7-9cfc18964eee",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.2458,
  "model_score": 0.4998,
  "style_score": 0.3805,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "08bb4c26-f827-48fe-98cf-3274a8c0689d",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.1278,
  "model_score": 0.6401,
  "style_score": 0.3702,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "de4d142d-96fa-4d60-8c62-d441efa2dce0",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.1682,
  "model_score": 0.5583,
  "style_score": 0.4117,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way. Nothing has been decided, and you can appeal at any time if you'd like a person to look at it.",
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
  "content_id": "7996e57d-b4d3-4d8a-846e-15298ad6f264",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.6,
  "model_score": 0.0,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "2b730d32-fda8-4d83-a558-36482357f034",
  "creator_id": "attacker_MF04",
  "guess": "human",
  "confidence": 0.3233,
  "model_score": 0.0112,
  "style_score": 0.8333,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "8d46c3b8-c8ad-4685-86a7-29948ede17ff",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.4824,
  "model_score": 0.9064,
  "style_score": 0.8333,
  "label": "We think this was probably written by AI. That's a guess from automated checks, not a finding \u2014 they're wrong sometimes. If you wrote this yourself, you can appeal and a person will look at it.",
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
  "content_id": "07c06e04-6785-4a87-a3f7-f805179855a4",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.4111,
  "model_score": 0.9876,
  "style_score": 0.6528,
  "label": "We think this was probably written by AI. That's a guess from automated checks, not a finding \u2014 they're wrong sometimes. If you wrote this yourself, you can appeal and a person will look at it.",
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
  "content_id": "2efbf2e6-4dd3-4e2f-b17b-0c01cdd2d2db",
  "creator_id": null,
  "guess": "human",
  "confidence": 0.3844,
  "model_score": 0.2395,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "e039593f-68c0-4a4a-aa55-e6fd9a33ecde",
  "creator_id": {
    "id": "x"
  },
  "guess": "human",
  "confidence": 0.5557,
  "model_score": 0.0492,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "36777482-9323-4b6b-bccd-e1433205ecb2",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "32e34078-91ec-4aa0-9902-2ec48f9f647e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "c7edc329-094d-48d9-83eb-449cf89fb037",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "e5369841-19f7-4999-8515-9d9472e307ac",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "9de9a507-bd70-40de-af0a-086bef637a0e",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
  "content_id": "9d4b8a1c-cb8f-4fbe-bf34-7de789a9173a",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.5742,
  "model_score": 0.0287,
  "style_score": 0.5,
  "label": "We think this was probably written by a person. If you think we got this wrong, you can appeal and a person will look at it.",
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
