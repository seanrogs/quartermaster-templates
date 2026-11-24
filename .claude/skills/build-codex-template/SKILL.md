---
name: build-codex-template
description: Build a new Warhammer 40,000 faction .qmtemplate (e.g. in WH40K3/) from a Codex PDF or page scans — army list entries, armoury, vehicle upgrades and special characters — by writing a Python data script on top of the shared qmtemplate.py builder. Use whenever the user shares a Codex/army book and asks for a new faction template, or wants to rebuild or change one that was generated this way.
---

# Build codex template

Faction templates are generated, not hand-edited: each one has a data script in `factions/` that describes the army with the builders in `qmtemplate.py` and writes the whole `.qmtemplate` in one go. To change a generated template, edit its script and re-run it.

- `qmtemplate.py` — builders (`opt`, `unit`, `fixed`, `standard`, `toggle`, `armoury`, `items`, `standard_foc`, `unit_limit`, `trait`, `template`, `write`) and an outline viewer.
- `factions/wh40k3_dark_eldar.py`, `factions/wh40k3_tau.py` — worked examples. Copy the closer one as the starting point for the next codex.

Output format: `write()` produces exactly what Quartermaster 6.7 saves — sorted keys, whole-number reals bare (`<real>20</real>`, `<real>0</real>`), fractions as-is (`<real>-0.34</real>`), Prerequisite as an array even with one condition. The Dark Eldar script rebuilds the app-saved `WH40K3/Dark Eldar.qmtemplate` byte-for-byte; keep it that way, so after the user re-saves a template in the app, regenerating shows only real differences. When the user has edited a generated template in the app, diff it against the script's output and fold their changes back into the script.

## 1. Read the source and the neighbours

1. Read the codex PDF a few pages at a time. For small print (armoury prices, vehicle upgrade lists), render the page larger and crop it: `pdftoppm -r 200 -f N -l N -png file.pdf out` then `sips -c H W --cropOffset Y X`. Cross-check prices that appear twice (unit entry vs. armoury summary).
2. Outline the closest existing templates in the same system folder for patterns: `python3 .claude/skills/build-codex-template/qmtemplate.py outline "WH40K3/Eldar.qmtemplate"`. Space Marines and Chaos Space Marines show armouries; Imperial Guard shows additional sergeants.
3. Ask the user about anything structural before writing — typically: how to handle army variants (separate file like the Eldar craftworlds, or one file with Prerequisite tags), and whether to include special characters.

## 2. Map codex entries to template patterns

| Codex says | Template pattern |
|---|---|
| Army variant (Chapter, Clan, Wych Cult…) | `traits=[trait('Sub-faction', ['Wych Cult'])]` on `template()`; units that only exist in, or are banned from, the variant get `prereq='Wych Cult'` / `prereq='not Wych Cult'` (a unit allowed in different slots is duplicated into each slot). Variants may carry colours: `('Goffs', '#141414', '#F25A50')` |
| "Only one of X or Y" across units (e.g. one Archon *or* Archite, special characters that count as one) | `hq_limits=[unit_limit('Archon or Wych Archite', [...names...])]` on `standard_foc()`, plus `upper=1` on each unit |
| "Army of at least 1,500 points" | `from_points=1500` |
| "Army must include X" / "army led by X" | `requires=['X', ...]` (one of the named units); keep a short `prereq` note for wording the link can't express |
| 0-1 unit | `upper=1` only — no "0-1" note needed |
| Standard weapons the whole squad carries | `standard('splinter rifles')` (Default + Equipped) |
| A per-model default option (every model has a splinter rifle) | `opt(..., count=<minimum unit size>, maximum=-1, default=True)` — Count is the number of models carrying it, not 1 |
| "Up to two models may take X or Y" | one group `[opt('X', pts, maximum=2), opt('Y', pts)]` |
| One per model / two per model | `maximum=-1` / `maximum=-2`; one per three models is `-0.34` |
| "All models may have X at +N pts per model" | `toggle('X', N)` |
| Upgrade one model to a character at +N | `command=[[opt('Sergeant', N, maximum=1, stats=..., options=..., magic_items=...)]]` |
| A character model added on top of the squad | `opt(..., count=1, default=True, additional=True)` |
| Mixed-model unit (e.g. Warriors and/or Incubi) | one Command group: base model `count=size, maximum=-1, default=True`, other model types at their extra cost; 0-1 types noted in `prereq` |
| Character weapon choices ("two single-handed, or one single + one two-handed") | an Equipment group with `maximum=2` for single-handed and a group with `maximum=1` for two-handed |
| "May take wargear from the Armoury, up to 100 pts" | `magic_items=armoury('Wargear, Arcane Wargear', 100)` plus `items(...)` categories at template level |
| Slots shared by weapons and systems (Tau battlesuit hard points) | one group per model, `maximum=-3` on a team (`3` on a single model); options using two slots carry `prereq='uses two hard points'` |
| Unit that takes a slot but joins another unit (Kroot Hounds, Krootox) | its own entry in its slot with `requires=['Kroot Carnivore Squad']` and an "attached to…" note |
| Flat upgrade for the whole unit (+10 pts per team, not per model) | `[opt('bonded', 10, maximum=1)]` |
| Armoury item a model can take more than once (drones) | 5th tuple element `True` in `items()` entries (writes `Multiple`) |
| Dedicated transport | attach it: `attached=[raider()]`; compulsory transport adds `lower=1` |
| Special character | `upper=1`, all wargear as `fixed(...)` at 0 pts, army restrictions in `prereq` |
| Vehicle | stats `FA10•SA10•RA10•BS4`; walkers/vehicle-like characters mix in `WS•BS•S•…•I•A` |
| Restrictions the app can't enforce ("one per army", "Haemonculi only", "10 models or fewer") | `prereq='…'` free-text note; separate conditions go in a list, `prereq=['Army led by an Archon', 'not Wych Cult']` |

Stat strings use `•` between characteristics; keep codex oddities as written (`A2(4)`, `T3(4)`, `AD6`, `Sv-` for no save). Equipment and armoury item names are lowercase common nouns (`plasma grenades`, `shadow field`); named artefacts and special rules keep their capitals (`Crucible of Malediction`, `Animus Vitae`). Army-wide special rules (e.g. Fleet of Foot) are not repeated on every unit.

## 3. Build, check, publish

1. Write `factions/<system>_<faction>.py` (lowercase, underscores) and run it: `python3 -B .claude/skills/build-codex-template/factions/<script>.py "WH40K3/<Faction>.qmtemplate"`. Set the `Version` to today's date as `YYYYMMDD`.
2. Validate: `plutil -lint` the file, outline it and read it through, and check it only uses keys the other templates in the folder use.
3. Add a link in the system's index page (e.g. `WH40K.html`, under the `WH40K3` heading). Check whether `catalogue.json` covers that system before touching it — WH40K3 isn't in it.
4. Commit the template, the index link and the faction script together.
