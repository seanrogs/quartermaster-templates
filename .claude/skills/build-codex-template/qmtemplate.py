"""Helpers for building Quartermaster .qmtemplate army lists from Python data.

Faction scripts in factions/ import this module, describe their units with the
builders below, and call write(). Run `python3 qmtemplate.py outline <file>` to
print a readable outline of any existing template for comparison.

Conventions (as used by the WH40K3 templates):
  - A group is a list of option dicts. Options in one group are alternatives;
    the first option's Maximum caps the whole group.
  - Maximum > 0 is a cap per unit; Maximum < 0 is per model (-1 = one each,
    -2 = two each, -0.34 = one per three models).
  - An option with no Count/Maximum is a unit-wide upgrade paid per model.
  - Default + Equipped marks standard gear that is always carried.
  - Prerequisite is a free-text note (one string, parts joined with '; ').
  - Whole numbers are written as reals with a trailing .0 (e.g. 20.0), which
    is what plistlib produces and what newer Quartermaster versions write.
"""
import plistlib
import sys

GLYPH_STAR = 'glyphicons_048_star'


def opt(name, pts=0, count=0, maximum=None, default=False, equipped=False, stats=None,
        prereq=None, options=None, rules=None, additional=False, magic_items=None):
    """One choice inside a group (equipment, command model, mount, ...)."""
    d = {'Name': name, 'Points': float(pts)}
    if equipped:
        d['Default'] = True
        d['Equipped'] = True
    else:
        if count is not None:
            d['Count'] = count
        if default:
            d['Default'] = True
        if maximum is not None:
            d['Maximum'] = float(maximum)
    if additional:
        d['Additional'] = True
    if stats:
        d['Stats'] = stats
    if prereq:
        d['Prerequisite'] = [prereq]
    if rules:
        d['Special Rules'] = rules
    if options:
        d['Options'] = options
    if magic_items:
        d['Magic Items'] = magic_items
    return d


def fixed(name):
    """Group holding one piece of fixed wargear (special characters)."""
    return [opt(name, 0, count=1, maximum=1, default=True)]


def standard(name):
    """Group holding standard gear the whole unit always carries."""
    return [opt(name, 0, equipped=True)]


def toggle(name, pts):
    """Group holding a unit-wide upgrade paid per model."""
    return [{'Name': name, 'Points': float(pts)}]


def armoury(categories, limit=100):
    """Magic Items entry giving access to Items categories, e.g. 'Wargear, Arcane Wargear'."""
    return [{'Items': [], 'Limit': float(limit), 'Name': categories}]


def unit(name, pts, stats, size=1, minimum=None, maximum=None, rules=None, upper=None, lower=None,
         plural=None, singular=None, equipment=None, command=None, mount=None, magic=None,
         magic_items=None, attached=None, prereq=None):
    """A unit (or an attached unit). Points are per model."""
    minimum = size if minimum is None else minimum
    maximum = size if maximum is None else maximum
    u = {'Name': name, 'Points': float(pts), 'Size': size, 'Minimum Size': minimum, 'Maximum Size': maximum}
    for key, value in (('Stats', stats), ('Special Rules', rules), ('Plural Name', plural),
                       ('Singular Name', singular), ('Equipment', equipment), ('Command', command),
                       ('Mount', mount), ('Magic', magic), ('Magic Items', magic_items),
                       ('Attached Units', attached)):
        if value:
            u[key] = value
    if upper is not None:
        u['Upper Limit'] = upper
    if lower is not None:
        u['Lower Limit'] = lower
    if prereq:
        u['Prerequisite'] = [prereq]
    return u


def org(cls, lo, hi, units):
    """One force organisation section."""
    return {'Class': cls, 'Lower Limit': float(lo), 'Upper Limit': float(hi), 'Units': units}


def standard_foc(hq, elites, troops, fast, heavy):
    """WH40K 3rd edition standard missions chart: 1-2 HQ, 0-3 Elites, 2-6 Troops, 0-3 FA, 0-3 HS."""
    return [org('HQ', 1, 2, hq), org('Elites', 0, 3, elites), org('Troops', 2, 6, troops),
            org('Fast Attack', 0, 3, fast), org('Heavy Support', 0, 3, heavy)]


def items(category, entries, icon=GLYPH_STAR):
    """An Items category. entries: (name, points, prerequisite or None, stats or None)."""
    out = []
    for name, pts, prereq, stats in entries:
        d = {'Category': category, 'Name': name, 'Points': float(pts)}
        if prereq:
            d['Prerequisite'] = [prereq]
        if stats:
            d['Stats'] = stats
        out.append(d)
    return {'Category': category, 'Icon': icon, 'Items': out}


def template(name, system, version, organisation, item_categories=None):
    t = {'Army List Name': name, 'System': system, 'Version': version, 'Organisation': organisation}
    if item_categories:
        t['Items'] = item_categories
    return t


def write(tmpl, path):
    with open(path, 'wb') as f:
        plistlib.dump(tmpl, f, sort_keys=True)
    with open(path, 'rb') as f:
        plistlib.load(f)  # validate


# ---------------------------------------------------------------- outline viewer

def _fmt(d):
    return ' '.join(f'{k}={v!r}' for k, v in d.items() if not isinstance(v, (list, dict)) or k == 'Prerequisite')


def _opts(lst, ind):
    for o in lst:
        if isinstance(o, list):
            print(ind + '[subgroup]')
            _opts(o, ind + '  ')
            continue
        print(ind + '- ' + _fmt(o))
        if 'Magic Items' in o:
            for m in o['Magic Items']:
                print(ind + '  Magic Items: ' + _fmt(m))
        for k in ('Options', 'Items'):
            if k in o:
                print(ind + '  ' + k + ':')
                _opts(o[k], ind + '    ')


def _unit(u, ind):
    print(ind + '* ' + _fmt(u))
    for k in ('Command', 'Equipment', 'Magic', 'Mount'):
        if k in u:
            print(ind + '  ' + k + ':')
            for grp in u[k]:
                print(ind + '    [group]')
                _opts(grp if isinstance(grp, list) else [grp], ind + '      ')
    for m in u.get('Magic Items', []):
        print(ind + '  Magic Items: ' + _fmt(m))
    for a in u.get('Attached Units', []):
        print(ind + '  ATTACHED:')
        _unit(a, ind + '    ')


def outline(path):
    with open(path, 'rb') as f:
        d = plistlib.load(f)
    print(_fmt(d))
    for section in d['Organisation']:
        print('== ' + _fmt(section))
        for u in section['Units']:
            _unit(u, '  ')
    for cat in d.get('Items', []):
        print('## ITEMS ' + _fmt(cat))
        _opts(cat['Items'], '  ')


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'outline':
        outline(sys.argv[2])
    else:
        sys.exit('usage: python3 qmtemplate.py outline <file.qmtemplate>')
