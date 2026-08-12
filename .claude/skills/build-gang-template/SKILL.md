---
name: build-gang-template
description: Build or extend an N26 gang .qmtemplate file (in N26/) from Necromunda-style rulebook screenshots — fighter stat-card pages, equipment price lists, equipment stat-reference pages, and skill-access tables — following the conventions established for House Cawdor and House Delaque. Use whenever the user shares gang-book screenshots for a house in N26/, or asks to set up a new gang file the same way.
---

# Build gang template

Populates an N26 `.qmtemplate` file (fighters, equipment catalogue, skills) from photographed rulebook pages, and keeps `N26/REVIEW_NOTES.md` updated with every judgment call made along the way. This is a multi-turn process — screenshots typically arrive one page/table at a time across a conversation, not all at once.

All edits are done as targeted text/line insertions into the plist XML, never a full `plistlib` rewrite of the whole file — `plistlib.dump` reformats every existing `<real>` (e.g. `20` → `20.0`) and produces a huge spurious diff. Only use `plistlib.load` (read-only) for lookups and for validating a file after editing it.

## 0. Setting up a new gang file

1. Find the original, pre-work skeleton of an existing gang file in git history (e.g. `git log --follow -- "N26/House Cawdor.qmtemplate"`, take the earliest commit) and pull it: `git show <sha>:"N26/House Cawdor.qmtemplate" > "N26/House <NewGang>.qmtemplate"`.
2. If that skeleton contains an example fighter (a hand-authored template fighter left in by the user), strip it out so the new file starts with genuinely empty `Units` arrays for every Organisation class — don't carry another gang's named fighter into the new file. Convert its parent `<array>...</array>` to a self-closed `<array/>`, and delete the whole unit `<dict>...</dict>` between them (watch for an off-by-one: the deletion range is `[array_open+1 : dict_close+1]` inclusive of the unit's own closing `</dict>`, and don't forget to remove the now-orphaned `</array>` that closed the original array — validate with `plistlib.load` immediately after and fix indentation-only mismatches if the parser complains about a mismatched tag).
3. Rename `<key>Army List Name</key>`'s `<string>` to the new gang's name.
4. Validate with `plistlib.load` before moving on. Log the "did I keep or strip the example fighter" decision (and why) as the first entry for this gang in `N26/REVIEW_NOTES.md`.

## 1. Recognizing what a screenshot is

- **Fighter stat card** (name banner, credit cost, M/WS/BS/S/T/W/I/A/Sv and Ld/Cl/Wil/Int rows, a "Type" cell, "Starting XP") → §2.
- **Equipment price list** (section headers like RANGED WEAPONS / CLOSE COMBAT WEAPONS / WARGEAR, item name + "... N credits", sometimes a faction-restriction parenthetical) → §3.
- **Equipment stat reference** (SR/LR/Str/AP/L/Traits columns plus Creds/TP, grouped under the same section headers) → §3, paired with the price list.
- **Skill access table** (fighter names down the left, Agility/Brawn/Combat/Cunning/Savant/Shooting/etc. across the top, cells are Primary/Secondary/–) → §4.

## 2. Fighter roster

Capture only: **Name, Points (credits), Stats (the M/WS/.../Sv•Ld/Cl/Wil/Int line joined with `•`, same bullet format as `N26.qmsystem`), Special Rules (the literal "Type" cell text, e.g. `Fighter (Champion, Pious)`), XP (Starting XP)**. Do not transcribe ability/rule prose (Wyrd power grants, deployment special rules, skill grants, starting-equipment loadouts, pet leash/sensor rules, equip-only-X-weapon restrictions) — flag each skipped item briefly in the review notes rather than modeling it.

**Role mapping** from the Type string: contains "Leader" → Leader; "Champion" → Champion; "Brute" → Brute; anything else (Ganger, Prospect, Beast, Pet, etc.) → Fighter, the default bucket.

