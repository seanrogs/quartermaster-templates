"""WH40K3 Tau, from the 3rd edition Codex: Tau (2001): army list, armoury and special characters.

Usage: python3 -B factions/wh40k3_tau.py "WH40K3/Tau.qmtemplate"

A 'Sept' Trait holds the eight major septs (background only, colours chosen for the
app) and 'Farsight Enclave'. Commander Farsight's Breakaway Faction rules hang off the
Farsight Enclave variant: banned units get 'not Farsight Enclave', units limited to
0-1 get a note, and the Ork Fighter upgrade needs 'Farsight Enclave'.

Battlesuit hard points are one group per model (maximum -3 on teams, 3 on a single
Commander). Twin-linked weapons use two hard points; the app can't count that, so
they carry a note.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from qmtemplate import (armoury, fixed, items, opt, standard, standard_foc, template, toggle,  # noqa: E402
                        trait, unit, unit_limit, write)

ARMOURY = armoury('Hard-wired Support Systems, Drones', 50)
FARSIGHT = 'Farsight Enclave'
NOT_FARSIGHT = 'not Farsight Enclave'
FARSIGHT_0_1 = '0-1 in Farsight Enclave'

GUN_DRONE = 'WS2•BS2•S3•T3•W1•I4•A1•Ld7•Sv4+'
SHIELD_DRONE = 'WS2•BS2•S3•T3•W1•I4•A1•Ld-•Sv4+'


def ork_fighter():
    """Farsight Enclave upgrade for Tau units: +1 WS and I at +5 pts per model."""
    return [{'Name': 'Ork Fighter', 'Points': 5.0, 'Stats': 'WS+1•I+1', 'Prerequisite': [FARSIGHT]}]


def bonded():
    """Ta'lissera bond: +10 pts for the whole team."""
    return [opt('bonded', 10, maximum=1)]


# ---------------------------------------------------------------- battlesuits

def support_systems(first_maximum):
    return [
        opt('multi-tracker', 5, maximum=first_maximum),
        opt('target lock', 5),
        opt('shield generator', 20),
        opt('drone controller and 1 gun drone', 10),
        opt('drone controller and 2 gun drones', 20),
        opt('drone controller and 1 shield drone', 15),
        opt('drone controller and 2 shield drones', 30),
    ]


def crisis_hard_points(maximum):
    """XV8 Crisis: three hard points, each a weapon or support system."""
    tl = 'uses two hard points'
    return [
        opt('flamer', 6, maximum=maximum),
        opt('burst cannon', 10),
        opt('twin-linked burst cannon', 15, prereq=tl),
        opt('fusion blaster', 12),
        opt('twin-linked fusion blaster', 18, prereq=tl),
        opt('missile pod', 14),
        opt('twin-linked missile pod', 21, prereq=tl),
        opt('plasma rifle', 16),
        opt('twin-linked plasma rifle', 24, prereq=tl),
    ] + support_systems(None)


def team_leader(shas_vre_stats, markerlight=False):
    """Battlesuit team leader: Shas'ui at +5, or Shas'vre at +10."""
    options = [[opt('markerlight', 10, maximum=1)]] if markerlight else None
    return [[
        opt('Shas’ui team leader', 5, maximum=1, options=options, magic_items=ARMOURY),
        opt('Shas’vre team leader', 10, stats=shas_vre_stats, options=options, magic_items=ARMOURY),
    ]]


def bodyguard(prereq=None):
    return unit('XV8 Crisis Battlesuit Bodyguard Team', 40, 'WS3•BS3•S5•T4•W2•I3•A2•Ld8•Sv3+', size=1,
                minimum=1, maximum=2, singular='Shas’vre', plural='Shas’vre', upper=1, rules='Bonded',
                equipment=[standard('XV8 Crisis battlesuits'), crisis_hard_points(-3), bonded(), ork_fighter()],
                magic_items=ARMOURY, prereq=prereq)


# ---------------------------------------------------------------- vehicles

VEHICLE_UPGRADES = [('sensor spines', 5), ('targeting array', 5), ('multi-tracker', 10), ('blacksun filter', 5),
                    ('target lock', 5), ('pair of gun drones', 20), ('flechette discharger', 5),
                    ('disruption pod', 5), ('decoy launchers', 5)]


def vehicle_upgrades(exclude=()):
    groups = [[opt(n, p, maximum=1)] for n, p in VEHICLE_UPGRADES if n not in exclude]
    groups.append([opt('seeker missile', 10, maximum=4)])
    return groups


def devilfish(prereq=None, lower=None):
    return unit('Devilfish Troop Carrier', 80, 'FA12•SA11•RA10•BS3', rules='Tank, Skimmer; Transport (12)',
                equipment=[fixed('burst cannon'), fixed('pair of gun drones')]
                + vehicle_upgrades(exclude=('pair of gun drones',)),
                prereq=prereq, lower=lower, upper=1)


