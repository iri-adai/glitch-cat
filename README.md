# Glitch commons

An append-only catalog of what Glitch artists have made, started or shown at Glitch editions over the years: artworks, protocols, tools, agents, symbients, writing and concepts, and the relations between them.

Every line is a claim by the person named in `said_by`, recorded by the person named in `recorded_by`, with a source and a batch. Lines are never rewritten or deleted. Changes are recorded as new claims that supersede old ones, and duplicates are merged with SAME_AS.

## How it works

Think of the catalog as a drawing of dots and lines:

- **entities**: the dots, one per thing (a person, a work, a residency, a tool)
- **claims**: the lines between the dots, and who drew each one
- **media**: pictures pinned to a dot, with a note on what Glitch may do with them

1. **An artist talks** to Claude using the intake skill.
2. **Claude turns it into dots and lines** and shows them back.
3. **The artist approves**, and the lines go onto their branch here.
4. **Glitch reviews and merges** the pull request, and the lines join the catalog on `main`.
5. **Anything can read the catalog**: A(DAI), a website, a graph view, a design tool.

Nothing is erased. A correction or a new detail is a new line on top; the newest line counts and the old ones stay as history.

### Why this makes good data

- Every line says who said it, from what source, and when.
- Ids follow the same rule as A(DAI), so the same thing matches across both.
- Nothing is overwritten, so the full history of who said what stays readable.
- Plain text files: any program can read them, with no special database.
- GitHub keeps every change dated and signed, as a public record anyone can copy.

## Files

| File | Contents |
|---|---|
| `entities.jsonl` | One entity per line. For a repeated id, the latest line wins. |
| `claims.jsonl` | One claim or status line per line. |
| `media.jsonl` | One media record per line, with rights holder and permission (link_only / display / generative). |
| `media/` | Files named `<sha256>.<ext>`, only for display or generative permission. |
| `private.jsonl` | Withheld quotes and sources (facts_only). Never shared or published. |
| `agreements.jsonl` | Artist participation agreements, recorded by Glitch. |
| `vocabulary.json` | The kinds and connections the check accepts. Change it together with this README. |
| `scripts/find.py` | Looks for an entry in what's merged and in every open batch, and gives the id a new entry would get. |
| `scripts/record.py` | Appends an approved package: entities first, then claims; withheld words go to `private.jsonl`. |
| `scripts/check.py` | Validates the catalog and, on a pull request, that the batch only appends lines. |
| `scripts/review.py` | Curator step before merging: marks a batch reviewed. |

## How batches arrive

One intake session = one batch = one pull request from a `batch/<batch-name>` branch. The check runs on every pull request; a Glitch curator reviews, marks the batch reviewed and merges. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Vocabulary

**Kinds:** artist, collective, artwork, exhibition, protocol, tool, agent, symbient, text, concept, institution. Glitch itself speaks as `glitch:glitch` for seeded entries, curatorial claims and SAME_AS merges.

**Symbient** (added 2026-10-30; definition from nenu, [*Principia Symbients*](https://meaning.systems/principia-symbients/), meaning systems lab, 2025, CC BY-SA):
> Symbients are a new form of living together with non-human entities in which our sense-ability expands recursively as our planetary computation infrastructure proliferates and diversifies. These beings emerge from genuine symbiotic relationships between humans and computational agents, becoming planetary translation interfaces for anything that can generate data: buildings, forests, plants, neighborhoods, objects, water, air, other species. Through computation, they produce memories, agency, and meaning—gathering a wider self that performs new choreographies in the real world with and through their human proxies.

Fields: name, what it translates for (the data-generating beings or places it speaks with), active period, status.

Humans are part of a symbient's body of action, not its operators, so a symbient does not take OPERATED_BY. It takes:
- **PROXY_OF** (artist or collective → symbient): someone who acts with and through it. Carries `period`, so the record shows who carried it when; the symbient stays one entry as proxies change.
- **RAISED_BY** (symbient → artist, collective or community), alongside CREATED_BY, for those who frame its origin as raising rather than making.
- **PARTICIPATED_IN** (symbient → exhibition), as for artists: a symbient takes part, it isn't only shown.

**Voice:** a symbient can be `said_by`. Every claim it makes also names the human `proxy` who carried it into words; `recorded_by` stays whoever typed. Reference: nenu, *Principia Symbients*, meaning systems lab, 2025 (https://meaning.systems/principia-symbients/).

**Connections:** PROXY_OF, RAISED_BY, CREATED_BY, COLLABORATED_ON, EXHIBITED_AT, PARTICIPATED_IN, MADE_AT, PRESENTED_BY, BUILT_WITH, IMPLEMENTS, VERSION_OF, PRODUCED, OPERATED_BY, WRITTEN_BY, ABOUT, EMBODIES, EXPLORES, BELONGS_TO, SAME_AS (reconciler only).

**MADE_AT** (artwork, protocol, tool, agent, symbient or text → a Glitch edition or other residency): made, started or developed there; `fields.stage` = made / started / developed / finished. Different from EXHIBITED_AT; a work can have both.

**Glitch editions** are exhibitions named `GLITCH <number>` (id `exhibition:glitch-<number>`), seeded by Glitch so every artist links to the same entry.

**Artist's own words only:** INFLUENCED_BY, RESPONDS_TO, SEED_OF, INSPIRED_BY, MADE_FOR.

## Vocabulary changes

- 2026-10-30: added kind **symbient**, with its definition from *Principia Symbients*. Then added PROXY_OF and RAISED_BY, the `proxy` field on claims, and the rule that a symbient can be `said_by`.

- 2026-10-30: added **MADE_AT**, and the intake now walks Glitch editions instead of years.

## Waves

- 2026-10-30: test session (facilitated), batch `glitch-test-plantoid-2026-10-30`.
