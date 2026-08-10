---
name: parse-weapon-table
description: Convert a screenshot of a weapon stat table (Necromunda/wargame-style, with SR, LR, Str, AP, L, Traits, Creds, TP columns — ranged or close combat) into a plain text file using this project's fixed entry format, appending to a named target file (e.g. "ranged weapons.txt", "close combat weapons.txt"). Use whenever the user shares an image of a weapons table and asks to extract/write it to a text file.
---

# Parse weapon table

Reads a photographed/screenshotted weapon stats table (columns: name, SR, LR, Str, AP, L, Traits, Creds, TP — grouped under headers like "RANGED WEAPONS", "BOLT WEAPONS", "FLAMERS", "GRAV WEAPONS") and writes every row to a `.txt` file as discrete entries.

## Output format

Each weapon is five lines, entries separated by one blank line:

```
<name, lowercase>
<Creds>
SR<val>"•LR<val>"•Str<val>•AP<val>•L<val>
<Traits, verbatim>
TP <number>
```

Example:

```
autogun
20
SR8"•LR24"•Str3•AP-•L1
Rapid Fire (1)
TP 0
```

### Characteristics line rules
- Join SR, LR, Str, AP, L with the bullet character `•` (no spaces).
- Keep the inch mark `"` on SR/LR only when the source shows a numeric distance (e.g. `SR8"`). If the source shows a non-distance placeholder like `T` (template), `E` (engagement range, common on close combat weapons), or `-` (no range), drop the inch mark.
- Str/AP: reproduce the value as printed, including a bare `-` when the table shows no value, negative numbers as `AP-1`, and user-Strength-relative values on melee weapons as printed (`S`, `S+1`, `S+3`).
- L: reproduce as printed, no quote mark (`L1`, `L2`).
- **Letter-led values get a colon.** If a characteristic's value starts with a letter (not a digit or punctuation like `-`), insert a colon between the characteristic label and the value: `SR:E`, `SR:T`, `Str:S`, `Str:S+1`, `Str:S+3`. Values starting with a digit (`SR8"`, `Str3`) or with `-` (`LR-`, `AP-1`, `Str-`) get no colon — the label and value run together as before.

### Name rules
- Lowercase the name exactly as printed.
- If the name has a trailing asterisk in the source (e.g. `Heavy stubber*`), keep the asterisk: `heavy stubber*`.

### Creds rules
- Reproduce the number as printed, but never include a leading `+` sign — write `10`, not `+10`.

### Sub-rows (variants that modify the weapon above, e.g. rows starting with "-" like "- warp round")
These rows share the parent weapon's row above them and only exist to add an ammo/variant modifier. Expand them into full standalone entries:
- Name: `<parent weapon name> <modifier text without its leading "-">`, all lowercase (e.g. parent `autogun` + row `- warp round` → `autogun warp round`).
- Creds: as printed, with any `+` sign stripped.
- Characteristics line: same as the parent weapon's line (these rows don't repeat their own SR/LR/etc. in the source; they inherit the parent's).
- Traits: as printed on that row.
- Last line: `<parent weapon name>, TP <number>` instead of the plain `TP <number>` — i.e. prefix with the parent weapon's lowercase name and a comma.
- If the TP cell for that row is blank/empty in the source (as opposed to showing a digit like `0`), drop the TP portion entirely and just write the parent weapon's lowercase name as the last line — e.g. `grenade launcher`, not `grenade launcher, TP -` or `grenade launcher, TP 0`.

Example (autogun's warp round variant, TP cell has a digit):

```
autogun warp round
10
SR8"•LR24"•Str3•AP-•L1
Cursed, Single Shot
autogun, TP 4
```

### Weapon families where the bare name has no row of its own (e.g. "Grenade launcher", "Shotgun" with multiple ammo types)
Some weapons are listed as a bare name followed by two or more "-" ammo/variant rows, where the bare name itself never gets its own distinct stats or price in the source — the weapon only exists as one of its ammo types. Don't invent a dash-stats entry for the bare name. Instead:
- **Merge the bare name with the first "-" row** into one primary entry: name `<weapon name> <first modifier text>`, using that row's real, as-printed stats/Traits/Creds (no placeholder dashes, no stripped price — it's the base purchase). Its last line is a plain `TP <number>` (or, if that row's TP cell is blank, the dropped-TP form is just the entry's own name context doesn't apply here since there's no separate parent to reference — write `TP <number>` as printed; this row essentially never has a blank TP since it's the base purchase).
- **Every subsequent "-" row** stays a normal sub-row per the rules above, but its parent reference (for the `<parent>, TP <n>` / bare-`<parent>` last line) is the **bare weapon name**, not the merged first-variant name.
- The bare weapon name itself never appears as its own standalone 5-line entry — it's fully represented by the merged primary entry, and only survives as the text used on later sub-rows' last lines.

Example (grenade launcher: frag grenades merges with the bare name; krak/photon flash/smoke stay sub-rows of "grenade launcher"):

```
grenade launcher frag grenades
80
SR6"•LR24"•Str3•AP-•L1
Ammo (4+), Blast (3"), Knockback (5+)
TP 1

grenade launcher krak grenades
0
SR6"•LR24"•Str6•AP-2•L1
Ammo (4+)
grenade launcher

grenade launcher photon flash grenades
15
SR6"•LR24"•Str-•AP-•L-
Ammo (5+), Blast (3"), Flash
grenade launcher, TP 1
```

Example (shotgun: scatter ammo merges with the bare name; solid ammo stays a sub-row of "shotgun"):

```
shotgun scatter ammo
35
SR4"•LR8"•Str3•AP-•L1
Rapid Fire (2)
TP 0

shotgun solid ammo
0
SR8"•LR16"•Str4•AP-•L1
Knockback (5+)
shotgun
```

## Target file
- The filename is an argument to this skill (e.g. `/parse-weapon-table ranged weapons.txt`, or just naming it in the request — "put this in close combat weapons.txt"). It lives in the project root. Add a `.txt` extension if the user didn't include one.
- If that file already exists, append to it — never overwrite or truncate it.
- If it doesn't exist yet, create it.
- If the file exists and doesn't already end with a blank line, add one before appending so entries stay separated.
- If no filename is given for a request, reuse whatever target file this conversation last used for this skill (sticky default). If none has been established yet in this conversation, ask the user which file to use before writing anything — don't invent a name.

## Process
1. Read the image and transcribe every row, grouped by the section headers in the source (weapon type doesn't need to appear in the output, just process every row across all sections in order).
2. Apply the formatting rules above to build each entry.
3. Append all entries to the target file described above, with one blank line between entries (including between the last existing entry and the first new one), in the same order as the source table.
4. If given multiple images/tables in one request, append all resulting entries in the order the images were provided, unless told otherwise.
