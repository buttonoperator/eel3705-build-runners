# -*- coding: utf-8 -*-
"""Breadboard placement diagram for the HOP 3 BCD counter.

One 830-point board, which is the only breadboard in the kit. Every wire, resistor and
capacitor lead lands in a real, free hole, and every element carries the step that places it
(data-s) and the net it carries (data-net).

Before writing bb.svg the script rebuilds the circuit from the drawing alone (terminal strips,
rails, and the parts plugged into them) and compares the result against NETLIST below. If any
pin ends up on the wrong net, or two leads share a hole, the build stops.
"""
import io
import sys

P = 22.0
MARGIN_X = 40.0
NCOL = 63
ROW = {'R+T': 0.0, 'R-T': 1.0, 'J': 4.4, 'I': 5.4, 'H': 6.4, 'G': 7.4, 'F': 8.4,
       'E': 10.8, 'D': 11.8, 'C': 12.8, 'B': 13.8, 'A': 14.8,
       'R-B': 18.2, 'R+B': 19.2}
UPPER = 'FGHIJ'
LOWER = 'ABCDE'
RAILS = ('R+T', 'R-T', 'R-B', 'R+B')
BOARD_H = 20.2


def X(col):
    return MARGIN_X + (col - 1) * P


def Yr(row):
    return ROW[row] * P


def Yu(u):
    return u * P


out = []


def e(s):
    out.append(s)


# ------------------------------------------------------------------ step indices
# Must match the order of STEPS in template.html. build.py checks the count.
S_SEAT_U1, S_SEAT_U2, S_SEAT_U3, S_SEAT_DS1 = 0, 1, 2, 3
S_MODULE, S_POWER, S_MEASURE = 4, 5, 6
S_RESET555, S_RESET90, S_STRAP4511 = 7, 8, 9
S_RA, S_CHAIN_UP, S_CHAIN_TURN, S_POT, S_LOOP, S_CAP, S_CLKLED = 10, 11, 12, 13, 14, 15, 16
S_CLK, S_LINK = 17, 18
S_QBUS, S_PULLUP = 19, 20
S_SEGRES, S_SEGIN, S_SEGOUT, S_COM, S_LAMP = 21, 22, 23, 24, 25
S_VERIFY = 26
NSTEPS = 27


# ------------------------------------------------------------------ parts
class Part:
    """A DIP-style part straddling the channel, notch left, pin 1 lower left."""
    def __init__(self, ref, col0, npins, label, names, rows=('E', 'F'), short=None):
        self.ref, self.col0, self.npins = ref, col0, npins
        self.label, self.names, self.rows = label, names, rows
        self.short = short or label

    def hole(self, pin):
        half = self.npins // 2
        if pin <= half:
            return (self.col0 + pin - 1, self.rows[0])
        return (self.col0 + (self.npins - pin), self.rows[1])


N555 = {1: 'GND', 2: 'TRIG', 3: 'OUT', 4: 'RST', 5: 'CTRL', 6: 'THR', 7: 'DIS', 8: 'VCC'}
N90 = {1: 'CKB', 2: 'R0', 3: 'R0', 4: 'NC', 5: 'VCC', 6: 'R9', 7: 'R9',
       8: 'QC', 9: 'QB', 10: 'GND', 11: 'QD', 12: 'QA', 13: 'NC', 14: 'CKA'}
N4511 = {1: 'B', 2: 'C', 3: 'LT', 4: 'BL', 5: 'LE', 6: 'D', 7: 'A', 8: 'VSS',
         9: 'e', 10: 'd', 11: 'c', 12: 'b', 13: 'a', 14: 'g', 15: 'f', 16: 'VDD'}
NDISP = {1: 'e', 2: 'd', 3: 'CC', 4: 'c', 5: 'dp', 6: 'b', 7: 'a', 8: 'CC', 9: 'f', 10: 'g'}