**Building the unit block:**
1. Locate an already-built fighter in this same file (or, for the very first fighter, hand-author one) to use as the boilerplate template — it carries the full `Command` → `Advancements`/`Lasting Injuries`/equipment-category `Magic Items` tree that every fighter shares verbatim. Extract it as raw lines: from the unit's opening `<dict>` through the last shared line before the fighter-specific tail (`Maximum Size`/`Minimum Size`/`Name`/`Points`/`Size`/`Special Rules`/`Stats`/`Upper Limit`/`XP`, alphabetical key order, ending `</dict>`).
2. **Attached Units**: if this gang has a universal auto-included companion (Cawdor's Sheen Bird), keep the `<key>Attached Units</key>` block in the template unmodified for every fighter. If not (Delaque's pets are standalone roster fighters instead, not attachments), the template must start directly at `<key>Command</key>` — exclude the `Attached Units` key/array entirely when extracting the template. Get this right per-gang; check whether the source book shows pets as their own priced fighter-card entries (→ standalone roster fighter, no attachment) or only as an equipment-list line + reference stats with no card of their own (→ attachment, add it once and reuse for every fighter).
3. Generate the tail per fighter (5-tab-indented keys under a 4-tab `<dict>`/`</dict>`, matching the template's own indentation) and append to the template lines.
4. Insert into the matching Organisation class's `Units` array (find the `<string>ClassName</string>` under `Organisation`, then its `<key>Units</key>`, then the array — convert `<array/>` to `<array>...</array>` if this is the first unit in that class, otherwise insert before the existing `</array>`).
5. Validate the whole file with `plistlib.load` after each batch, and spot check a couple of fighters' full structure (`Attached Units` present/absent as intended, tail fields correct).

## 3. Equipment list + reference

Target is the gang's own `Items` array (9 categories: Ranged Weapons, Close Combat Weapons, Grenades, Armour, Field Armour, Personal Equipment, Gang Equipment, Weapon Accessories, Mounts) — distinct from `N26.qmsystem`'s master catalogue, which is only a lookup source here.

For each priced line in the equipment list:
1. **Look it up by exact name** (case-insensitive) in the matching category of `N26.qmsystem`.
2. **Match found** → deep-copy that item, strip only a `TP N` segment from its `Prerequisite` (keep any other comma-separated segment, e.g. a parent-weapon reference), and override `Points` if the gang's list price differs from the master catalogue.
3. **No match** → check if the equipment-list line actually *names a bundle of items that individually exist in N26* (e.g. `sawn-off shotgun with solid & scatter shot` bundling `sawn-off shotgun scatter shot` + `sawn-off shotgun solid shot`, or `grenade launcher with frag & krak grenades (+smoke sub-option)` bundling three grenade-launcher ammo entries). If so, split it into its matched components rather than adding one bare stub — this reads far better than a single opaque line, and matches what's already in the file for Cawdor/Delaque.
4. **Genuinely new** (not in N26 at all, and not a bundle of things that are) → add a bare entry with only `Category`/`Name`/`Points`. If the equipment-*reference* page (stats/traits) for this item is available in the same batch, add `Special Rules`/`Stats` too instead of leaving a stub — don't make the user come back for a second pass if the data's already in hand. If only the reference page arrives later, fill the stub in then.
5. **Restriction tags**: if an item is exclusive to one sub-list (e.g. a gang vs. its allied cult, like Cawdor/Redemptionist) or one specific fighter (e.g. "Psy-Gheist only"), add `Prerequisite: [<bare tag>]` — just the faction or fighter name, no "only"/"exclusive" wording. If the item already has a kept non-TP prerequisite segment, join with a comma (`<existing>, <tag>`). If the *same* item name appears in two sub-lists at *different* prices, it can't be one shared entry — add it twice, once per tag, rather than picking one price.
6. **Skip, don't stub**: items with no independent credit cost that only exist as another fighter's built-in loadout or swap option (e.g. a Brute's default weapon, or an upgrade only reachable through one specific fighter's equipment text) — these aren't equipment-list purchases. Log the skip.
7. Shared items (same name, same price, in every relevant sub-list) get no restriction tag at all.

Always validate with `plistlib.load` and spot-check a few entries (especially any split/renamed bundles) after each batch.

## 4. Skill access table

Maps each fighter to 0+ `(SkillSet, Primary|Secondary)` pairs. Locate, for each fighter, the *fighter's own* `Skills` advancement dict (`Name: "Skills"`, `Maximum: 1`) inside their `Command` tree — not the attached companion's, if this gang has one (search backward from the fighter's `Name` line for the nearest preceding `<string>Skills</string>`; the companion's copy, if any, is always further back). Replace its `Magic Items` array entirely with dicts of the form `{Items: [], Limit: -1, Name: "<SkillSet> Skills", Prerequisite: "Primary"|"Secondary"}`, in the table's column order. A fighter listed in the table with every column dashed still keeps an (empty) entry only if the table explicitly lists them — if a roster fighter is *absent from the table entirely*, remove their `Skills` dict from `Advancements` → `Options` rather than leaving it empty.

**Skewed photos**: these tables are frequently photographed at an angle that makes column alignment genuinely unreliable to OCR — don't guess a full table from a skewed image. Read what's confidently legible, and either ask the user to confirm/correct specific ambiguous cells (via a short targeted question, not a full re-ask) or, if more than a couple of cells are unclear, ask the user to write the table out directly rather than guessing twice.

## 5. Review notes

After finishing a batch of work (a fighter roster, an equipment list, a skills pass), append to `N26/REVIEW_NOTES.md` under that gang's `##` section (create the section if it doesn't exist yet). Log: naming/splitting decisions for bundled or ambiguous items, anything skipped and why, restriction-tag choices, cost conflicts between sub-lists, and any table cells that needed the user's confirmation. Keep entries terse — one or two sentences each, grouped by theme, not a chronological transcript.
