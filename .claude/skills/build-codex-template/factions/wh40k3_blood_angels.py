"""WH40K3 Blood Angels, from the 3rd edition Codex: Blood Angels (1998), built on Space Marines.

Usage: python3 -B factions/wh40k3_blood_angels.py "WH40K3/Blood Angels.qmtemplate"

The codex is a supplement used with Codex: Space Marines: the units it lists as "see
Codex: Space Marines" are copied from WH40K3/Space Marines.qmtemplate (read from the
output file's folder), and the codex's own entries are added or replace them. Re-run
after editing Space Marines to pick up its changes.

Blood Angels characters take an Honour Guard instead of a Command squad; the Chaplain
and Lemartes lead the Death Company instead. Blood Angels Rhinos and Razorbacks cost
65 and 85 pts with over-charged engines, wherever they appear.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from qmtemplate import (base_items, base_unit, find_option, fixed, items, load, opt,  # noqa: E402
                        remove_options, standard, standard_foc, template, toggle, unit, unit_limit, write)

SM = None  # the parent Space Marines template, loaded in main

VETERAN = 'WS4•BS4•S4•T4•W1•I4•A1•Ld9•Sv3+'
VETERAN_SERGEANT = 'WS4•BS4•S4•T4•W1•I4•A2•Ld9•Sv3+'
TRANSPORT_COST = {'Rhino': 65.0, 'Razorback': 85.0}


# ---------------------------------------------------------------- helpers

def blood_angels_transports(u):
    """Blood Angels Rhinos and Razorbacks: over-charged engines, 65 and 85 pts."""
    for a in u.get('Attached Units', []):
        if a['Name'] in TRANSPORT_COST:
            a['Points'] = TRANSPORT_COST[a['Name']]
            a['Special Rules'] = 'Tank; Over-charged Engine'
    return u


def sm(name, **changes):
    return blood_angels_transports(base_unit(SM, name, **changes))


def character_groups():
    """Sanguinary Priest, Techmarine and Standard Bearer, from the Space Marines Command Squad upgrades."""
    groups = base_unit(SM, 'Force Commander')['Attached Units'][0]['Command'][1:]
    groups[0][0]['Name'] = 'Sanguinary Priest'
    return groups


def honour_guard():
    u = base_unit(SM, 'Space Marine Veteran Squad', Name='Honour Guard', Plural_Name='Honour Guard',
                  Attached_Units=None)
    honours = u['Equipment'][-1]
    honours[0]['Prerequisite'] = ['led by a Hero, Librarian or Sanguinary High Priest with Terminator honours, '
                                  'and Veteran Sergeant']
    u['Command'] += character_groups()
    u['Equipment'] = [
        [opt('bolter', count=u['Size'], maximum=-1, default=True), opt('bolt pistol and close combat weapon')],
        [opt('flamer', 3, maximum=2), opt('plasma gun', 6), opt('plasma pistol and close combat weapon', 5),
         opt('meltagun', 10)],
        [opt('power weapon', 10, maximum=-1, prereq='close combat weapon')],
        toggle('frag grenades', 1),
        toggle('krak grenades', 2),
        toggle('melta bombs', 4),
        honours,
    ]
    u['Mount'] = [[{'Name': 'jump packs', 'Points': 10.0, 'Special Rules': 'Deep Strike',
                    'Prerequisite': ['led by a character with a jump pack', 'no transport']}]]
    return u


def with_honour_guard(u):
    """Swap the Space Marines Command Squad for an Honour Guard, keeping its transports."""
    attached = u.get('Attached Units') or base_unit(SM, 'Force Commander')['Attached Units']
    attached = [honour_guard()] + attached[1:]
    for a in attached[1:]:
        a['Prerequisite'] = ['Honour Guard']
    u['Attached Units'] = attached
    return blood_angels_transports(u)


def death_company(prereq=None, flat_cost=None):
    equipment = [[opt('bolter', count=4, maximum=-1, default=True), opt('bolt pistol and close combat weapon')],
                 standard('frag grenades')]
    if flat_cost:
        equipment.insert(0, [opt('D3+3 Death Company Space Marines', flat_cost, count=1, maximum=1, default=True)])
    return unit('Death Company', 0, 'WS4•BS4•S4•T4•W1•I4•A2•Ld9•Sv3+', size=4, minimum=4, maximum=6,
                singular='Death Company Space Marine', plural='Death Company Space Marines',
                rules='The Red Thirst; Fearless; Ignore Injury', prereq=prereq, equipment=equipment,
                command=[[opt('Veteran Sergeant', 0, maximum=1, stats=VETERAN_SERGEANT,
                              options=[[opt('bolt pistol and power weapon', 0, maximum=1),
                                        opt('bolt pistol and power fist', 0)]])]],
                mount=[[{'Name': 'jump packs', 'Points': 0.0, 'Special Rules': 'Deep Strike'}]])


def death_company_rhino():
    rhino = base_unit(SM, 'Space Marine Tactical Squad')['Attached Units'][0]
    rhino.update(Points=0.0, Prerequisite=['Death Company without jump packs'],
                 **{'Special Rules': 'Tank; Over-charged Engine'})
    return rhino


# ---------------------------------------------------------------- HQ

def hero(name, stats):
    return with_honour_guard(base_unit(SM, name, Stats=stats))


def chaplain():
    u = base_unit(SM, 'Chaplain', Points=180, Stats='WS5•BS5•S4•T4•W2•I5•A3•Ld9•Sv3+')
    u['Attached Units'] = [death_company(), death_company_rhino()]
    return u


def librarian():
    u = base_unit(SM, 'Librarian')
    u['Magic'] = [fixed('Quickening')]
    return with_honour_guard(u)


def high_priest():
    u = base_unit(SM, 'Commander', Name='Sanguinary High Priest', Points=75, Stats='WS5•BS4•S4•T4•W2•I5•A3•Ld9•Sv3+',
                  Special_Rules='Sanguinius’ Chosen; Independent Character', Upper_Limit=1)
    return with_honour_guard(u)


def special(name, pts, stats, rules, gear, from_points=None, magic=None):
    return with_honour_guard(unit(name, pts, stats, upper=1, rules=rules, from_points=from_points, magic=magic,
                                  equipment=[fixed(g) for g in gear]))


def lemartes():
    gear = ['bolt pistol', 'crozius arcanum', 'frag & krak grenades', 'rosarius', 'purity seals', 'Death Mask']
    return unit('Chaplain Lemartes', 94, 'WS5•BS5•S4•T4•W2•I5•AD3(+3)•Ld10•Sv3+', upper=1,
                rules='Iron-willed; Rigid Discipline',
                equipment=[fixed(g) for g in gear]
                + [[opt('jump pack', 20, maximum=1, prereq='Death Company with jump packs')]],
                attached=[death_company(flat_cost=120), death_company_rhino()])


# ---------------------------------------------------------------- other units

def veteran_assault_squad():
    u = base_unit(SM, 'Assault Squad', Name='Veteran Assault Squad', Points=28, Plural_Name='Veteran Space Marines',
                  Stats=VETERAN)
    find_option(u, 'Sergeant')['Points'] = 28.0
    veteran = find_option(u, 'Veteran Sergeant')
    veteran.update(Points=40.0, Stats=VETERAN_SERGEANT)
    remove_options(u, ['remove jump packs'])
    honours = base_unit(SM, 'Space Marine Veteran Squad')['Equipment'][-1]
    honours[0]['Prerequisite'] = ['Veteran Sergeant']
    u['Equipment'] = [
        standard('bolt pistols'), standard('close combat weapons'), standard('frag grenades'),
        [opt('flamer', 6, maximum=2), opt('meltagun', 10), opt('plasma gun', 6),
         opt('plasma pistol and close combat weapon', 5)],
        toggle('krak grenades', 2),
        toggle('melta bombs', 5),
        honours,
    ]
    return u


def furioso():
    upgrades = base_unit(SM, 'Dreadnought')['Equipment'][-3:]  # extra armour, searchlight, smoke launchers
    return unit('Furioso Dreadnought', 95, 'WS4•BS4•S6(10)•FA12•SA12•RA10•I4•A2(3)', rules='Walker; Tear Attack',
                equipment=[fixed('two Dreadnought close combat weapons'),
                           [opt('built-in storm bolter', 0, count=1, maximum=1, default=True),
                            opt('built-in heavy flamer', 10)],
                           fixed('built-in meltagun')] + upgrades)


def moriar():
    gear = ['two Dreadnought close combat weapons', 'built-in heavy flamer', 'built-in meltagun', 'searchlight',
            'smoke launchers']
    return unit('Moriar the Chosen', 144, 'WS5•BS4•S6(10)•FA12•SA12•RA10•I4•AD6+2', upper=1,
                rules='Walker; Tear Attack; Black Rage; Battle-frenzied; Rampage', equipment=[fixed(g) for g in gear])


def blood_angels_scouts():
    u = base_unit(SM, 'Scout Squad', Name='Blood Angels Scout Squad')
    return remove_options(u, ['sniper rifle', 'heavy bolter', 'autocannon', 'missile launcher'])


def baal_predator():
    u = base_unit(SM, 'Predator Destructor', Name='Baal Predator', Points=110)
    u['Equipment'][:2] = [fixed('twin-linked assault cannon'),
                          [opt('sponson heavy bolters', 10, maximum=1), opt('sponson heavy flamers', 10)]]
    return u


# ---------------------------------------------------------------- armoury

def armoury_items():
    wargear = base_items(SM, 'Wargear')
    terminator = base_items(SM, 'Terminator Wargear')
    gone = ('holy relic', 'sacred standard', 'Narthecium')
    for cat in (wargear, terminator):
        cat['Items'] = [i for i in cat['Items'] if i['Name'] not in gone]
        for i in cat['Items']:
            if i.get('Prerequisite') == ['Apothecaries']:
                i['Prerequisite'] = ['Sanguinary Priests']
    terminator_ok = [
        ('Death Mask', 10, 'Independent Characters', None),
        ('Grail', 25, '0-1; Sanguinary High Priest, Standard Bearer or Chaplain', None),
    ]
    wargear['Items'] += items('Wargear', terminator_ok + [
        ('Exsanguinator', 30, 'Sanguinary Priests', None),
        ('Holy Shroud', 45, 'Standard Bearer', None),
    ])['Items']
    terminator['Items'] += items('Terminator Wargear', terminator_ok)['Items']
    wargear['Items'].sort(key=lambda i: i['Name'].lower())
    terminator['Items'][1:] = sorted(terminator['Items'][1:], key=lambda i: i['Name'].lower())  # armour first
    return [wargear, terminator]


# ---------------------------------------------------------------- army list

def organisation():
    hq = [
        hero('Force Commander', 'WS5•BS5•S4•T4•W3•I5•A3•Ld9•Sv3+'),
        hero('Commander', 'WS5•BS5•S4•T4•W2•I5•A3•Ld9•Sv3+'),
        hero('Leader', 'WS4•BS4•S4•T4•W1•I4•A2•Ld9•Sv3+'),
        librarian(),
        chaplain(),
        high_priest(),
        special('Commander Dante', 205, 'WS6•BS5•S4•T4•W3•I5•A4•Ld10•Sv2+',
                'Inferno Pistol; Death Mask of Sanguinius; Independent Character',
                ['power weapon', 'Inferno pistol', 'frag & krak grenades', 'Terminator honours', 'jump pack',
                 'artificer armour', 'purity seals', 'Iron Halo', 'Death Mask of Sanguinius'], from_points=2000),
        special('Brother Corbulo', 156, 'WS5•BS4•S4•T4•W2•I5•A3•Ld9•Sv3+',
                'Sanguinius’ Chosen; The Red Grail; Independent Character',
                ['bolt pistol', 'close combat weapon', 'Exsanguinator', 'Reductor', 'frag & krak grenades',
                 'Red Grail']),
        lemartes(),
        special('Chief Librarian Mephiston', 217, 'WS6•BS5•S4•T5•W3•I5•A4•Ld10•Sv2+',
                'Transfixing Glare; Blood Fever; Independent Character',
                ['master-crafted plasma pistol', 'force sword', 'frag & krak grenades', 'Terminator honours',
                 'artificer armour', 'psychic hood'], magic=[fixed('Quickening'), fixed('Smite')]),
        special('Brother Captain Tycho', 109, 'WS5•BS5•S4•T4•W2•I5•A3•Ld9•Sv2+',
                'Digi-lasers; Embittered; Hates Orks; Independent Character',
                ['combi-weapon (bolter-meltagun)', 'bolt pistol', 'frag & krak grenades', 'digi-lasers',
                 'artificer armour', 'bionics', 'purity seals']),
    ]
    elites = [
        veteran_assault_squad(),
        furioso(),
        sm('Terminator Squad'),
        sm('Terminator Assault Squad'),
        sm('Space Marine Veteran Squad'),
        moriar(),
    ]
    troops = [
        blood_angels_scouts(),
        remove_options(sm('Space Marine Tactical Squad'), ['Veteran Sergeant Lysander']),
        sm('Scout Squad', Upper_Limit=1),
    ]
    fast = [sm(name) for name in ('Assault Squad', 'Bike Squadron', 'Scout Bike Squadron', 'Land Speeder Squadron',
                                  'Land Speeder Tornado', 'Land Speeder Typhoon', 'Attack Bike Squadron')]
    heavy = [baal_predator()] + [sm(name) for name in ('Devastator Squad', 'Whirlwind', 'Predator Annihilator',
                                                       'Predator Destructor', 'Dreadnought', 'Land Raider',
                                                       'Vindicator')]
    priests = unit_limit('Sanguinary High Priest', ['Sanguinary High Priest', 'Brother Corbulo'])
    return standard_foc(hq, elites, troops, fast, heavy, hq_limits=[priests])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = sys.argv[1]
    SM = load(os.path.join(os.path.dirname(os.path.abspath(out)), 'Space Marines.qmtemplate'))
    write(template('Blood Angels', 'WH40K3', 20261125, organisation(), armoury_items()), out)
