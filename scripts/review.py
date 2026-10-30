#!/usr/bin/env python3
"""Curator step: mark every claim in a batch as reviewed, just before merging its pull request.

Usage: python3 scripts/review.py <batch> <curator name>

Appends one status line per claim; nothing is edited.
"""
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main(batch, curator):
    path = ROOT / "claims.jsonl"
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    targets = [r["id"] for r in rows if r.get("batch") == batch and "id" in r]
    if not targets:
        sys.exit(f"No claims found for batch {batch!r}")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    with open(path, "a", encoding="utf-8") as f:
        for cid in targets:
            f.write(json.dumps({"claim": cid, "status": "reviewed", "by": curator, "at": now},
                               ensure_ascii=False) + "\n")
    print(f"{len(targets)} claims in {batch} marked reviewed by {curator}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
