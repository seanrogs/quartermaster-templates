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
  - Prerequisite is a list of conditions. A condition naming a Trait variant
    ('Wych Cult', or 'not Wych Cult') is matched against the army's chosen
    variant; anything else is a free-text note. Pass a string for one
    condition or a list for several.
  - Quartermaster 6.7 fields: Traits (army-wide variants such as Chapter or
    Clan), Unit Limits (shared 0-1 caps across several units in a section),
    Limit From Points (unit only allowed from N points) and Link Requirement
    (unit needs one of the named units in the army).
  - Reals are written the way Quartermaster 6.7 saves them: whole numbers
    bare (<real>20</real>, <real>0</real>), fractions as-is (<real>-0.34</real>).
"""
import plistlib
import re
import sys

GLYPH_STAR = 'glyphicons_048_star'


def _prereq(value):
    return [value] if isinstance(value, str) else list(value)


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
        d['Prerequisite'] = _prereq(prereq)
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
         magic_items=None, attached=None, prereq=None, from_points=None, requires=None):
    """A unit (or an attached unit). Points are per model.

    from_points: only allowed in armies of at least this many points (Limit From Points).
    requires: list of unit names, one of which must be in the army (Link Requirement).
    """
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
        u['Prerequisite'] = _prereq(prereq)
    if from_points is not None:
        u['Limit From Points'] = float(from_points)
    if requires:
        u['Link Requirement'] = {'Names': list(requires)}
    return u


def unit_limit(name, units, upper=1):
    """A cap shared by several units in one section, e.g. 'Archon or Wych Archite'."""
    return {'Name': name, 'Units': list(units), 'Upper Limit': upper}


def org(cls, lo, hi, units, limits=None):
    """One force organisation section, with optional unit_limit() entries."""
    o = {'Class': cls, 'Lower Limit': float(lo), 'Upper Limit': float(hi), 'Units': units}
    if limits:
        o['Unit Limits'] = limits
    return o


def standard_foc(hq, elites, troops, fast, heavy, hq_limits=None, elites_limits=None, troops_limits=None,
                 fast_limits=None, heavy_limits=None):
    """WH40K 3rd edition standard missions chart: 1-2 HQ, 0-3 Elites, 2-6 Troops, 0-3 FA, 0-3 HS."""
    return [org('HQ', 1, 2, hq, hq_limits), org('Elites', 0, 3, elites, elites_limits),
            org('Troops', 2, 6, troops, troops_limits), org('Fast Attack', 0, 3, fast, fast_limits),
            org('Heavy Support', 0, 3, heavy, heavy_limits)]


def trait(name, variants):
    """An army-wide choice such as Chapter or Clan. Variants are names, or (name, base, trim) colour triples."""
    out = []
    for v in variants:
        if isinstance(v, str):
            out.append({'Name': v})
        else:
            vname, base, trim = v
            out.append({'Name': vname, 'Base': base, 'Trim': trim})
    return {'Name': name, 'Variants': out}


def items(category, entries, icon=GLYPH_STAR):
    """An Items category. entries: (name, points, prerequisite or None, stats or None[, multiple]).

    multiple=True lets a model take the item more than once (e.g. drones, Chaos Hounds).
    """
    out = []
    for entry in entries:
        name, pts, prereq, stats = entry[:4]
        d = {'Category': category, 'Name': name, 'Points': float(pts)}
        if len(entry) > 4 and entry[4]:
            d['Multiple'] = True
        if prereq:
            d['Prerequisite'] = _prereq(prereq)
        if stats:
            d['Stats'] = stats
        out.append(d)
    return {'Category': category, 'Icon': icon, 'Items': out}


def template(name, system, version, organisation, item_categories=None, traits=None):
    t = {'Army List Name': name, 'System': system, 'Version': version, 'Organisation': organisation}
    if item_categories:
        t['Items'] = item_categories
    if traits:
        t['Traits'] = traits
    return t


_WHOLE_REAL = re.compile(rb'<real>(-?\d+)\.0</real>')


def write(tmpl, path):
    """Write the template as Quartermaster 6.7 saves it (sorted keys, bare whole-number reals)."""
    data = _WHOLE_REAL.sub(rb'<real>\1</real>', plistlib.dumps(tmpl, sort_keys=True))
    plistlib.loads(data)  # validate
    with open(path, 'wb') as f:
        f.write(data)


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
