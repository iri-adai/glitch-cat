"""Shared helpers: one id rule, and one view of what already exists.

"What exists" means three places:
  main     what has been merged (origin/main if fetched, else local main)
  open     entries in other people's open batch branches (origin/batch/*)
  here     entries already written on the current branch
"""
import difflib
import json
import pathlib
import re
import subprocess
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent.parent
FUZZY = 0.88


def slug(text):
    """Same rule as A(DAI): lowercase, accents transliterated, parens/dots/apostrophes
    stripped, & -> and, any other punctuation or space -> one hyphen."""
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    t = t.replace("&", " and ")
    t = re.sub(r"[().'’`]", "", t)
    t = re.sub(r"[^a-z0-9]+", "-", t)
    return t.strip("-")


def make_id(kind, name, year=None):
    """<kind>:<slug(name)>, with -<year> for recurring things such as yearly exhibitions."""
    s = slug(name)
    if year and not s.endswith(f"-{year}"):
        s = f"{s}-{year}"
    return f"{kind}:{s}"


def id_follows_rule(entity):
    kind, _, s = entity["id"].partition(":")
    base = slug(entity.get("name", ""))
    return s == base or re.fullmatch(re.escape(base) + r"-\d{4}", s) is not None


def keys(entity):
    """Normalised names an entity can be found by: its name, aliases, and id slug."""
    out = {slug(entity.get("name", "")), entity["id"].partition(":")[2]}
    out |= {slug(a) for a in entity.get("aliases", []) if isinstance(a, str)}
    return {k for k in out if k}


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def parse(text):
    rows = []
    for raw in text.splitlines():
        if raw.strip():
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError:
                pass
    return rows


def latest(rows):
    """Latest line wins for a repeated id."""
    out = {}
    for r in rows:
        if "id" in r:
            out[r["id"]] = r
    return out


def at_ref(ref, name="entities.jsonl"):
    r = git("show", f"{ref}:{name}")
    return parse(r.stdout) if r.returncode == 0 else []


def main_ref():
    return "origin/main" if git("rev-parse", "--verify", "-q", "origin/main").returncode == 0 else "main"


def current_branch():
    return git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def known(fetch=False):
    """Every known entity, tagged with where it was found."""
    if fetch:
        git("fetch", "-q", "origin")
    seen = []
    for e in latest(at_ref(main_ref())).values():
        seen.append((e, "main"))
    main_ids = {e["id"] for e, _ in seen}
    me = current_branch()
    refs = git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/batch/").stdout.split()
    for ref in refs:
        if ref.endswith("/" + me) or ref == f"origin/{me}":
            continue
        for e in latest(at_ref(ref)).values():
            if e["id"] not in main_ids:
                seen.append((e, f"open batch {e.get('batch', ref)}"))
    path = ROOT / "entities.jsonl"
    if path.exists():
        for e in latest(parse(path.read_text(encoding="utf-8"))).values():
            if e["id"] not in main_ids:
                seen.append((e, "this branch"))
    return seen


def matches(name, kind=None, aliases=(), pool=None):
    """Exact matches on any normalised key, then near matches of the same kind."""
    pool = known() if pool is None else pool
    wanted = {slug(name)} | {slug(a) for a in aliases}
    exact, near, seen = [], [], set()
    for e, where in pool:
        if (kind and e.get("type") != kind) or e["id"] in seen:
            continue
        seen.add(e["id"])
        ks = keys(e)
        if wanted & ks:
            exact.append((e, where))
        elif any(difflib.SequenceMatcher(None, w, k).ratio() >= FUZZY for w in wanted for k in ks):
            near.append((e, where))
    return exact, near
