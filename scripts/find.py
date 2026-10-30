#!/usr/bin/env python3
"""Look before you create: search merged entries and everyone's open batches.

Usage:
  python3 scripts/find.py "Feral File"
  python3 scripts/find.py "HEK" --type institution
  python3 scripts/find.py --id institution "Transmediale" --year 2023   # the id a new entry would get

Fetches origin first so open batches pushed by other sessions are included.
"""
import argparse
import json

from catalog import known, make_id, matches


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--type")
    ap.add_argument("--alias", action="append", default=[])
    ap.add_argument("--id", metavar="KIND", help="print the id a new entry of this kind would get")
    ap.add_argument("--year")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-fetch", action="store_true")
    a = ap.parse_args()

    if a.id:
        print(make_id(a.id, a.name, a.year))
        return
    pool = known(fetch=not a.no_fetch)
    exact, near = matches(a.name, a.type, a.alias, pool)
    if a.json:
        print(json.dumps({"exact": [dict(e, found_in=w) for e, w in exact],
                          "near": [dict(e, found_in=w) for e, w in near]}, ensure_ascii=False))
        return
    if not exact and not near:
        print(f"Nothing like {a.name!r} yet. A new entry is fine.")
        return
    for label, rows in (("Same thing", exact), ("Possibly the same", near)):
        for e, where in rows:
            aka = f" (also: {', '.join(e['aliases'])})" if e.get("aliases") else ""
            print(f"{label}: {e['name']}{aka} -> {e['id']}  [{where}]")


if __name__ == "__main__":
    main()