U1 = Part('U1', 18, 8, 'U1 NE555', N555)
U2 = Part('U2', 25, 14, 'U2 74LS90', N90)
U3 = Part('U3', 36, 16, 'U3 CD4511', N4511)
# 0.39 in display, pin rows 0.6 in apart: on a breadboard that is rows D and H.
DS1 = Part('DS1', 58, 10, 'DS1', NDISP, rows=('D', 'H'))
PARTS = [U1, U2, U3, DS1]

RED, BLK, ORA = '#d1495b', '#3d4451', '#e08b2a'
BLU, GRN, PUR, SEG = '#2f7fd6', '#2f9e5e', '#8b5cf6', '#c2410c'
TIM = '#a0522d'

# ------------------------------------------------------------------ element model
# Every element: kind, list of (terminal name, hole), drawing args, group, step, net.
ELEMS = []
holes_used = {}


def claim(hole, who):
    if hole[1] in RAILS:
        return
    if hole in holes_used:
        sys.exit('hole %s%s claimed by %s and %s' % (hole[1], hole[0], holes_used[hole], who))
    holes_used[hole] = who


for p in PARTS:
    for pin in range(1, p.npins + 1):
        claim(p.hole(pin), '%s.%d' % (p.ref, pin))


def pt(h):
    col, row = h
    return X(col), Yr(row)


def N(net):
    return (' data-net="%s"' % net) if net else ''


def wire(name, a, b, via, color, group, step, net):
    """Jumper from hole a to hole b through intermediate points via=[(col, yunits)]."""
    claim(a, name)
    claim(b, name)
    pts = [pt(a)] + [(X(c), Yu(y)) for c, y in via] + [pt(b)]
    ELEMS.append(('w', name, [('1', a), ('2', b)], pts, color, group, step, net))


def stub(name, a, rail, color, group, step, net):
    claim(a, name)
    x, y = pt(a)
    ELEMS.append(('s', name, [('1', a), ('2', (a[0], rail))],
                  [(x, y), (x, Yr(rail))], color, group, step, net))


def two(kind, name, a, b, label, group, step, net, terms=('1', '2')):
    claim(a, name)
    claim(b, name)
    ELEMS.append((kind, name, [(terms[0], a), (terms[1], b)], label, None, group, step, net))


def pot(name, h1, h2, h3, label, group, step, net):
    for h in (h1, h2, h3):
        claim(h, name)
    ELEMS.append(('pot', name, [('1', h1), ('2', h2), ('3', h3)], label, None, group, step, net))


# ---- power: stubs from the outermost free hole of each strip to the nearest rail of that side
stub('U1 VCC', (18, 'J'), 'R+T', RED, 'pwr', S_POWER, 'VCC')
stub('U1 GND', (18, 'A'), 'R-B', BLK, 'pwr', S_POWER, 'GND')
stub('U2 VCC', (29, 'A'), 'R+B', RED, 'pwr', S_POWER, 'VCC')      # pin 5, lower side
stub('U2 GND', (29, 'J'), 'R-T', BLK, 'pwr', S_POWER, 'GND')      # pin 10, upper side
stub('U3 VDD', (36, 'J'), 'R+T', RED, 'pwr', S_POWER, 'VCC')
stub('U3 VSS', (43, 'A'), 'R-B', BLK, 'pwr', S_POWER, 'GND')

# ---- tie-offs
stub('U1 RESET', (21, 'A'), 'R+B', RED, 'tie', S_RESET555, 'VCC')
for c in (26, 27, 30, 31):
    stub('U2 reset %d' % c, (c, 'A'), 'R-B', BLK, 'tie', S_RESET90, 'GND')
stub('U3 LT', (38, 'A'), 'R+B', RED, 'tie', S_STRAP4511, 'VCC')
stub('U3 BL', (39, 'A'), 'R+B', RED, 'tie', S_STRAP4511, 'VCC')
stub('U3 LE', (40, 'A'), 'R-B', BLK, 'tie', S_STRAP4511, 'GND')

