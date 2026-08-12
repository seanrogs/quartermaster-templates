# N26 Review Notes

Running log of judgment calls made while building N26 gang files from screenshots, for manual review/correction. Each entry: what was assumed, and why. Newest entries at the bottom of each section.

## N26.qmsystem (master catalogue)

- **Carapace Armour, Servo-Harness split by tier.** Source gives one name with two credit/TP tiers (Light/Heavy, Partial/Full). Split into two catalogue entries named `<item> <tier>` (`carapace armour light` / `carapace armour heavy`, `servo-harness partial` / `servo-harness full`), lowercase, no other fields. Confirmed pattern by user, reused throughout.
- **Weapon accessory restrictions folded into Prerequisite.** `focusing crystal`, `hotshot las pack` → `TP 1, las weapons only`; `suspensors` → `TP 0, weapons marked with * only`. The restriction text is appended verbatim (lowercased) after the TP value, comma-separated, in the single Prerequisite string — not modeled as a separate field.
- **`dirt bike` backfilled with `Prerequisite: [TP 0]`.** It predated the TP-tracking convention (had no Prerequisite at all) and was corrected once a source image gave its TP value.
- **TP-strip rule:** when copying/reusing an entry's Prerequisite elsewhere, strip only a `TP N` segment; keep any other comma-separated segment (e.g. `sawn-off shotgun` stays, `grenade launcher, TP 1` → `grenade launcher`). Established after an initial over-strip mistake.

## House Cawdor.qmtemplate

- **Fighter flavor text not captured.** Skipped: Way-Brethren's Dodge skill and included Ridge Walker mount; Stig-Shambler's Bulging Biceps skill, starting heavy club/heavy flamer loadout, and the +10cr twin-linked heavy stubber swap option. Only Name/Points/Stats/Special Rules(=Type)/XP + the standard Sheen Bird attachment were built — none of these extras exist anywhere in the file yet.
- **Twin-linked heavy stubber skipped entirely.** No independent credit cost in the equipment reference (`Creds: -`), only relevant as Stig-Shambler's swap option (which itself was skipped above). Does not exist in the qmtemplate.
- **Equipment-list lines that name a bundle get split into their matched N26 components** rather than added as one bare stub, whenever the components already exist in `N26.qmsystem`:
  - `sawn-off shotgun with solid & scatter shot` → `sawn-off shotgun scatter shot` + `sawn-off shotgun solid shot`
  - `combi-weapon (autogun/flamer)` → renamed/split to `combi-autogun` (primary profile) + `combi-autogun flamer` (secondary profile, 0cr, prereq `combi-autogun`)
  - `cawdor heavy crossbow with frag & krak shells*` → renamed/split to `cawdor heavy crossbow* frag shells` + `cawdor heavy crossbow* krak shells` (0cr, prereq `cawdor heavy crossbow*`)
  - Redemptionist list: `grenade launcher with frag & krak grenades (+smoke)` → three matched entries (frag/krak/smoke); `shotgun with solid & scatter ammo` → scatter/solid matched, plus two brand-new bare stubs (`shotgun executioner ammo`, `shotgun retributor ammo`) for the ammo types not in N26 at all.
  - These renames are a judgment call — worth checking the split naming reads sensibly in the app.
- **Cawdor/Redemptionist dual-list tagging.** Items unique to one equipment list get `Prerequisite: [Cawdor]` or `[Redemptionist]`; items in both lists (same cost) get no tag. `ridge walker` costs differ between lists (40 vs 45) so it's two separate entries, one per tag, rather than one shared entry.
- **`exterminator (...)` and `fire pike*`** filed under Ranged Weapons matching their source section headers (Auxiliary Weapons / Flamers), even though "exterminator" reads more like an accessory.
- **Skill Access table required a hand-written re-transcription from the user** — the photographed table's skew made automated reading unreliable, and a first attempt at reading it was wrong. Treated the corrected table as authoritative even where it overrode the original hand-authored Word-Keeper example (Combat was Primary in the file, table says Secondary).

## House Delaque.qmtemplate

- **Skeleton built from Cawdor's original (pre-work) commit**, with the "Cawdor Word-keeper" example fighter stripped out entirely rather than kept/renamed — read "based on how Cawdor was when we started" as the structural skeleton, not the literal example content.
- **No auto-attached pet.** Cawdor's Sheen Bird was a fixed `Attached Units` entry on every fighter; Delaque instead lists its pets (`Cephalopod Spektor`, `Psychoteric Wyrm`) as their own standalone roster fighters (Fighter role), so the whole `Attached Units` block was omitted from the fighter template for this gang.
- **Fighter-restricted equipment tagged with a bare fighter name**, dropping the "(...only)" wording: `psychomantic claws*`, `psychomancer's harness` → `Prerequisite: [Psy-Gheist]`; `serpent's fangs*`, `shivver sword` → `Prerequisite: [Nacht-Ghul]`. Same style as the Cawdor/Redemptionist tags but scoped to one fighter instead of a whole gang.
- **"Natural Weapons" reference entries skipped** (Ferocious jaws for Psychoteric Wyrm, Shock tendrils for Cephalopod Spektor) — no credit cost, innate/non-purchasable, same treatment as the twin-linked heavy stubber.
- **Fighter flavor/mechanic text not captured**: Master of Shadow/Phantom's Wyrd subtype option, Nacht-Ghul's "From the Shadows" deployment rule, Psy-Gheist/Piscean Spektor's Wyrd power selection, and the pets' Leash Range/Sensor Array/Psychoteric Node/Burrowing rules.
- **Skill Access table had two unclear cells** (Phantom's Shooting column, Psychoteric Wyrm's Cunning column) due to the same photo-skew issue as Cawdor's table. Resolved via direct confirmation with the user rather than guessing: Phantom Shooting = dash, Psychoteric Wyrm Cunning = Secondary.