# ---------------------------------------------------------------- HQ

def commander(name, pts, stats):
    return unit(name, pts, stats, rules='Independent Character; Bodyguard',
                equipment=[standard('XV8 Crisis battlesuit'), crisis_hard_points(3), ork_fighter()],
                magic_items=ARMOURY, attached=[bodyguard()])


HQ = [
    commander('Shas’o', 75, 'WS4•BS5•S5•T4•W4•I3•A4•Ld10•Sv3+'),
    commander('Shas’el', 50, 'WS3•BS4•S5•T4•W3•I3•A3•Ld9•Sv3+'),
    unit('Ethereal', 50, 'WS4•BS3•S3•T3•W2•I3•A3•Ld10•Sv-', upper=1,
         rules='Independent Character; Inspiring Presence; Price of Failure',
         equipment=[[opt('symbols of office', 0, count=1, maximum=1, default=True), opt('honour blade', 10)]],
         magic_items=ARMOURY, prereq=NOT_FARSIGHT),
    unit('Commander Farsight', 170, 'WS5•BS5•S3(5)•T3(4)•W3(4)•I5•A4•Ld10•Sv3+', upper=1,
         rules='Dawn Blade; Ork Fighter; Breakaway Faction; Independent Character; Bodyguard',
         equipment=[fixed('XV8 Crisis battlesuit'), fixed('shield generator'), fixed('plasma rifle'),
                    fixed('Dawn Blade')],
         attached=[bodyguard(prereq='must take Ork Fighter')], prereq=FARSIGHT),
    unit('Aun’shi', 105, 'WS5•BS3•S3•T3•W3•I5•A4•Ld10•Sv4+', upper=1,
         rules='Independent Character; Blade Master; Inspiring Presence; Price of Failure',
         equipment=[fixed('honour blade'), fixed('hard-wired shield generator'), fixed('photon grenades'),
                    fixed('EMP grenades')],
         prereq=NOT_FARSIGHT),
]

# ---------------------------------------------------------------- Elites

ELITES = [
    unit('XV8 Crisis Battlesuit Team', 30, 'WS2•BS3•S5•T4•W2•I2•A2•Ld8•Sv3+', size=1, minimum=1, maximum=3,
         singular='Shas’ui', plural='Shas’ui', rules='Bonded',
         command=team_leader('WS3•BS3•S5•T4•W2•I3•A2•Ld8•Sv3+'),
         equipment=[standard('XV8 Crisis battlesuits'), crisis_hard_points(-3), bonded(), ork_fighter()]),
    unit('XV15 Stealth Team', 30, 'WS2•BS3•S4•T3•W1•I2•A2•Ld8•Sv3+', size=3, minimum=3, maximum=6,
         singular='Shas’ui', plural='Shas’ui', rules='Stealth Armour; Infiltrate; Bonded',
         command=team_leader('WS3•BS3•S4•T3•W1•I3•A2•Ld8•Sv3+', markerlight=True),
         equipment=[standard('XV15 Stealth battlesuits'), standard('burst cannons'), bonded(), ork_fighter()],
         prereq=FARSIGHT_0_1),
]

# ---------------------------------------------------------------- Troops

TROOPS = [
    unit('Fire Warrior Team', 10, 'WS2•BS3•S3•T3•W1•I2•A1•Ld7•Sv4+', size=6, minimum=6, maximum=12, lower=1,
         singular='Shas’la', plural='Shas’la', rules='Bonded',
         command=[[opt('Shas’ui', 10, maximum=1, stats='WS2•BS3•S3•T3•W1•I2•A2•Ld8•Sv4+',
                       options=[[opt('markerlight', 10, maximum=1)]], magic_items=ARMOURY)]],
         equipment=[[opt('pulse rifle', 0, count=6, maximum=-1, default=True),
                     opt('pulse carbine', 0, prereq='up to half the team')],
                    toggle('photon grenades', 1), toggle('EMP grenades', 3), bonded(), ork_fighter()],
         attached=[devilfish(prereq='12 models or fewer, including drones')]),
    unit('Kroot Carnivore Squad', 7, 'WS4•BS3•S4•T3•W1•I3•A1•Ld7/8•Sv-', size=10, minimum=10, maximum=20,
         singular='Kroot', plural='Kroot', rules='Mercenaries; Eaters of the Dead; Fieldcraft; Infiltrate',
         command=[[opt('Shaper', 21, maximum=1, stats='WS4•BS3•S4•T3•W3•I3•A3•Ld7/8•Sv6+',
                       options=[[opt('Kroot rifle', 0, count=1, maximum=1, default=True),
                                 opt('pulse rifle', 5), opt('pulse carbine', 5)]])]],
         equipment=[standard('Kroot rifles'),
                    [{'Name': 'Kroot armour', 'Points': 1.0, 'Stats': 'Ld=8•Sv=6+', 'Prerequisite': ['Shaper']}]],
         prereq=NOT_FARSIGHT),
]

