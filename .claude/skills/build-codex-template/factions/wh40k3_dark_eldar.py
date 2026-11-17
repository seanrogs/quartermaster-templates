"""WH40K3 Dark Eldar, from the 3rd edition Codex: Dark Eldar (army list, armoury and special characters).

Usage: python3 factions/wh40k3_dark_eldar.py "WH40K3/Dark Eldar.qmtemplate"

The Wych Cult variant is handled in the one file with Prerequisite notes: units are
duplicated into their Wych Cult slot tagged 'Wych Cult', and normal-slot copies or
banned units are tagged 'not Wych Cult'.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from qmtemplate import armoury, fixed, items, opt, standard_foc, template, toggle, unit, write  # noqa: E402

ARMOURY = armoury('Wargear, Arcane Wargear')


# ---------------------------------------------------------------- weapons

def single_handed(per_model=False):
    m = -2 if per_model else 2
    return [
        opt('agoniser', 20, maximum=m),
        opt('close combat weapon', 1),
        opt('poisoned blades', 5),
        opt('power weapon', 15),
        opt('splinter pistol', 1),
    ]


def two_handed(per_model=False):
    m = -1 if per_model else 1
    return [
        opt('hellglaive', 5, maximum=m, prereq='Hellion skyboard; no other weapons'),
        opt('punisher', 20, prereq='no other weapons'),
        opt('splinter rifle', 2),
    ]


def haemonculi_weapons():
    return [
        opt('destructor', 15, maximum=-2),
        opt('scissorhand', 5),
        opt('stinger', 5),
    ]


def character_weapons():
    """Armoury weapon choices for squad characters (Sybarites, Succubi)."""
    return [
        [opt('splinter rifle', 0, count=1, maximum=1, default=True),
         opt('splinter pistol and close combat weapon', 0)],
        [opt('agoniser', 20, maximum=1), opt('poisoned blades', 5), opt('power weapon', 15)],
        [opt('punisher', 20, maximum=1, prereq='no other weapons')],
    ]


def succubus_weapons():
    return [
        [opt('splinter pistol and close combat weapon', 0, count=1, maximum=1, default=True)],
        [opt('agoniser', 20, maximum=1), opt('poisoned blades', 5), opt('power weapon', 15)],
        [opt('punisher', 20, maximum=1, prereq='no other weapons')],
    ]


def sybarite(stats='WS4•BS4•S3•T3•W1•I5•A2•Ld8•Sv5+', pts=6):
    return [opt('Sybarite', pts, maximum=1, stats=stats, options=character_weapons(), magic_items=ARMOURY)]


def succubus(name, pts, stats):
    return [opt(name, pts, maximum=1, stats=stats, options=succubus_weapons(), magic_items=ARMOURY)]


# ---------------------------------------------------------------- vehicles

RAIDER_UPGRADES = [('horrorfex', 5), ('night shield', 15), ('scaling nets', 5), ('screaming jets', 15),
                   ('scythes', 10), ('slave snares', 15), ('torture amp', 10), ('trophy racks', 10)]
RAVAGER_UPGRADES = [('horrorfex', 5), ('night shield', 20), ('screaming jets', 10), ('scythes', 10)]


def raider(prereq=None, lower=None):
    eq = [[opt('dark lance', 0, count=1, maximum=1, default=True), opt('disintegrator', 5)]]
    eq += [[opt(n, p, maximum=1)] for n, p in RAIDER_UPGRADES]
    return unit('Raider', 55, 'FA10•SA10•RA10•BS4', rules='Skimmer, Fast, Open-topped; Transport (10)',
                equipment=eq, prereq=prereq, lower=lower, upper=1)


def ravager():
    eq = [[opt('dark lance', 0, count=3, maximum=3, default=True), opt('disintegrator', 5)]]
    eq += [[opt(n, p, maximum=1)] for n, p in RAVAGER_UPGRADES]
    return unit('Ravager', 105, 'FA11•SA11•RA10•BS4', rules='Skimmer, Fast, Open-topped', equipment=eq)


# ---------------------------------------------------------------- retinues

def kabal_retinue():
    command = [[
        opt('Warrior', 0, count=5, maximum=-1, default=True, stats='WS4•BS4•S3•T3•W1•I5•A1•Ld8•Sv5+',
            options=[[opt('splinter rifle', 0, count=1, maximum=-1, default=True)]]),
        opt('Incubus', 17, stats='WS5•BS4•S3•T3•W1•I5•A1•Ld8•Sv3+',
            options=[[opt('tormentor helm', 0, count=1, maximum=-1, default=True)],
                     [opt('punisher', 0, count=1, maximum=-1, default=True)]]),
        opt('Incubi Master', 35, stats='WS5•BS4•S3•T3•W1•I6•A2•Ld9•Sv3+', prereq='0-1; 5+ Incubi',
            options=[[opt('tormentor helm', 0, count=1, maximum=-1, default=True)],
                     [opt('punisher', 0, count=1, maximum=-1, default=True)]],
            magic_items=ARMOURY),
        opt('Drazhar', 82, stats='WS6•BS4•S4•T3•W3•I6•A2(3)•Ld9•Sv3+', prereq='0-1; takes the place of an Incubus',
            rules='Disemboweller Blades; Bodyguard',
            options=[[opt('tormentor helm', 0, count=1, maximum=-1, default=True)],
                     [opt('Disemboweller Blades', 0, count=1, maximum=-1, default=True)]]),
    ]]
    equipment = [
        [opt('splinter cannon', 10, maximum=2, prereq='Warriors'), opt('dark lance', 15, prereq='Warriors')],
        [opt('shredder', 10, maximum=2, prereq='Incubi'), opt('blaster', 6, prereq='Incubi')],
        toggle('plasma grenades', 2),
    ]
    return unit('Dark Eldar Retinue', 8, None, size=5, minimum=5, maximum=10, upper=1, singular='Retinue member',
                plural='Retinue', command=command, equipment=equipment)


def wych_retinue(name='Wych Retinue', rules='Combat Drugs; Dodge; Wych Weapons'):
    u = wyches(retinue=True)
    u['Name'] = name
    u['Special Rules'] = rules
    u['Upper Limit'] = 1
    u['Maximum Size'] = 10
    u.pop('Prerequisite', None)
    return u


def lord_raider():
    return raider(prereq='with Retinue; 10 models or fewer')


# ---------------------------------------------------------------- squads

def warrior_squad(mounted, prereq):
    if mounted:
        name, lo, hi = 'Raider Squad', 5, 10
        special = [[opt('shredder', 10, maximum=1), opt('blaster', 5)],
                   [opt('dark lance', 10, maximum=1), opt('splinter cannon', 10)]]
        attached = [raider(lower=1)]
    else:
        name, lo, hi = 'Warrior Squad', 10, 20
        special = [[opt('shredder', 10, maximum=2), opt('blaster', 5)],
                   [opt('dark lance', 10, maximum=2), opt('splinter cannon', 10)]]
        attached = None
    return unit(name, 8, 'WS4•BS4•S3•T3•W1•I5•A1•Ld8•Sv5+', size=lo, minimum=lo, maximum=hi,
                plural='Warriors', singular='Warrior', command=[sybarite()],
                equipment=[[opt('splinter rifles', 0, equipped=True)]] + special,
                attached=attached, prereq=prereq)


def warp_beasts():
    beastmaster = opt('Beastmaster', 15, count=1, maximum=1, default=True, additional=True,
                      stats='WS4•BS4•S3•T3•W1•I6•A1•Ld8•Sv6+',
                      options=[[opt('agoniser', 0, count=1, maximum=1, default=True)],
                               [opt('splinter pistol', 0, count=1, maximum=1, default=True)]])
    return unit('Warp Beast Pack', 12, 'WS4•BS0•S4•T3•W1•I5•A3•Ld3•Sv6+', size=3, minimum=3, maximum=5,
                singular='Warp Beast', plural='Warp Beasts', upper=1, rules='Warp Beasts; Beastmaster',
                command=[[beastmaster]], prereq='0-1; Wych Cult: one per Wyches squad')


def wyches(prereq=None, retinue=False):
    attached = None if retinue else [raider(prereq='10 models or fewer'), warp_beasts()]
    return unit('Wyches', 12, 'WS4•BS4•S3•T3•W1•I6•A1•Ld8•Sv6+', size=5, minimum=5, maximum=20,
                singular='Wych', rules='Combat Drugs; Dodge; Wych Weapons',
                command=[succubus('Wych Succubus', 8, 'WS4•BS4•S3•T3•W1•I6•A2•Ld8•Sv6+')],
                equipment=[[opt('splinter pistols', 0, equipped=True)],
                           [opt('close combat weapons', 0, equipped=True)],
                           [opt('shredder', 10, maximum=2), opt('blaster', 5)],
                           toggle('plasma grenades', 1),
                           toggle('haywire grenades', 4),
                           toggle('Wych weapons', 1)],
                attached=attached, prereq=prereq)


def grotesques():
    return unit('Grotesques', 15, 'WS4•BS0•S4•T3•W2•I3•A2•Ld5•Sv-', size=3, minimum=3, maximum=10,
                singular='Grotesque', rules='Stupid; Feel No Pain; Terrifying Opponent',
                attached=[raider(prereq='accompanied by an Independent Character')], prereq='not Wych Cult')


def mandrakes():
    return unit('Mandrakes', 15, 'WS4•BS4•S3•T3•W1•I5•A1•Ld8•Sv5+', size=5, minimum=5, maximum=10,
                singular='Mandrake', rules='Shadow-skinned; Hidden Deployment',
                equipment=[[opt('splinter pistols', 0, equipped=True)],
                           [opt('close combat weapons', 0, equipped=True)]])


# ---------------------------------------------------------------- HQ

def lord(name, pts, stats, prereq, wych=False):
    equipment = [single_handed(), two_handed()]
    if wych:
        equipment.insert(0, [opt('Wych weapons', 0, equipped=True)])
        rules = 'Independent Character; Wych Weapons; Dodge; Wych Retinue'
        attached = [wych_retinue(), lord_raider()]
    else:
        rules = 'Independent Character; Retinue'
        attached = [kabal_retinue(), lord_raider()]
    return unit(name, pts, stats, rules=rules, upper=1 if prereq and '0-1' in prereq else None,
                equipment=equipment, magic_items=ARMOURY, attached=attached, prereq=prereq)


HQ = [
    lord('Archon', 60, 'WS6•BS6•S3•T3•W3•I7•A3•Ld9•Sv5+', '0-1 Archon or Archite; not Wych Cult'),
    lord('Dracon', 35, 'WS5•BS5•S3•T3•W2•I6•A2•Ld9•Sv5+', 'not Wych Cult'),
    lord('Wych Archite', 70, 'WS6•BS6•S3•T3•W3•I8•A3•Ld9•Sv6+', '0-1 Archon or Archite', wych=True),
    lord('Wych Dracite', 45, 'WS5•BS5•S3•T3•W2•I7•A2•Ld9•Sv6+', None, wych=True),
    unit('Haemonculi', 25, 'WS4•BS4•S3•T4•W2•I4•A2•Ld8•Sv5+', size=1, minimum=1, maximum=3,
         singular='Haemonculus', plural='Haemonculi', rules='Independent Character',
         equipment=[haemonculi_weapons()], magic_items=ARMOURY, prereq='not Wych Cult'),
    unit('Asdrubael Vect', 277, 'WS6•BS6•S4•FA14(11)•SA14(11)•RA14(10)•I7•A5', upper=1,
         rules='Fast, Skimmer, Open-topped; Dais of Destruction; Energy Field; Independent Character',
         prereq='2,000+ points; counts as Archon',
         equipment=[fixed('Dais of Destruction'), [opt('disintegrator', 0, count=2, maximum=2, default=True)],
                    fixed('dark lance'), fixed('splinter pistols'), fixed('power weapons')]),
    unit('Kruellagh the Vile', 125, 'WS6•BS6•S3•T3•W3•I7•A3(4)•Ld9•Sv5+', upper=1,
         rules='Independent Character; Soul Flayer; Damnation Grenades; Retinue',
         prereq='1,500+ points; Kabal of the Flayed Skull; counts as Archon',
         equipment=[fixed('hell mask'), fixed('terrorfex (Damnation grenades)'), fixed('Soul Flayer')],
         attached=[kabal_retinue(), lord_raider()]),
    unit('Lelith Hesperax', 90, 'WS7•BS6•S3•T3•W3•I8•A3•Ld9•Sv6+', upper=1,
         rules='Independent Character; Wych Weapons; Dodge; Lelith’s Retinue',
         prereq='1,500+ points; Wych Cult; counts as Archite',
         equipment=[fixed('agoniser'), fixed('splinter pistol'), fixed('shadow field'), fixed('Wych weapons')],
         attached=[wych_retinue('Lelith’s Retinue', 'Combat Drugs (choose result); Dodge; Wych Weapons'),
                   lord_raider()]),
    unit('Urien Rakarth', 100, 'WS4•BS4•S3•T4•W2•I4•A2•Ld8•Sv5+', upper=1,
         rules='Independent Character; Master Haemonculus; Retinue',
         prereq='Army led by an Archon; not Wych Cult',
         equipment=[fixed('destructor'), fixed('stinger'), fixed('poisoned blades'), fixed('Crucible of Malediction')],
         attached=[unit('Uber Grotesques', 15, 'WS5•BS0•S4•T3•W2•I4•A2•Ld6•Sv5+', size=1, minimum=1, maximum=5,
                        singular='Uber Grotesque', upper=1,
                        rules='Stupid; Feel No Pain; Terrifying Opponent',
                        attached=[raider(prereq='accompanied by Urien')])]),
    unit('Decapitator', 112, 'WS5(6)•BS5•S3•T3•W2•I6•A2(4)•Ld9•Sv5+', upper=1,
         rules='Independent Character; Additional Limbs; Decapitator; Shadow-skinned; Master Infiltrator',
         prereq='Army must include Mandrakes',
         equipment=[fixed('gruesome talismans'), fixed('severed heads (trophy rack)'), fixed('splinter pistol'),
                    fixed('Decapitator')]),
]


ELITES = [
    grotesques(),
    mandrakes(),
    wyches(prereq='not Wych Cult'),
    warrior_squad(False, 'Wych Cult'),
    warrior_squad(True, 'Wych Cult'),
]

TROOPS = [
    warrior_squad(False, 'not Wych Cult'),
    warrior_squad(True, 'not Wych Cult'),
    wyches(prereq='Wych Cult'),
]

FAST = [
    unit('Reaver Jetbike Squad', 25, 'WS4•BS4•S4•T4•W1•I6•A1•Ld8•Sv4+', size=3, minimum=3, maximum=10,
         singular='Reaver', plural='Reavers', rules='Reaver Jetbike; Combat Drugs',
         command=[succubus('Reaver Succubus', 16, 'WS4•BS4•S4•T4•W1•I6•A2•Ld8•Sv4+')],
         equipment=[[opt('splinter pistols', 0, equipped=True)]],
         mount=[[opt('Reaver jetbikes', 0, equipped=True,
                     options=[[opt('splinter rifle', 0, count=1, maximum=-1, default=True)],
                              [opt('shredder', 15, maximum=2), opt('blaster', 10)]])]]),
    unit('Hellions', 18, 'WS4•BS4•S3•T3•W1•I6•A1•Ld8•Sv5+', size=3, minimum=3, maximum=10,
         singular='Hellion', upper=1,
         rules='Hellion Skyboard & Hellglaive; Combat Drugs; Deep Strike; Hit & Run',
         command=[succubus('Hellion Succubus', 16, 'WS4•BS4•S3•T3•W1•I6•A2•Ld8•Sv5+')],
         equipment=[[opt('hellglaives', 0, equipped=True)],
                    [opt('shredder', 15, maximum=1), opt('blaster', 10)]],
         mount=[[opt('Hellion skyboards', 0, equipped=True)]], prereq='0-1'),
]

HEAVY = [
    unit('Scourges', 16, 'WS4•BS4•S3•T3•W1•I5•A1•Ld8•Sv5+', size=5, minimum=5, maximum=10,
         singular='Scourge', rules='Jump Packs; Deep Strike', command=[sybarite()],
         equipment=[[opt('splinter rifles', 0, equipped=True)],
                    [opt('splinter cannon', 20, maximum=4), opt('dark lance', 25)]]),
    ravager(),
    unit('Talos', 100, 'WS5•BS3•S7•T7•W3•I4•AD6•Ld-•Sv3+',
         rules='Wildfire; Talos Claws; Fearless; Skimmer',
         equipment=[fixed('Talos sting'), fixed('Talos claws')], prereq='not Wych Cult'),
]

ITEMS = [
    items('Wargear', [
        ('Combat drugs', 25, None, None),
        ('Crucible of Malediction', 20, 'One per army', None),
        ('Gruesome talisman', 2, None, None),
        ('Haywire grenades', 4, None, None),
        ('Hell mask', 5, 'One mask per model', None),
        ('Hellion skyboard', 15, None, 'Sv+1'),
        ('Plasma grenades', 2, None, None),
        ('Reaver jetbike', 35, None, 'T+1•Sv+1'),
        ('Shadow field', 25, 'One per army', None),
        ('Soul seeker ammunition', 10, None, None),
        ('Terrorfex', 15, None, None),
        ('Tormentor helm', 5, None, None),
        ('Trophy rack', 5, None, None),
        ('Webway portal', 50, None, None),
    ]),
    items('Arcane Wargear', [
        ('Animus Vitae', 15, 'One per army', None),
        ('Archangel of Pain', 5, 'One per army', None),
        ('Goblet of Spite', 5, 'Succubi only; one per army', None),
        ('Mask of the Damned', 15, 'One per army; one mask per model', None),
        ('Nightmare Doll', 20, 'One per army', None),
        ('Vexantrope', 10, 'One per army; one mask per model', None),
        ('Xenospasm', 20, 'One per army', None),
    ]),
]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    write(template('Dark Eldar', 'WH40K3', 20261118, standard_foc(HQ, ELITES, TROOPS, FAST, HEAVY), ITEMS),
          sys.argv[1])