# ---- clock: 555 astable
# R1 = R_A, rail to T_MID (U1 pin 7 strip, column 19 upper).
two('res', 'R1', (19, 'J'), (19, 'R+T'), '<10k', 'clk', S_RA, 'T_MID')
# R2..R5 run left along the upper half, alternating rows H and I so no two leads share a hole.
two('res', 'R2', (19, 'H'), (16, 'H'), '10k', 'clk', S_CHAIN_UP, 'T_MID')
two('res', 'R3', (16, 'I'), (13, 'I'), '10k', 'clk', S_CHAIN_UP, 'CH1')
two('res', 'R4', (13, 'H'), (10, 'H'), '10k', 'clk', S_CHAIN_UP, 'CH2')
two('res', 'R5', (10, 'I'), (7, 'I'), '10k', 'clk', S_CHAIN_UP, 'CH3')
# R6 crosses the channel in column 7, R7 runs back right along the lower half.
two('res', 'R6', (7, 'G'), (7, 'D'), '10k', 'clk', S_CHAIN_TURN, 'CH4')
two('res', 'R7', (7, 'C'), (10, 'C'), '10k', 'clk', S_CHAIN_TURN, 'CH5')
# RV1, rheostat: pin 1 and wiper on the chain end, pin 3 to T_CAP.
pot('RV1', (10, 'A'), (11, 'A'), (12, 'A'), '10k pot', 'clk', S_POT, 'CH6')
wire('RV1 wiper tie', (11, 'B'), (10, 'B'), [], TIM, 'clk', S_POT, 'CH6')
# close the loop: RV1 pin 3 to TRIG, TRIG to THRES (around the left end of U1)
wire('RV1 to TRIG', (12, 'C'), (19, 'C'), [(12, 13.3), (19, 13.3)], TIM, 'clk', S_LOOP, 'T_CAP')
wire('TRIG to THR', (19, 'D'), (20, 'G'),
     [(19, 12.3), (17.4, 12.3), (17.4, 6.9), (20, 6.9)], TIM, 'clk', S_LOOP, 'T_CAP')
# C1, + on the THRES strip, - in the top ground rail
two('cap', 'C1', (20, 'J'), (20, 'R-T'), '10µF', 'clk', S_CAP, 'T_CAP', terms=('+', '-'))
# optional clock indicator
two('res', 'R19', (20, 'B'), (23, 'B'), '330', 'clk', S_CLKLED, 'CLK')
two('led', 'LED1', (23, 'A'), (23, 'R-B'), 'LED1', 'clk', S_CLKLED, 'N_LED', terms=('A', 'K'))

# ---- counter
wire('CLK', (20, 'C'), (25, 'J'), [(20, 12.3), (23.5, 12.3), (23.5, 4.0), (25, 4.0)],
     ORA, 'cnt', S_CLK, 'CLK')
wire('QA to CKB', (27, 'I'), (25, 'D'), [(27, 5.0), (24.4, 5.0), (24.4, 11.3), (25, 11.3)],
     BLU, 'cnt', S_LINK, 'Q0')

# ---- Q bus to the decoder, through the channel (under both chips)
QB = [('Q0', 27, 42, 9.1), ('Q3', 28, 41, 9.4), ('Q1', 30, 36, 9.7), ('Q2', 31, 37, 10.0)]
for nm, src, dst, lane in QB:
    wire(nm, (src, 'G'), (dst, 'D'), [(src, lane), (dst, lane)], BLU, 'qbus', S_QBUS, nm)
for ref, c, nm, lab in (('R8', 42, 'Q0', '>4k7'), ('R9', 36, 'Q1', '<4k7'),
                       ('R10', 37, 'Q2', ''), ('R11', 41, 'Q3', '')):
    two('res', ref, (c, 'A'), (c, 'R+B'), lab, 'qbus', S_PULLUP, nm)

# ---- segment network
# Bank of seven 330 R crossing the channel. Bank order is the reverse of the CD4511 output
# order, so the seven feed wires nest in the top gap without crossing.
BANK = [('e', 47, 'R16'), ('d', 48, 'R15'), ('c', 49, 'R14'), ('b', 50, 'R13'),
        ('a', 51, 'R12'), ('g', 52, 'R18'), ('f', 53, 'R17')]
