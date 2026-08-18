---
name: wahapedia-compare
description: Compare one or more Horus Heresy 3rd edition .qmtemplate files (e.g. Loyalist/Traitor Legiones Astartes, Solar Auxilia) against their faction page on wahapedia.ru and report missing units, points mismatches, wargear discrepancies, or naming differences. Use when the user asks to compare, check, or validate a qmtemplate file against wahapedia.
---

# Wahapedia Compare

Compare one or more `.qmtemplate` files against their corresponding faction page on wahapedia.ru and report significant differences.

## Usage

```
/wahapedia-compare [template file(s)] [wahapedia URL]
```

**Examples:**
- `/wahapedia-compare` — compare the Loyalist and Traitor Legiones Astartes templates against wahapedia.ru/heresy3/factions/legiones-astartes/
- `/wahapedia-compare "Solar Auxilia.qmtemplate" https://wahapedia.ru/heresy3/factions/solar-auxilia/`

## Instructions

When this skill is invoked:

1. **Identify files and URL.** If the user provided specific template filenames and/or a wahapedia URL, use those. Otherwise default to comparing both `Loyalist Legiones Astartes.qmtemplate` and `Traitor Legiones Astartes.qmtemplate` against `https://wahapedia.ru/heresy3/factions/legiones-astartes/`. All `.qmtemplate` files are in the current working directory.

2. **Delegate to a general-purpose subagent** using the Agent tool with this prompt (fill in the actual filenames and URL):

```
Compare [TEMPLATE FILE(S)] against [WAHAPEDIA URL] for Horus Heresy 3rd edition.

The .qmtemplate files are Apple plist XML. They are large (~1.7MB each) — read them in chunks of 500 lines using offset/limit.

Look for:
1. Units present on wahapedia but absent from the template(s) — check all categories: Warlord, High Command, Command, Retinue, Elites, Troops, Fast Attack, Heavy Support, Lords of War, etc.
2. Units in the template(s) but not on wahapedia (stale entries)
3. Points cost mismatches between template and wahapedia
4. Wargear options listed on wahapedia missing from template wargear categories, or with wrong prices
5. Naming discrepancies (spelling, word order, prefixes)

To extract unit names and points from the templates, grep for <key>Name</key> and <key>Points</key> patterns. Also fetch any linked subpages on wahapedia needed to get complete unit lists.

Produce a structured report organised by priority:
- HIGH: Missing units, points errors
- MEDIUM: Structural/design differences
- LOW: Naming/spelling discrepancies

Be specific — name the unit and state the exact discrepancy.
```

3. **Relay the agent's report** back to the user once complete.
