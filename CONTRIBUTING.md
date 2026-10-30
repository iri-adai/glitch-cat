# Contributing a batch

Each intake session with an artist (or a symbient's proxy) becomes **one pull request**. The pull request is the receipt. Glitch's review happens on it, and merging it is what makes the batch part of the catalog.

## For the person running the session

You run the session in Claude with the `glitch-commons-contributor` skill. The skill handles the steps below; this page is here so you know what it's doing.

1. **Work on a branch.** The branch is named after the batch, `batch/<batch-name>`, for example `batch/glitch-w1-jane-doe-2026-10-31`.
2. **Look before creating.** `python3 scripts/find.py "Feral File"` searches what's merged and every other session's open batch, so two artists recording at the same time end up pointing at one entry instead of two.
3. **Record only what was approved.** Lines are appended with `scripts/record.py` after each read-back. Nothing is written that the artist hasn't seen. It refuses to create something that looks like an existing entry under a different name, so the session can ask the artist.
4. **Push early.** After the first list is approved, the session pushes the branch and opens a draft pull request, so parallel sessions can see its new entries. It pushes again after each later step.
5. **Check, then mark ready.** `python3 scripts/check.py --base origin/main` must say OK. The same check runs on every pull request. Once the artist approves the read-back, the draft is marked ready for review.

**No push access?** Fork the repo and open the pull request from the fork, or send the batch to a Glitch facilitator who opens it for you.

## For the Glitch curator

Review checks for duplicates, missing sources and consent problems, not the merit of the work.

- Ask questions as comments on the pull request; the artist or facilitator answers there.
- Spotted a likely duplicate of something already on `main`? Don't fix it in the batch. Note it, and add a SAME_AS claim in Glitch's own name after merging.
- When it's ready, run `python3 scripts/review.py <batch> <your name>`, commit that on the batch branch, and merge. The status lines record who reviewed it and when.

## How ids work

Every entry's id comes from its name by one rule, the same one A(DAI) uses: lowercase, accents dropped, brackets, dots and apostrophes removed, `&` becomes `and`, everything else becomes a hyphen. Recurring events add the year. So "Feral File" is always `institution:feral-file` and "Transmediale 2023" is `exhibition:transmediale-2023`, whoever records it. Different names for the same thing ("HEK" and "Haus der Elektronischen Künste") are caught through aliases, so record the other names as aliases.

## When two batches touch the same thing

If two open batches both create the same entry, the second one to record it marks its line `also_proposed_in`, and either can merge first. Both append to the same files, so GitHub may report a conflict on the second pull request. Rebase it locally (`git fetch && git rebase origin/main`); `.gitattributes` tells git to keep both sides' lines, so it resolves on its own.

## Rules the check enforces

- Ids follow the naming rule.
- A batch doesn't recreate an entry that's already on `main`, or add one whose name or alias matches an existing entry; near matches are flagged for the reviewer.
- Existing lines are never changed or removed. Corrections are new claims with `supersedes`.
- One batch per pull request.
- Every claim has a source, unless its words are held privately (facts_only).
- INFLUENCED_BY, RESPONDS_TO, SEED_OF, INSPIRED_BY and MADE_FOR carry the speaker's own words.
- A symbient's claims name the human proxy who carried them.
- SAME_AS is said by Glitch only.
- `private.jsonl` is never committed.

## Private material

Quotes and sources the artist wants withheld (facts_only) go to `private.jsonl`, which git ignores. In this setup they stay with whoever ran the session. **Open decision for Glitch:** whether withheld material should also be held somewhere access-controlled on Glitch's side.