U3OUT = {'f': 15, 'g': 14, 'a': 13, 'b': 12, 'c': 11, 'd': 10, 'e': 9}
DSPIN = {'a': 7, 'b': 6, 'c': 4, 'd': 2, 'e': 1, 'f': 9, 'g': 10}
TOPLANE = {'e': 3.9, 'd': 3.6, 'c': 3.3, 'b': 3.0, 'a': 2.7, 'g': 2.4, 'f': 2.1}
for s, col, ref in BANK:
    two('res', ref, (col, 'G'), (col, 'D'), '', 'seg', S_SEGRES, s)
GROUPLABELS = [(50, 'H', -0.15, '7 \u00d7 330 \u03a9', 'seg', S_SEGRES, ''),
               (U3.col0 + 3.5, 'A', 3.0, '4 \u00d7 4k7 pull-ups on Q0..Q3', 'qbus', S_PULLUP, '')]
for s, col, ref in BANK:
    src = U3.hole(U3OUT[s])[0]
    wire('U3 %s' % s, (src, 'J'), (col, 'J'), [(src, TOPLANE[s]), (col, TOPLANE[s])],
         SEG, 'seg', S_SEGIN, s)
# Out of the bank. c, d, e land on the display's lower pins from below. a, b, f, g land on its
# upper pins: each rises in its own gap between display columns, passes under the display
# body, and comes out above it into row J. Seven wires that have to reorder themselves cannot
# all nest; every crossing that remains is square and in the open.
BOT = {'f': (15.25, 57.72, 4.95, 59), 'g': (15.6, 58.5, 4.7, 58),
       'a': (15.95, 59.5, 4.95, 61), 'b': (16.3, 60.5, 4.7, 62),
       'e': (16.65, None, None, 58), 'd': (17.0, None, None, 59), 'c': (17.35, None, None, 61)}
for s, col, ref in BANK:
    lane, turn, top, dcol = BOT[s]
    if turn is None:
        wire('DS1 %s' % s, (col, 'A'), (dcol, 'A'), [(col, lane), (dcol, lane)],
             SEG, 'seg', S_SEGOUT, s)
    else:
        wire('DS1 %s' % s, (col, 'A'), (dcol, 'J'),
             [(col, lane), (turn, lane), (turn, top), (dcol, top)], SEG, 'seg', S_SEGOUT, s)
stub('DS1 CC lower', (60, 'A'), 'R-B', BLK, 'seg', S_COM, 'GND')
stub('DS1 CC upper', (60, 'J'), 'R-T', BLK, 'seg', S_COM, 'GND')

# ------------------------------------------------------------------ expected netlist
# Written from the HOP-3 Rev B spec (sections 5.2 to 5.5), independently of the drawing.
# Breadboard designators; see WIRING.md for the cross-reference to the PCB designators.
NETLIST = {
    'VCC': ['U1.8', 'U1.4', 'U2.5', 'U3.16', 'U3.3', 'U3.4', 'R1.2',
            'R8.2', 'R9.2', 'R10.2', 'R11.2'],
    'GND': ['U1.1', 'U2.10', 'U2.2', 'U2.3', 'U2.6', 'U2.7', 'U3.8', 'U3.5',
            'DS1.3', 'DS1.8', 'C1.-', 'LED1.K'],
    'T_MID': ['U1.7', 'R1.1', 'R2.1'],
    'CH1': ['R2.2', 'R3.1'], 'CH2': ['R3.2', 'R4.1'], 'CH3': ['R4.2', 'R5.1'],
    'CH4': ['R5.2', 'R6.1'], 'CH5': ['R6.2', 'R7.1'],
    'CH6': ['R7.2', 'RV1.1', 'RV1.2'],
    'T_CAP': ['RV1.3', 'U1.2', 'U1.6', 'C1.+'],
    'CLK': ['U1.3', 'U2.14', 'R19.1'],
    'N_LED': ['R19.2', 'LED1.A'],
    'Q0': ['U2.12', 'U2.1', 'U3.7', 'R8.1'],
    'Q1': ['U2.9', 'U3.1', 'R9.1'],
    'Q2': ['U2.8', 'U3.2', 'R10.1'],
    'Q3': ['U2.11', 'U3.6', 'R11.1'],
    'U1.5': ['U1.5'], 'U2.4': ['U2.4'], 'U2.13': ['U2.13'], 'DS1.5': ['DS1.5'],
}
for s, _, ref in BANK:
    NETLIST['SEG_' + s] = ['U3.%d' % U3OUT[s], ref + '.1']
    NETLIST['N_SEG_' + s] = [ref + '.2', 'DS1.%d' % DSPIN[s]]


