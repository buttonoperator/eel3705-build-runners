# -*- coding: utf-8 -*-
import io, os, re, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')

t = io.open('template.html', encoding='utf-8').read()
for ph, f in (('<!--SVG-->', 'bb.svg'), ('<!--FLOW-->', 'flow.svg'), ('<!--CHIPS-->', 'chips.svg')):
    if t.count(ph) != 1:
        sys.exit('placeholder %s appears %d times' % (ph, t.count(ph)))
    t = t.replace(ph, io.open(f, encoding='utf-8').read())
io.open(OUT, 'w', encoding='utf-8').write(t)

err = []

# --- steps ---
steps_src = t[t.index('var STEPS = ['):t.index('// Pins each step touches')]
chunks = re.split(r'\n \{g:', steps_src)[1:]
nsteps = len(chunks)
# how many wire rows each step lists
wrows = [len(re.findall(r'\["[^"]*","[^"]*"\]', c)) for c in chunks]

# --- pin map references resolve ---
pin_ids = set('%s.%s' % m for m in re.findall(r'id="p-([A-Z0-9]+)-(\d+)"', t))
pkg = dict(re.findall(r'(\w+):(\d+)', re.search(r'var PKGPINS = \{([^}]*)\}', t).group(1)))
refs = set()
for k in re.findall(r'"([A-Z0-9]+)\.([0-9*]+)"',
                    re.search(r'var PINS = \[(.*?)\n\];', t, re.S).group(1)):
    if k[1] == '*':
        refs |= set('%s.%d' % (k[0], i) for i in range(1, int(pkg[k[0]]) + 1))
    else:
        refs.add('%s.%s' % k)
if refs - pin_ids:
    err.append('pin refs missing: %s' % sorted(refs - pin_ids))

# --- breadboard step stamps ---
stamps = {}
for v in re.findall(r'data-s="(\d+)"', t):
    stamps[int(v)] = stamps.get(int(v), 0) + 1
bad = [k for k in stamps if k < 0 or k >= nsteps]
if bad:
    err.append('data-s out of range: %s' % sorted(bad))
# every step that lists connections must draw something, and vice versa
for i in range(nsteps):
    has_rows, has_art = wrows[i] > 0, stamps.get(i, 0) > 0
    if has_rows and not has_art:
        err.append('step %d lists %d connections but draws no wires' % (i, wrows[i]))
# steps that draw wires without listing rows are fine (resistors, LED, switch commons)
silent = sorted(i for i in stamps if wrows[i] == 0)

# --- unique ids ---
for i in ('bb', 'cm', 'fl', 'ppin', 'pbb', 'ball', 'bbnote', 'panes',
          'zin', 'zout', 'zfit', 'zlab', 'undo', 'dia',
          'pzin', 'pzout', 'pzfit', 'pzlab',
          'rcount', 'rtitle', 'rwhere', 'cnt', 'cdn', 'cup', 'qbits', 'rv', 'rvlab', 'run',
          'lsum', 'lread', 'cled', 'ctext', 'lnote', 'seg7',
          'outs', 'goal', 'goalt'):
    if t.count('id="%s"' % i) != 1:
        err.append('id="%s" appears %d times' % (i, t.count('id="%s"' % i)))

# --- no leftovers from the HOP 2 page this one was adapted from ---
for dead in ('id="opa"', 'id="opb"', 'id="bitsa"', 'id="tled"', 'hop2.', '74HC283', 'SW1'):
    if dead in t:
        err.append('stale HOP 2 reference: %s' % dead)

# --- step count agrees with the breadboard generator ---
import importlib.util
gsrc = io.open('gen.py', encoding='utf-8').read()
m = re.search(r'^NSTEPS = (\d+)', gsrc, re.M)
if not m or int(m.group(1)) != nsteps:
    err.append('gen.py NSTEPS %s but template has %d steps' % (m.group(1) if m else '?', nsteps))
if len(re.findall(r'^ \[', t[t.index('var PINS = ['):t.index('var PKGPINS')], re.M)) == 0:
    err.append('PINS block not found')
pins_block = t[t.index('var PINS = ['):t.index('var PKGPINS')]
npins_rows = pins_block.count('[') - 1
if npins_rows != nsteps:
    err.append('PINS has %d rows for %d steps' % (npins_rows, nsteps))

# --- no leftovers from the old group-level scheme ---
for ref in ('U1', 'U2', 'U3', 'DS1'):
    for pre in ('ro-', 'rotag-', 'rol1-', 'rol2-'):
        if t.count('id="%s%s"' % (pre, ref)) != 1:
            err.append('missing readout id %s%s' % (pre, ref))

if 'window.scrollTo' in t:
    err.append('render still jumps the page to the top')

for dead in ('BBG', 'BBALL', 'BBNAME', 'n-pwr', 'd-pwr',
             'setView', 'setFull', 'tfull', 'diabar', 'panes.split', 'lgrid'):
    if dead in t:
        err.append('stale reference: %s' % dead)

print('steps %d | pin refs %d | stamped steps %d | svg elements %d'
      % (nsteps, len(refs), len(stamps), sum(stamps.values())))
print('steps drawing wires with no listed rows:', silent)
print('bytes', len(t))
print('ERRORS:', err if err else 'none')
if err:
    sys.exit(1)
