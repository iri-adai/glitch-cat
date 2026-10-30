#!/usr/bin/env python3
"""Check the Glitch commons before a batch is merged.

Usage:
  python3 scripts/check.py                 # check the whole catalog
  python3 scripts/check.py --base main     # also check what this branch adds against main

Exits non-zero and lists problems in plain words if anything is wrong.
"""
import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOCAB = json.load(open(ROOT / "vocabulary.json", encoding="utf-8"))
FILES = ["entities.jsonl", "claims.jsonl", "media.jsonl", "agreements.jsonl"]
problems = []


def problem(msg):
    problems.append(msg)


def load(name):
    rows = []
    path = ROOT / name
    if not path.exists():
        return rows
    for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            rows.append(json.loads(raw))
        except json.JSONDecodeError as e:
            problem(f"{name} line {n} is not valid JSON ({e.msg})")
    return rows


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def check_catalog():
    entities = load("entities.jsonl")
    claims = load("claims.jsonl")
    ids = {e.get("id") for e in entities}
    claim_ids = set()

    for e in entities:
        eid = e.get("id", "")
        kind = eid.split(":", 1)[0] if ":" in eid else None
        if kind not in VOCAB["kinds"]:
            problem(f"entity {eid!r}: unknown kind {kind!r}")
        if e.get("type") != kind:
            problem(f"entity {eid!r}: type {e.get('type')!r} does not match its id")
        for f in ("name", "said_by", "recorded_by", "batch"):
            if not e.get(f):
                problem(f"entity {eid!r}: missing {f}")

    for c in claims:
        if "claim" in c and "status" in c:  # a status line confirming or reviewing a claim
            if c["status"] not in VOCAB["status"]:
                problem(f"status line for {c['claim']!r}: unknown status {c['status']!r}")
            if c["claim"] not in claim_ids:
                problem(f"status line points to a claim that isn't recorded: {c['claim']!r}")
            continue
        cid = c.get("id", "?")
        claim_ids.add(cid)
        rel = c.get("relation")
        if rel not in VOCAB["relations"]:
            problem(f"claim {cid}: unknown connection {rel!r}")
        for f in ("subject", "object", "said_by"):
            if c.get(f) not in ids:
                problem(f"claim {cid}: {f} {c.get(f)!r} has no entry in entities.jsonl")
        if c.get("proxy") and c["proxy"] not in ids:
            problem(f"claim {cid}: proxy {c['proxy']!r} has no entry")
        if c.get("said_by", "").startswith("symbient:") and not c.get("proxy"):
            problem(f"claim {cid}: a symbient's claim must name its human proxy")
        for f, allowed in (("consent", "consent"), ("status", "status"), ("confidence", "confidence")):
            if c.get(f) not in VOCAB[allowed]:
                problem(f"claim {cid}: {f} {c.get(f)!r} is not one of {VOCAB[allowed]}")
        if not c.get("recorded_by") or not c.get("batch"):
            problem(f"claim {cid}: missing recorded_by or batch")
        if c.get("consent") == "facts_only" and (c.get("quote") or c.get("source")):
            problem(f"claim {cid}: facts_only but quote/source are public; move them to private.jsonl")
        if c.get("consent") != "facts_only" and not c.get("source"):
            problem(f"claim {cid}: no source")
        if rel in VOCAB["own_words_only"] and c.get("consent") != "facts_only" and not c.get("quote"):
            problem(f"claim {cid}: {rel} needs the speaker's own words in quote")
        if rel in VOCAB["reconciler_only"] and c.get("said_by") != VOCAB["glitch_speaker"]:
            problem(f"claim {cid}: SAME_AS can only be said by Glitch (the reconciler)")
        if c.get("supersedes") and c["supersedes"] not in claim_ids:
            problem(f"claim {cid}: supersedes a claim that isn't recorded earlier: {c['supersedes']!r}")

    tracked = git("ls-files", "private.jsonl").stdout.strip()
    if tracked:
        problem("private.jsonl is tracked by git; it must never be committed")
    return entities, claims


def check_branch(base):
    """What this branch adds must be appended lines only, all from one batch."""
    batches = set()
    for name in FILES:
        old = git("show", f"{base}:{name}")
        old_text = old.stdout if old.returncode == 0 else ""
        new_text = (ROOT / name).read_text(encoding="utf-8") if (ROOT / name).exists() else ""
        if not new_text.startswith(old_text):
            problem(f"{name}: existing lines were changed or removed; the commons is append-only")
            continue
        for raw in new_text[len(old_text):].splitlines():
            if raw.strip():
                try:
                    row = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if row.get("batch"):
                    batches.add(row["batch"])
    if len(batches) > 1:
        problem(f"this branch adds more than one batch ({', '.join(sorted(batches))}); one batch per pull request")
    return batches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref to compare against, e.g. origin/main")
    args = ap.parse_args()
    entities, claims = check_catalog()
    batches = check_branch(args.base) if args.base else set()
    if problems:
        print(f"{len(problems)} problem(s):")
        for p in problems:
            print(" -", p)
        sys.exit(1)
    msg = f"OK: {len(entities)} entities, {len(claims)} claim lines"
    if batches:
        msg += f"; adds batch {next(iter(batches))}"
    print(msg)


if __name__ == "__main__":
    main()