def check():
    parent = {}

    def node(h):
        col, row = h
        if row in ('R+T', 'R+B'):
            return 'VCC'          # the power module drives both + rails
        if row in ('R-T', 'R-B'):
            return 'GND'
        return ('U' if row in UPPER else 'L', col)

    def find(a):
        parent.setdefault(a, a)
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        parent[find(a)] = find(b)

    term = {}
    for p in PARTS:
        for pin in range(1, p.npins + 1):
            term['%s.%d' % (p.ref, pin)] = node(p.hole(pin))
    for kind, name, terms, *_ in ELEMS:
        if kind in ('w', 's'):
            union(node(terms[0][1]), node(terms[1][1]))
        else:
            for t, h in terms:
                term['%s.%s' % (name, t)] = node(h)
    if 'RV1 wiper tie' not in [el[1] for el in ELEMS]:
        sys.exit('wiper tie missing')
    got = {}
    for t, n in term.items():
        got.setdefault(find(n), set()).add(t)
    want = [frozenset(v) for v in NETLIST.values()]
    have = [frozenset(v) for v in got.values()]
    errs = []
    for k, v in NETLIST.items():
        if frozenset(v) not in have:
            errs.append('net %s %s not found as drawn' % (k, sorted(v)))
    for v in have:
        if v not in want:
            errs.append('drawn net %s matches no spec net' % sorted(v))
    if errs:
        sys.exit('NETLIST MISMATCH\n  ' + '\n  '.join(errs))
    return len(have), len(term)


# ------------------------------------------------------------------ drawing
def draw_board():
    y0 = Yu(-0.7)
    e('<rect class="bd" x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="8"/>'
      % (X(1) - P * 0.8, y0, NCOL * P + P * 0.6, BOARD_H * P))
    ch_t = Yr('F') + P * 0.5
    ch_b = Yr('E') - P * 0.5
    e('<rect class="ch" x="%.0f" y="%.0f" width="%.0f" height="%.0f"/>'
      % (X(1) - P * 0.8, ch_t, NCOL * P + P * 0.6, ch_b - ch_t))
    for rl, cls in (('R+T', 'rp'), ('R-T', 'rn'), ('R-B', 'rn'), ('R+B', 'rp')):
        yy = Yr(rl)
        e('<line class="%s" x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f"/>'
          % (cls, X(1) - P * 0.4, yy, X(NCOL) + P * 0.4, yy))
        e('<text class="raillab" x="%.0f" y="%.0f">%s</text>'
          % (X(NCOL) + P * 1.1, yy + 3, '+' if 'R+' in rl else '−'))
    for rl in RAILS:
        yy = Yr(rl)
        for c in range(1, NCOL + 1):
            e('<circle class="hl" cx="%.1f" cy="%.1f" r="2.1"/>' % (X(c), yy))
    for rl in 'JIHGFEDCBA':
        yy = Yr(rl)
        for c in range(1, NCOL + 1):
            e('<circle class="hl" cx="%.1f" cy="%.1f" r="2.6"/>' % (X(c), yy))
        e('<text class="rowlab" x="%.0f" y="%.0f">%s</text>' % (X(1) - P * 1.5, yy + 3, rl))
        e('<text class="rowlab" x="%.0f" y="%.0f">%s</text>' % (X(NCOL) + P * 1.1, yy + 3, rl))
    for c in [1] + list(range(5, NCOL + 1, 5)):
        e('<text class="collab" x="%.1f" y="%.0f">%d</text>' % (X(c), Yu(-1.15), c))
    e('<text class="btitle" x="%.0f" y="%.0f">830-POINT BOARD   CLOCK / COUNTER / DECODER / DISPLAY</text>'
      % (X(1) - P * 0.8, Yu(-1.95)))