# ---------------------------------------------------------------- Fast Attack

FAST = [
    unit('Gun Drone Squadron', 12, GUN_DRONE, size=4, minimum=4, maximum=8,
         singular='Gun Drone', plural='Gun Drones', rules='Jetpacks; Independent',
         equipment=[standard('twin-linked pulse carbines')], prereq=NOT_FARSIGHT),
    unit('Pathfinder Team', 12, 'WS2•BS3•S3•T3•W1•I2•A1•Ld7•Sv4+', size=4, minimum=4, maximum=8,
         singular='Shas’la', plural='Shas’la', rules='Bonded; Forward Scouts',
         command=[[opt('Shas’ui', 10, maximum=1, stats='WS2•BS3•S3•T3•W1•I2•A2•Ld8•Sv4+', magic_items=ARMOURY)]],
         equipment=[standard('pulse carbines with markerlights'), toggle('photon grenades', 1),
                    toggle('EMP grenades', 3), bonded(), ork_fighter()],
         attached=[devilfish(lower=1)], prereq=FARSIGHT_0_1),
    unit('Kroot Hound Pack', 6, 'WS4•BS0•S4•T3•W1•I4•A2•Ld*•Sv*', size=2, minimum=2, maximum=8,
         singular='Kroot Hound', plural='Kroot Hounds', rules='Attached Unit; Release the Hounds',
         equipment=[standard('fangs')], requires=['Kroot Carnivore Squad'],
         prereq=['attached to a Kroot Carnivore Squad', NOT_FARSIGHT]),
]

# ---------------------------------------------------------------- Heavy Support

HEAVY = [
    unit('XV88 Broadside Battlesuit Team', 70, 'WS2•BS3•S5•T4•W2•I2•A2•Ld8•Sv2+', size=1, minimum=1, maximum=3,
         singular='Shas’ui', plural='Shas’ui', rules='Bonded',
         command=team_leader('WS3•BS3•S5•T4•W2•I3•A2•Ld8•Sv2+'),
         equipment=[standard('XV88 Broadside battlesuits'), standard('twin-linked railguns'),
                    [opt('smart missile system', 0, count=1, maximum=-1, default=True),
                     opt('twin-linked plasma rifle', 10)],
                    support_systems(-1), bonded(), ork_fighter()],
         prereq=FARSIGHT_0_1),
    unit('Hammerhead Gunship', 90, 'FA13•SA12•RA10•BS3(4)', rules='Tank, Skimmer',
         equipment=[[opt('ion cannon', 30, count=1, maximum=1, default=True), opt('railgun', 50)],
                    [opt('two burst cannon', 10, count=1, maximum=1, default=True),
                     opt('smart missile system', 20)],
                    fixed('targeting array')] + vehicle_upgrades(exclude=('targeting array',)),
         prereq=FARSIGHT_0_1),
    unit('Krootox', 50, 'WS4•BS3•S6•T3(5)•W3•I3•A3•Ld*•Sv*', size=1, minimum=1, maximum=3,
         rules='Attached Unit', equipment=[standard('Kroot guns')], requires=['Kroot Carnivore Squad'],
         prereq=['attached to a Kroot Carnivore Squad', NOT_FARSIGHT]),
]

# ---------------------------------------------------------------- Armoury

HARD_WIRED = 'one per model; Commanders up to three'
ITEMS = [
    items('Hard-wired Support Systems', [
        ('hard-wired multi-tracker', 10, HARD_WIRED, None),
        ('hard-wired target lock', 7, HARD_WIRED, None),
        ('hard-wired blacksun filter', 3, HARD_WIRED, None),
        ('hard-wired drone controller', 2, HARD_WIRED, None),
    ]),
    items('Drones', [
        ('gun drone', 10, 'drone controller', GUN_DRONE, True),
        ('shield drone', 15, 'drone controller', SHIELD_DRONE, True),
    ]),
]

SEPTS = [
    ('T’au', '#C8893A', '#2B2B2B'),
    ('Tau’n', '#C9962E', '#2A2F6E'),
    ('Vior’la', '#E8E6DF', '#9E1A1A'),
    ('D’yanoi', '#A3A65A', '#1F6B35'),
    ('Dal’yth', '#E3D3A0', '#8A5A2B'),
    ('Sa’cea', '#3A3F44', '#8F9AA6'),
    ('Bork’an', '#2A2F6E', '#B3261E'),
    ('Fal’shia', '#1F8A8A', '#F7F7F5'),
    (FARSIGHT, '#B3261E', '#F7F7F5'),
]

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ethereal = unit_limit('Ethereal caste member', ['Ethereal', 'Aun’shi'])
    write(template('Tau', 'WH40K3', 20261124,
                   standard_foc(HQ, ELITES, TROOPS, FAST, HEAVY, hq_limits=[ethereal]), ITEMS,
                   traits=[trait('Sept', SEPTS)]),
          sys.argv[1])
