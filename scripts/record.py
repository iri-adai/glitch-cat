#!/usr/bin/env python3
"""Append one package (entities first, then claims) to the Glitch commons.

Usage: python3 scripts/record.py package.json

package.json:
{
  "common": {"said_by": "...", "proxy": null, "recorded_by": "...", "batch": "...",
             "source": "...", "status": "draft|artist_confirmed"},
  "entities": [{"id": "type:slug", "name": "...", "fields": {}, "aliases": []}],
  "claims":   [{"subject": "...", "relation": "...", "object": "...", "event_time": "...",
                "confidence": "low|medium|high", "consent": "full|facts_only|anonymous",
                "quote": "...", "source": "...", "fields": {}}]
}

facts_only claims: the quote and source go to private.jsonl (never committed);
the public claim keeps quote and source as null.
"""
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main(path):
    pkg = json.load(open(path, encoding="utf-8"))
    common = pkg["common"]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    speaker = common["said_by"].split(":", 1)[1]

    entities, claims, private = [], [], []
    for e in pkg.get("entities", []):
        entities.append({
            "id": e["id"], "type": e["id"].split(":", 1)[0], "name": e["name"],
            "fields": e.get("fields", {}), "aliases": e.get("aliases", []),
            "said_by": common["said_by"], "proxy": common.get("proxy"),
            "recorded_by": common["recorded_by"], "batch": common["batch"], "recorded_at": now,
        })
    for c in pkg.get("claims", []):
        cid = f'{c["subject"]}--{c["relation"]}--{c["object"]}--{speaker}'
        consent = c.get("consent", "full")
        quote, source = c.get("quote"), c.get("source", common.get("source"))
        if consent == "facts_only":
            private.append({"claim": cid, "quote": quote, "source": source,
                            "batch": common["batch"], "recorded_at": now})
            quote, source = None, None
        line = {
            "id": cid, "subject": c["subject"], "relation": c["relation"], "object": c["object"],
            "said_by": common["said_by"], "proxy": common.get("proxy"),
            "recorded_by": common["recorded_by"], "source": source, "quote": quote,
            "event_time": c.get("event_time"), "confidence": c.get("confidence", "medium"),
            "consent": consent, "status": c.get("status", common["status"]),
            "batch": common["batch"], "recorded_at": now,
        }
        if c.get("supersedes"):
            line["supersedes"] = c["supersedes"]
        if c.get("fields"):
            line["fields"] = c["fields"]
        claims.append(line)

    for name, rows in (("entities.jsonl", entities), ("claims.jsonl", claims), ("private.jsonl", private)):
        if rows:
            with open(ROOT / name, "a", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(entities)} entities, {len(claims)} claims, {len(private)} private lines appended")


if __name__ == "__main__":
    main(sys.argv[1])
