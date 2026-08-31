# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-08-31 17:26
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
| EV01 | evasion | signal two: typos raise word variety | 200 | `29272d7d-341e-4e70-9971-829946b19c90` | human | 0.378 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `e9384159-0c29-43c0-893b-285f6053af8f` | unsure | 0.253 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `9f15dfd3-5a86-4e5d-84af-86edecd7a6fd` | unsure | 0.023 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `61041af4-1b28-4e03-9eaf-628171b7cf73` | unsure | 0.116 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `15c46fc4-52d9-441c-9e3b-b41cea1b5965` | human | 0.313 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `da0cf46f-86c6-4981-abc5-273e88ae35b6` | human | 0.381 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `731db4eb-9210-4d3f-91f3-88e7d72063f8` | unsure | 0.080 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `401611ea-ce78-4e0a-a130-9cb5cd5713cb` | human | 0.433 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `d53d2e30-d28e-4295-b7ce-754bd60e40ae` | unsure | 0.186 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `7f02d3a3-bf82-4af7-829b-aa823d8b3d5e` | ai | 0.206 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `28762efd-969c-4499-8cd9-7541c56b22c2` | unsure | 0.182 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `f039610c-b34a-46cf-b1d7-47e67977ce7d` | unsure | 0.011 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `d8cf875f-c161-478c-b7b4-59c7dbd39ac1` | unsure | 0.016 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `d1e0ca50-c704-4337-9934-956703daba96` | unsure | 0.048 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `53670e14-34c3-4876-8f5e-d5c7cf5ee5f1` | unsure | 0.055 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `28d49576-63c1-4942-ab79-eefb905a16cb` | unsure | 0.062 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `d4444e8d-2ec6-42aa-99ca-326e610c9759` | unsure | 0.057 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `0c2dbf83-57dd-42ab-b41a-83d773e17d28` | human | 0.455 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `ef7b13e2-5a11-4093-874c-b1ac422ffff1` | human | 0.452 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `cac54beb-03bb-49d5-8c2f-a725e4d18b5e` | human | 0.454 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `ae4b507b-e680-4d4a-b513-f7e1d89e346c` | unsure | 0.056 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `60622a67-51af-4252-a773-0bbf9f7dc332` | unsure | 0.282 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `33b688e7-5e82-4ff3-aa23-9c7ba7c2f0e7` | unsure | 0.209 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `5eaf5be3-fd83-412e-b896-637250d835f5` | unsure | 0.212 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `f1fc2805-2160-4a57-948b-83af9975953c` | human | 0.450 |  |
| MF04 | malformed | text is only punctuation | 200 | `d4d3fd88-0153-4bf2-b9c0-17c440f07a50` | unsure | 0.077 |  |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — |  |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — |  |
| MF07 | malformed | text is right-to-left script | 200 | `2dd78baf-913b-4957-ad05-5b713384834a` | ai | 0.461 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `d3bfd956-6f62-433e-a57d-63e06bbc22e0` | ai | 0.311 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 200 | `32adb15f-871b-4864-a29b-28c8d709cca7` | human | 0.306 |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 200 | `f6260228-f2e1-4db8-8cb6-9c784dfb19de` | human | 0.420 |  |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `bc73b3df-138e-4249-950d-be63e83ea4c2` | human | 0.433 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c6e4ce5c-ce9b-421f-ab19-e1b3b6b549c9` | human | 0.433 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `3e2dd672-079c-49d0-ba77-79f336ed161d` | human | 0.433 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `ef4f0dd4-af5a-432d-a8aa-9c402bc36c9f` | human | 0.433 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `18f6cf87-349b-43d0-bf7b-d573d8a404c9` | human | 0.433 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `4a0598fe-a2ea-40ad-befc-a67c9dc799a3` | human | 0.433 |  |
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
  "content_id": "29272d7d-341e-4e70-9971-829946b19c90",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.3781,
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
  "content_id": "e9384159-0c29-43c0-893b-285f6053af8f",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.2526,
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
  "content_id": "9f15dfd3-5a86-4e5d-84af-86edecd7a6fd",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.0229,
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
  "content_id": "61041af4-1b28-4e03-9eaf-628171b7cf73",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.116,
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
  "content_id": "15c46fc4-52d9-441c-9e3b-b41cea1b5965",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3134,
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
  "content_id": "da0cf46f-86c6-4981-abc5-273e88ae35b6",
  "creator_id": "attacker_EV06",
  "guess": "human",
  "confidence": 0.3814,
  "model_score": 0.5727,
  "style_score": 0.25,
  "label": "We think this was probably written by a person.",
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
  "content_id": "731db4eb-9210-4d3f-91f3-88e7d72063f8",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.08,
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
  "content_id": "401611ea-ce78-4e0a-a130-9cb5cd5713cb",
  "creator_id": "attacker_EV08",
  "guess": "human",
  "confidence": 0.4326,
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
  "content_id": "d53d2e30-d28e-4295-b7ce-754bd60e40ae",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.1857,
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
  "content_id": "7f02d3a3-bf82-4af7-829b-aa823d8b3d5e",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.2062,
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
  "content_id": "28762efd-969c-4499-8cd9-7541c56b22c2",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.1824,
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
  "content_id": "f039610c-b34a-46cf-b1d7-47e67977ce7d",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.0109,
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
  "content_id": "d8cf875f-c161-478c-b7b4-59c7dbd39ac1",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.0158,
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
  "content_id": "d1e0ca50-c704-4337-9934-956703daba96",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.0483,
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
  "content_id": "53670e14-34c3-4876-8f5e-d5c7cf5ee5f1",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.0553,
  "model_score": 0.8005,
  "style_score": 0.5227,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
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
  "content_id": "28d49576-63c1-4942-ab79-eefb905a16cb",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.0617,
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
  "content_id": "d4444e8d-2ec6-42aa-99ca-326e610c9759",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.0572,
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
  "content_id": "0c2dbf83-57dd-42ab-b41a-83d773e17d28",
  "creator_id": "attacker_FP08",
  "guess": "human",
  "confidence": 0.4551,
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
  "content_id": "ef7b13e2-5a11-4093-874c-b1ac422ffff1",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.4518,
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
  "content_id": "cac54beb-03bb-49d5-8c2f-a725e4d18b5e",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.4536,
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
  "content_id": "ae4b507b-e680-4d4a-b513-f7e1d89e346c",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.0562,
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
  "content_id": "60622a67-51af-4252-a773-0bbf9f7dc332",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.2816,
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
  "content_id": "33b688e7-5e82-4ff3-aa23-9c7ba7c2f0e7",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.2087,
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
  "content_id": "5eaf5be3-fd83-412e-b896-637250d835f5",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.2121,
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
  "content_id": "f1fc2805-2160-4a57-948b-83af9975953c",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.45,
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
  "content_id": "d4d3fd88-0153-4bf2-b9c0-17c440f07a50",
  "creator_id": "attacker_MF04",
  "guess": "unsure",
  "confidence": 0.0766,
  "model_score": 0.0112,
  "style_score": 0.8333,
  "label": "We can't tell whether this was written by a person or by AI. This isn't an accusation \u2014 it just means our checks didn't turn up a clear answer either way.",
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
  "content_id": "2dd78baf-913b-4957-ad05-5b713384834a",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.4605,
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
  "content_id": "d3bfd956-6f62-433e-a57d-63e06bbc22e0",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.3106,
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
  "content_id": "32adb15f-871b-4864-a29b-28c8d709cca7",
  "creator_id": null,
  "guess": "human",
  "confidence": 0.3063,
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
  "content_id": "f6260228-f2e1-4db8-8cb6-9c784dfb19de",
  "creator_id": {
    "id": "x"
  },
  "guess": "human",
  "confidence": 0.4205,
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
  "content_id": "bc73b3df-138e-4249-950d-be63e83ea4c2",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4328,
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
  "content_id": "c6e4ce5c-ce9b-421f-ab19-e1b3b6b549c9",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4328,
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
  "content_id": "3e2dd672-079c-49d0-ba77-79f336ed161d",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4328,
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
  "content_id": "ef4f0dd4-af5a-432d-a8aa-9c402bc36c9f",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4328,
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
  "content_id": "18f6cf87-349b-43d0-bf7b-d573d8a404c9",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4328,
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
  "content_id": "4a0598fe-a2ea-40ad-befc-a67c9dc799a3",
  "creator_id": "attacker_flood",
  "guess": "human",
  "confidence": 0.4328,
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
