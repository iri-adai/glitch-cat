#!/usr/bin/env python3
"""Append one approved package (entities first, then claims) to the Glitch commons.

Usage: python3 scripts/record.py package.json [--no-fetch]

package.json:
{
  "common": {"said_by": "...", "proxy": null, "recorded_by": "...", "batch": "...",
             "source": "...", "status": "draft|artist_confirmed"},
  "entities": [{"type": "institution", "name": "...", "year": null, "aliases": [], "fields": {},
                "consent": "full|facts_only",
                "id": "optional, computed from type + name (+ year) if left out",
                "update": false, "new_confirmed": false}],
  "claims":   [{"subject": "...", "relation": "...", "object": "...", "event_time": "...",
                "confidence": "low|medium|high", "consent": "full|facts_only|anonymous",
                "quote": "...", "source": "...", "supersedes": null, "fields": {}}]
}

Before writing anything it checks every new entity against what is merged and what other
sessions have pushed in open batches:
  - same id already merged: not written again (the claims simply point at it)
  - same id only in someone's open batch: written, marked also_proposed_in, so either batch can merge first
  - same name or alias under a different id: stops, so the session can ask the artist
  - a near match: stops unless the entity says "new_confirmed": true (the artist said it's different)
facts_only claims: quote and source go to private.jsonl (never committed).
"""
import datetime
import json
import sys

from catalog import ROOT, id_follows_rule, known, make_id, matches

# Fields that hold the speaker's own words (field cards, skill D2). On a facts_only entity
# they go to private.jsonl; the public line keeps only the structural fields.
WORD_FIELDS = {"description", "concept", "process", "statement", "notes", "what_it_does",
               "how_it_works", "translates_for", "summary", "practice"}


def stop(lines):
    print("Nothing recorded. Check these with the artist first:")
    for l in lines:
        print(" -", l)
    sys.exit(1)


def main(path, fetch=True):
    pkg = json.load(open(path, encoding="utf-8"))
    common = pkg["common"]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    speaker = common["said_by"].split(":", 1)[1]
    pool = known(fetch=fetch)
    issues, entities, notes, private = [], [], [], []

    for e in pkg.get("entities", []):
        kind = e.get("type") or e["id"].split(":", 1)[0]
        eid = e.get("id") or make_id(kind, e["name"], e.get("year"))
        fields = dict(e.get("fields", {}))
        consent = e.get("consent", "full")
        if consent == "facts_only":
            held = {k: fields.pop(k) for k in list(fields) if k in WORD_FIELDS}
            if held:
                private.append({"entity": eid, "fields": held,
                                "batch": common["batch"], "recorded_at": now})
        line = {"id": eid, "type": kind, "name": e["name"], "fields": fields,
                "aliases": e.get("aliases", []), "consent": consent, "said_by": common["said_by"],
                "proxy": common.get("proxy"), "recorded_by": common["recorded_by"],
                "batch": common["batch"], "recorded_at": now}
        if e.get("update"):
            if not any(x["id"] == eid for x, _ in pool):
                issues.append(f"{eid}: marked as an update, but there is no such entry")
            line["update"] = True
            entities.append(line)
            continue
        if not id_follows_rule(line):
            issues.append(f"{eid}: id doesn't follow the naming rule for {e['name']!r} "
                          f"(expected {make_id(kind, e['name'], e.get('year'))})")
        exact, near = matches(e["name"], kind, e.get("aliases", []), pool)
        same = [(x, w) for x, w in exact if x["id"] == eid]
        other = [(x, w) for x, w in exact if x["id"] != eid]
        for x, w in other:
            issues.append(f"{e['name']!r} looks like {x['name']!r} ({x['id']}, {w}); use that id if it's the same")
        if same:
            where = same[0][1]
            if where.startswith("open batch"):
                line["also_proposed_in"] = where.removeprefix("open batch ")
                entities.append(line)
                notes.append(f"{eid} is also in {where}; recorded here too, so either can merge first")
            else:
                notes.append(f"{eid} already exists ({where}); linking to it")
            continue
        if not e.get("new_confirmed"):
            for x, w in matches(e["name"], None, e.get("aliases", []), pool)[0]:
                if x.get("type") != kind:
                    issues.append(f"{e['name']!r} has the same name as {x['name']!r}, recorded as a {x['type']} "
                                  f"({x['id']}, {w}); if it's the same thing, use that id")
        if near and not e.get("new_confirmed"):
            for x, w in near:
                issues.append(f"{e['name']!r} is close to {x['name']!r} ({x['id']}, {w}); "
                              f"if the artist says they're different, add \"new_confirmed\": true")
        entities.append(line)

    if issues:
        stop(issues)

    claims = []
    for c in pkg.get("claims", []):
        cid = f'{c["subject"]}--{c["relation"]}--{c["object"]}--{speaker}'
        consent = c.get("consent", "full")
        quote, source = c.get("quote"), c.get("source", common.get("source"))
        if consent == "facts_only":
            private.append({"claim": cid, "quote": quote, "source": source,
                            "batch": common["batch"], "recorded_at": now})
            quote, source = None, None
        line = {"id": cid, "subject": c["subject"], "relation": c["relation"], "object": c["object"],
                "said_by": common["said_by"], "proxy": common.get("proxy"),
                "recorded_by": common["recorded_by"], "source": source, "quote": quote,
                "event_time": c.get("event_time"), "confidence": c.get("confidence", "medium"),
                "consent": consent, "status": c.get("status", common["status"]),
                "batch": common["batch"], "recorded_at": now}
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
    for n in notes:
        print("note:", n)
    print(f"{len(entities)} entities, {len(claims)} claims, {len(private)} private lines appended")


if __name__ == "__main__":
    main(sys.argv[1], fetch="--no-fetch" not in sys.argv)
