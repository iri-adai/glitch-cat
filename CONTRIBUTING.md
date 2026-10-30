# Contributing a batch

Each intake session with an artist (or a symbient's proxy) becomes **one pull request**. The pull request is the receipt. Glitch's review happens on it, and merging it is what makes the batch part of the catalog.

## For the person running the session

You run the session in Claude with the `glitch-commons-contributor` skill. The skill handles the steps below; this page is here so you know what it's doing.

1. **Read the catalog first.** The session clones this repo so it can check `entities.jsonl` on `main` before creating anything. That's how two artists who both showed at the same festival end up pointing at one entry instead of two.
2. **Work on a branch.** The branch is named after the batch, `batch/<batch-name>`, for example `batch/glitch-w1-jane-doe-2026-10-31`.
3. **Record only what was approved.** Lines are appended with `scripts/record.py` after each read-back. Nothing is written that the artist hasn't seen.
4. **Check before opening.** `python3 scripts/check.py --base origin/main` must say OK. The same check runs automatically on every pull request.
5. **Open the pull request** with the template filled in from the read-back.

**No push access?** Fork the repo and open the pull request from the fork, or send the batch to a Glitch facilitator who opens it for you.

## For the Glitch curator

Review checks for duplicates, missing sources and consent problems, not the merit of the work.

- Ask questions as comments on the pull request; the artist or facilitator answers there.
- Spotted a likely duplicate of something already on `main`? Don't fix it in the batch. Note it, and add a SAME_AS claim in Glitch's own name after merging.
- When it's ready, run `python3 scripts/review.py <batch> <your name>`, commit that on the batch branch, and merge. The status lines record who reviewed it and when.

## Rules the check enforces

- Existing lines are never changed or removed. Corrections are new claims with `supersedes`.
- One batch per pull request.
- Every claim has a source, unless its words are held privately (facts_only).
- INFLUENCED_BY, RESPONDS_TO, SEED_OF, INSPIRED_BY and MADE_FOR carry the speaker's own words.
- A symbient's claims name the human proxy who carried them.
- SAME_AS is said by Glitch only.
- `private.jsonl` is never committed.

## Private material

Quotes and sources the artist wants withheld (facts_only) go to `private.jsonl`, which git ignores. In this setup they stay with whoever ran the session. **Open decision for Glitch:** whether withheld material should also be held somewhere access-controlled on Glitch's side.
