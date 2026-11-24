"""WH40K3 Dark Angels, from the 3rd edition Codex: Dark Angels (1999), built on Space Marines.

Usage: python3 -B factions/wh40k3_dark_angels.py "WH40K3/Dark Angels.qmtemplate"

The codex is a supplement: most entries say "see Codex: Space Marines", so those units
are copied from WH40K3/Space Marines.qmtemplate (read from the output file's folder)
and changed where the codex changes them. Re-run after editing Space Marines to pick
up its changes.

A 'Sub-faction' Trait holds the Deathwing and Ravenwing armies (colours as in the
Space Marines Chapter trait). Units they ban carry 'not Deathwing' / 'not Ravenwing';
units that change slot in them (Deathwing Terminators in any slot, Ravenwing bikes as
Troops, attack bikes as Heavy Support) are duplicated into that slot with the variant
as a prerequisite.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from qmtemplate import (base_items, base_unit, find_option, fixed, items, load, opt,  # noqa: E402
                        remove_options, standard, standard_foc, template, trait, unit, write)

DW = 'Deathwing'
RW = 'Ravenwing'
STANDARD = ['not Deathwing', 'not Ravenwing']
STUBBORN = 'Stubborn'
CHARACTER = 'Independent Character; Stubborn'

SM = None  # the parent Space Marines template, loaded in main


# ---------------------------------------------------------------- helpers

def stubborn_veterans(u):
    """Dark Angels Veteran Sergeants may be inducted into the Deathwing: stubborn at +5 pts."""
    for group in u.get('Command', []):
        for o in group:
            if o['Name'].startswith('Veteran') and 'Naaman' not in o['Name']:
                o.setdefault('Options', []).append([opt('stubborn', 5, maximum=1)])
    return u


def sm_character_groups(magic='Wargear'):
    """Apothecary, Techmarine and Standard Bearer upgrades from the Space Marines Command Squad."""
    groups = base_unit(SM, 'Force Commander')['Attached Units'][0]['Command'][1:]
    for group in groups:
        for o in group:
            o['Magic Items'][0]['Name'] = magic
    return groups


def command_squad():
    """A Dark Angels Tactical squad with the Command squad character upgrades."""
    u = base_unit(SM, 'Space Marine Tactical Squad', Name='Command Squad', Plural_Name='Command Squad Bodyguard',
                  Attached_Units=None)
    remove_options(u, ['Veteran Sergeant Lysander'])
    u['Command'] += sm_character_groups()
    return stubborn_veterans(u)


def deathwing_terminators(name='Deathwing Terminator Squad', prereq=None):
    u = base_unit(SM, 'Terminator Squad', Name=name, Points=52, Plural_Name='Deathwing Terminators',
                  Special_Rules='Deep Strike; Stubborn')
    sergeant = find_option(u, 'Terminator Sergeant')
    sergeant.update(Name='Deathwing Terminator Sergeant', Points=52.0)
    fists = u['Equipment'][0]
    fists += [opt('pair of lightning claws'), opt('thunder hammer and storm shield')]
    if prereq:
        u['Prerequisite'] = [prereq] if isinstance(prereq, str) else list(prereq)
    return u


def deathwing_command(prereq='Master of the Deathwing'):
    u = deathwing_terminators('Deathwing Command Squad', prereq)
    u['Command'] += sm_character_groups('Terminator Wargear')
    return u


def ravenwing_bikes(name='Ravenwing Bike Squadron', prereq=None):
    u = base_unit(SM, 'Bike Squadron', Name=name, Points=45, Plural_Name='Ravenwing Bikers', Special_Rules='Ravenwing')
    sergeant = find_option(u, 'Sergeant')
    sergeant.update(Name='Ravenwing Sergeant', Points=45.0)
    veteran = find_option(u, 'Veteran Sergeant')
    veteran.update(Points=60.0, **{'Magic Items': [{'Items': [], 'Limit': 100.0, 'Name': 'Wargear'}]})
    for o in (sergeant, veteran):
        find_option(o, 'close combat weapon')['Points'] = 0.0  # swaps the bolt pistol
    u['Equipment'][0] = [opt('bolt pistol', count=u['Size'], maximum=-1, default=True), opt('close combat weapon')]
    bike = u['Attached Units'][0]
    bike.update(Points=75.0, **{'Special Rules': 'Ravenwing', 'Upper Limit': 1})
    bike['Equipment'] = [standard('twin-linked bolters'), standard('pintle-mounted multi-melta'),
                         standard('bolt pistol')]
    if prereq:
        u['Prerequisite'] = [prereq] if isinstance(prereq, str) else list(prereq)
    return stubborn_veterans(u)


def ravenwing_bike_command():
    u = ravenwing_bikes('Ravenwing Command Squadron')
    del u['Attached Units']  # no units attached to an attached unit
    u['Command'] += sm_character_groups()
    return u


def ravenwing_speeders(prereq=None):
    u = base_unit(SM, 'Land Speeder Squadron', Name='Ravenwing Land Speeder Squadron', Points=60,
                  Special_Rules='Fast, Skimmer; Ravenwing')
    u['Equipment'] = [standard('heavy bolters'), [opt('assault cannon', 25, maximum=-1)]]
    if prereq:
        u['Prerequisite'] = [prereq] if isinstance(prereq, str) else list(prereq)
    return u


def ravenwing_attack_bikes(prereq):
    u = base_unit(SM, 'Attack Bike Squadron', Name='Ravenwing Attack Bike Squadron', Points=75,
                  Special_Rules='Ravenwing', Prerequisite=[prereq] if isinstance(prereq, str) else list(prereq))
    u['Equipment'] = [standard('twin-linked bolters'), standard('pintle-mounted multi-meltas'), standard('bolt pistols')]
    return u


def with_command(u, extra=()):
    """Swap the Space Marines Command Squad for the Dark Angels one, keeping its transports."""
    attached = u.get('Attached Units', [])
    if attached and attached[0]['Name'] == 'Command Squad':
        attached[0] = command_squad()
    u['Attached Units'] = attached[:1] + list(extra) + attached[1:]
    return u


def sm_transports():
    return base_unit(SM, 'Force Commander')['Attached Units'][1:]


# ---------------------------------------------------------------- HQ

def hero(sm_name, name, pts, stats, master):
    u = base_unit(SM, sm_name, Name=name, Points=pts, Stats=stats, Special_Rules=CHARACTER,
                  Prerequisite=['not Ravenwing'] if master else STANDARD)
    if not master:
        return with_command(u)
    u['Equipment'].append([opt('Master of the Deathwing', 0, maximum=1,
                               prereq=['0-1', 'Terminator armour', 'required in a Deathwing army'])])
    return with_command(u, [deathwing_command()])


def librarian():
    u = base_unit(SM, 'Librarian', Points=85, Stats='WS5•BS5•S4•T4•W2•I5•A4•Ld9•Sv3+', Special_Rules=CHARACTER)
    u['Magic'] = fixed_group('Weaken Resolve')
    return with_command(u)


def fixed_group(name):
    return [fixed(name)]


def interrogator_chaplain():
    u = base_unit(SM, 'Chaplain', Name='Interrogator-Chaplain', Points=90, Stats='WS5•BS5•S4•T4•W2•I5•A4•Ld9•Sv3+',
                  Special_Rules=CHARACTER)
    return with_command(u)


def master_of_the_ravenwing():
    return unit('Master of the Ravenwing', 255, 'FA10•SA10•RA10•BS5', upper=1,
                prereq=['not Deathwing', 'required in a Ravenwing army'],
                rules='Fast, Skimmer; Ravenwing; Shield of Night; All-Seeing Eye; The Raven Sword',
                equipment=[fixed('twin-linked heavy bolter'), fixed('twin-linked assault cannon')],
                attached=[ravenwing_bike_command(), ravenwing_speeders()])


def azrael():
    return unit('Azrael', 213, 'WS5•BS5•S4•T4•W4•I5•A4•Ld10•Sv3+', upper=1, prereq=STANDARD, from_points=2000,
                rules='No Retreat; No Surrender; Independent Character; Stubborn',
                equipment=[fixed('Sword of Secrets'), fixed('Lion Helm'), fixed('combi-weapon (bolter-plasma gun)'),
                           fixed('frag grenades'), fixed('krak grenades')],
                attached=[command_squad(), deathwing_command(prereq=None), ravenwing_bike_command()] + sm_transports())


def asmodai():
    return unit('Asmodai', 110, 'WS5•BS5•S4•T4•W2•I5•A4•Ld9•Sv3+', upper=1,
                rules='Master Interrogator; Fearful Reputation; Independent Character; Stubborn',
                equipment=[fixed('power sword'), fixed('rosarius'), fixed('Blades of Reason')])


def ezekiel():
    return unit('Ezekiel', 225, 'WS5•BS5•S4•T4•W3•I5•A4•Ld9•Sv3+', upper=1,
                rules='Know Thine Enemy; Independent Character; Stubborn',
                equipment=[fixed('Book of Salvation'), fixed('force sword'), fixed('psychic hood'), fixed('bionics'),
                           fixed('bolt pistol'), fixed('frag grenades'), fixed('krak grenades')],
                magic=fixed_group('Weaken Resolve'),
                attached=[command_squad()] + sm_transports())


def naaman():
    gear = ['master-crafted bolt pistol', 'master-crafted chainsword', 'frag grenades', 'melta bombs', 'auspex',
            'teleport homer']
    return opt('Veteran Sergeant Naaman', 80, additional=True, stats='WS4•BS4•S4•T4•W2•I5•A2•Ld9•Sv4+', prereq='0-1',
               rules='Evade Detection; Silent Death; Brush Aside Blow; Stubborn', options=[fixed(g) for g in gear])


# ---------------------------------------------------------------- armoury

def armoury_items():
    wargear = base_items(SM, 'Wargear')
    terminator = base_items(SM, 'Terminator Wargear')
    for cat in (wargear, terminator):
        cat['Items'] = [i for i in cat['Items'] if i['Name'] not in ('holy relic', 'sacred standard')]
    for i in wargear['Items']:
        if i['Name'] == 'Terminator honours':
            i['Prerequisite'] = ['not Masters, Grand Masters, Librarians or Chaplains']
    relics = [
        ('Blades of Reason', 5, '0-1; Chaplains', None),
        ('Book of Salvation', 40, '0-1; Librarians', None),
        ('Cup of Retribution', 40, '0-1; Independent Characters', None),
        ('Lion Helm', 35, '0-1; Grand Masters', None),
        ('Sword of Secrets', 40, '0-1; Grand Masters', None),
    ]
    standards = [
        ('Standard of Devastation', 35, '0-1; Standard Bearer', None),
        ('Standard of Fortitude', 30, '0-1; Standard Bearer', None),
        ('Standard of Retribution', 40, '0-1; Standard Bearer', None),
    ]
    wargear['Items'] += items('Wargear', relics + standards)['Items']
    terminator['Items'] += items('Terminator Wargear', relics)['Items']
    wargear['Items'].sort(key=lambda i: i['Name'].lower())
    terminator['Items'][1:] = sorted(terminator['Items'][1:], key=lambda i: i['Name'].lower())  # armour first
    return [wargear, terminator]


# ---------------------------------------------------------------- army list

def organisation():
    hq = [
        hero('Leader', 'Leader', 50, 'WS4•BS4•S4•T4•W1•I4•A3•Ld9•Sv3+', master=False),
        hero('Commander', 'Master', 65, 'WS5•BS5•S4•T4•W2•I5•A4•Ld9•Sv3+', master=True),
        hero('Force Commander', 'Grand Master', 80, 'WS5•BS5•S4•T4•W3•I5•A4•Ld10•Sv3+', master=True),
        librarian(),
        interrogator_chaplain(),
        master_of_the_ravenwing(),
        azrael(),
        asmodai(),
        ezekiel(),
    ]
    elites = [
        deathwing_terminators(prereq='not Ravenwing'),
        base_unit(SM, 'Dreadnought', Prerequisite=['not Ravenwing']),
    ]
    tactical = stubborn_veterans(remove_options(base_unit(SM, 'Space Marine Tactical Squad', Prerequisite=STANDARD),
                                                ['Veteran Sergeant Lysander']))
    scouts = stubborn_veterans(base_unit(SM, 'Scout Squad', Prerequisite=STANDARD))
    scouts['Command'][0].append(naaman())
    troops = [tactical, scouts, deathwing_terminators(prereq=DW), ravenwing_bikes(prereq=RW)]
    fast = [
        ravenwing_bikes(prereq=STANDARD),
        ravenwing_speeders(prereq='not Deathwing'),
        ravenwing_attack_bikes(STANDARD),
        stubborn_veterans(base_unit(SM, 'Assault Squad', Prerequisite=STANDARD)),
        stubborn_veterans(base_unit(SM, 'Scout Bike Squadron', Prerequisite=STANDARD)),
        deathwing_terminators(prereq=DW),
    ]
    heavy = [stubborn_veterans(base_unit(SM, 'Devastator Squad', Prerequisite=STANDARD))]
    heavy += [base_unit(SM, name, Prerequisite=STANDARD)
              for name in ('Whirlwind', 'Predator Annihilator', 'Predator Destructor')]
    heavy += [
        base_unit(SM, 'Land Raider', Prerequisite=['not Ravenwing']),
        base_unit(SM, 'Vindicator', Prerequisite=STANDARD),
        deathwing_terminators(prereq=DW),
        ravenwing_attack_bikes(RW),
    ]
    return standard_foc(hq, elites, troops, fast, heavy)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = sys.argv[1]
    SM = load(os.path.join(os.path.dirname(os.path.abspath(out)), 'Space Marines.qmtemplate'))
    write(template('Dark Angels', 'WH40K3', 20261125, organisation(), armoury_items(),
                   traits=[trait('Sub-faction', [(DW, '#E6DCC0', '#9E1B1B'), (RW, '#141A16', '#E8DDB5')])]),
          out)
