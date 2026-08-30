# Trace — one submission, start to finish

1. **Writer submits text.** A POST to `/submit` with `text` and `creator_id`. This is the only way in.

2. **The route checks the input.** Is `text` there, not empty, not absurdly long? Bad input gets rejected here, before either signal runs, and the rejection gets logged too.

3. **Signal one reads the text for meaning.** `detector.py` runs a small local language model over the text and asks how predictable it is (perplexity). Predictable text scores closer to "AI"; surprising text scores closer to "human". Adds: a machine judgment based on word-choice patterns.

4. **Signal two reads the text as shape.** `stylometry.py` looks at sentence length spread, vocabulary repetition, and punctuation density — no understanding of meaning at all. Adds: a structural judgment independent of what the words mean.

5. **The two signals get combined.** `scoring.py::combine_signals` takes both 0–1 scores and produces one combined score. This is where a decision gets made about what to do when the two signals disagree.

6. **The combined score becomes a label.** `scoring.py::score_to_label` turns the number into one of three fixed, plain-English labels a reader can actually understand, using the thresholds in `config.py`.

7. **The decision is logged and returned.** `audit.py` writes the whole decision (both signal scores, the combined score, the label) to the audit log, and the same information comes back to the caller as JSON. If the writer disagrees, `/appeal` is how they push back — it doesn't re-score anything, it just marks the item `under_review` and records why.