def draw_part(p):
    r0, r1 = p.rows
    yt = Yr(r1) - P * 0.40
    yb = Yr(r0) + P * 0.40
    x0 = X(p.col0) - P * 0.42
    w = (p.npins // 2 - 1) * P + P * 0.84
    cls = 'disp' if p.ref == 'DS1' else 'ic'
    e('<g class="part" id="bp-%s">' % p.ref)
    e('<rect class="%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3"/>'
      % (cls, x0, yt, w, yb - yt))
    if p.ref != 'DS1':
        e('<path class="notch" d="M %.1f %.1f a 6 6 0 0 0 0 12"/>' % (x0, (yt + yb) / 2 - 6))
    mid = (yt + yb) / 2
    if p.ref == 'DS1':
        # a small digit outline so it reads as a display
        cx, top = x0 + w / 2, yt + P * 1.15
        sw, sh = P * 1.25, P * 1.45
        d = ('M %.1f %.1f h %.1f v %.1f h %.1f v %.1f h %.1f M %.1f %.1f v %.1f h %.1f'
             % (cx - sw / 2, top, sw, sh, -sw, -sh, 0, cx - sw / 2, top + sh, sh, sw))
        e('<path class="dglyph" d="M %.1f %.1f h %.1f v %.1f h %.1f z M %.1f %.1f h %.1f M %.1f %.1f v %.1f"/>'
          % (cx - sw / 2, top, sw, 2 * sh, -sw, cx - sw / 2, top + sh, sw,
             cx + sw / 2, top + sh, 0))
        e('<text class="iclab" x="%.1f" y="%.1f">DS1 7-SEG CC</text>' % (cx, yb - P * 1.15))
    else:
        e('<text class="iclab" x="%.1f" y="%.1f">%s</text>' % (x0 + w / 2, mid + 3.6, p.label))
    for pin in sorted(p.names):
        col, row = p.hole(pin)
        lx = X(col) + 3.2
        if row == r1:      # upper row: label reads downward from just inside the top edge
            ly = yt + 3.5
            e('<text class="pinlab" x="%.1f" y="%.1f" transform="rotate(90 %.1f %.1f)">%d %s</text>'
              % (lx - 6.4, ly, lx - 6.4, ly, pin, p.names[pin]))
        else:
            ly = yb - 3.5
            e('<text class="pinlab" x="%.1f" y="%.1f" transform="rotate(-90 %.1f %.1f)">%d %s</text>'
              % (lx, ly, lx, ly, pin, p.names[pin]))
    e('</g>')


def g_open(group, step, net):
    return '<g class="sw g-%s" data-s="%d"%s>' % (group, step, N(net))


def draw_elem(el):
    kind, name, terms, a3, a4, group, step, net = el
    if kind in ('w', 's'):
        pts, color = a3, a4
        d = 'M ' + ' L '.join('%.1f %.1f' % p for p in pts)
        e('<path class="w sw g-%s" data-s="%d"%s d="%s" stroke="%s" stroke-width="2.2"/>'
          % (group, step, N(net), d, color))
        for (xx, yy) in (pts[0], pts[-1]):
            e('<circle class="wd sw g-%s" data-s="%d"%s cx="%.1f" cy="%.1f" r="3.4" fill="%s"/>'
              % (group, step, N(net), xx, yy, color))
        return
    label = a3
    if kind == 'pot':
        (x1, y1), (x2, _), (x3, _) = [pt(h) for _, h in terms]
        e(g_open(group, step, net))
        e('<rect class="pot" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4"/>'
          % (x1 - 8, y1 - 8, x3 - x1 + 16, 16))
        e('<circle class="potk" cx="%.1f" cy="%.1f" r="5.5"/>' % (x2, y1))
        for xx in (x1, x2, x3):
            e('<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (xx, y1, TIM))
        e('<text class="reslab" x="%.1f" y="%.1f">RV1 10k</text>' % (x2, y1 + 22))
        e('</g>')
        return
    (x1, y1), (x2, y2) = pt(terms[0][1]), pt(terms[1][1])
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    horiz = abs(x2 - x1) >= abs(y2 - y1)
    lead = '#6b5428' if kind == 'res' else ('#1f6b3c' if kind == 'led' else '#3a5a8a')
    e(g_open(group, step, net))
    e('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8"/>'
      % (x1, y1, x2, y2, lead))
    if kind == 'res':
        bl, bw = (26, 9) if horiz else (9, 24)
        e('<rect class="res" x="%.1f" y="%.1f" width="%d" height="%d" rx="2"/>'
          % (mx - bl / 2, my - bw / 2, bl, bw))
    elif kind == 'cap':
        e('<rect class="cap" x="%.1f" y="%.1f" width="15" height="19" rx="4"/>' % (mx - 7.5, my - 9.5))
        e('<text class="capp" x="%.1f" y="%.1f">+</text>' % (x1 + 9, y1 - 3))
    elif kind == 'led':
        e('<circle class="led" cx="%.1f" cy="%.1f" r="7.5"/>' % (mx, my))
    for (xx, yy) in ((x1, y1), (x2, y2)):
        e('<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (xx, yy, lead))
    if not label:
        pass
    elif horiz:
        e('<text class="reslab" x="%.1f" y="%.1f">%s</text>' % (mx, my - 8, label))
    elif label[0] == '<':
        e('<text class="reslab rr" x="%.1f" y="%.1f">%s</text>' % (mx - 8, my + 3, label[1:]))
    else:
        e('<text class="reslab rl" x="%.1f" y="%.1f">%s</text>' % (mx + 8, my + 3, label.lstrip('>')))
    e('</g>')


def draw_module():
    """Breadboard power module over the left end. It feeds both rail pairs."""
    x0, x1 = X(1) - P * 0.75, X(5) + P * 0.45
    e('<g class="sw g-pwr" data-s="%d" data-net="VCC">' % S_MODULE)
    e('<rect class="mod" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6"/>'
      % (x0, Yu(-0.55), x1 - x0, Yu(BOARD_H - 0.35)))
    for rl in RAILS:
        e('<circle class="modpin" cx="%.1f" cy="%.1f" r="3.6"/>' % (X(2), Yr(rl)))
        e('<circle class="modpin" cx="%.1f" cy="%.1f" r="3.6"/>' % (X(3), Yr(rl)))
    ty = Yu(9.6)
    e('<text class="modlab" x="%.1f" y="%.1f" transform="rotate(-90 %.1f %.1f)">POWER MODULE  5 V | 5 V</text>'
      % ((x0 + x1) / 2 + 4, ty, (x0 + x1) / 2 + 4, ty))
    e('</g>')


nets, terms = check()

e('<g id="root">')
draw_board()
draw_module()
for el in ELEMS:
    if el[0] in ('w', 's'):
        draw_elem(el)
for p in PARTS:
    draw_part(p)
# Passives go on top: a resistor or capacitor lead is visible, never hidden under a chip.
for el in ELEMS:
    if el[0] not in ('w', 's'):
        draw_elem(el)
for col, row, dy, txt, group, step, net in GROUPLABELS:
    e('<text class="sw g-%s grplab" data-s="%d" x="%.1f" y="%.1f">%s</text>'
      % (group, step, X(col), Yr(row) + dy * P, txt))
e('</g>')

W_PX = X(NCOL) + MARGIN_X + P
H_PX = Yu(BOARD_H)
svg = ('<svg id="bb" viewBox="-14 -60 %.0f %.0f" xmlns="http://www.w3.org/2000/svg" '
       'role="img" aria-label="Breadboard placement diagram for the HOP 3 BCD counter">'
       % (W_PX + 28, H_PX + 70)) + '\n'.join(out) + '</svg>'
io.open('bb.svg', 'w', encoding='utf-8').write(svg)

steps = sorted(set(el[6] for el in ELEMS) | {S_MODULE})
print('ok', len(svg), '| nets', nets, '| terminals', terms, '| holes', len(holes_used),
      '| stamped steps', len(steps))
