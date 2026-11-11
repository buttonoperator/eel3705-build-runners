# -*- coding: utf-8 -*-
import io

P = 22.0
MARGIN_X = 40.0
NCOL = 63
ROW = {'R+T': 0.0, 'R-T': 1.0, 'J': 4.4, 'I': 5.4, 'H': 6.4, 'G': 7.4, 'F': 8.4,
       'E': 10.8, 'D': 11.8, 'C': 12.8, 'B': 13.8, 'A': 14.8,
       'R-B': 18.2, 'R+B': 19.2}
BOARD_H = 20.2
B1Y = 0.0
B2Y = 23.6
INTER = 20.9

def X(col):
    return MARGIN_X + (col - 1) * P

def Y(board, row):
    return ((B1Y if board == 1 else B2Y) + ROW[row]) * P

def YU(board, u):
    return ((B1Y if board == 1 else B2Y) + u) * P

out = []
def e(s):
    out.append(s)

def dip_hole(col0, npins, pin):
    half = npins // 2
    if pin <= half:
        return col0 + pin - 1, 'E'
    return col0 + (npins - pin), 'F'

class Part:
    def __init__(self, ref, board, col0, npins, label, pins):
        self.ref, self.board, self.col0 = ref, board, col0
        self.npins, self.label, self.pins = npins, label, pins
    def hole(self, pin):
        c, r = dip_hole(self.col0, self.npins, pin)
        return (self.board, c, r)

A283 = {1: 'S2', 2: 'B2', 3: 'A2', 4: 'S1', 5: 'A1', 6: 'B1', 7: 'C0', 8: 'GND',
        9: 'C4', 10: 'S4', 11: 'B4', 12: 'A4', 13: 'S3', 14: 'A3', 15: 'B3', 16: 'VCC'}
G14 = {1: '1A', 2: '1B', 3: '1Y', 4: '2A', 5: '2B', 6: '2Y', 7: 'GND',
       8: '3Y', 9: '3A', 10: '3B', 11: '4Y', 12: '4A', 13: '4B', 14: 'VCC'}
C4511 = {1: 'B', 2: 'C', 3: '/LT', 4: '/BL', 5: 'LE', 6: 'D', 7: 'A', 8: 'VSS',
         9: 'e', 10: 'd', 11: 'c', 12: 'b', 13: 'a', 14: 'g', 15: 'f', 16: 'VDD'}
SWP = {1: 'A0', 2: 'A1', 3: 'A2', 4: 'A3', 5: 'B0', 6: 'B1', 7: 'B2', 8: 'B3',
       9: '+5', 10: '+5', 11: '+5', 12: '+5', 13: '+5', 14: '+5', 15: '+5', 16: '+5'}
DISPP = {1: 'e', 2: 'd', 3: 'CC', 4: 'c', 5: 'dp', 6: 'b', 7: 'a', 8: 'CC', 9: 'f', 10: 'g'}

SW1 = Part('SW1', 1, 2, 16, 'SW1  8-POS DIP', SWP)
U1 = Part('U1', 1, 13, 16, 'U1  74HC283', A283)
U3 = Part('U3', 1, 24, 14, 'U3  74HC08', G14)
U4 = Part('U4', 1, 34, 14, 'U4  74HC32', G14)
U2 = Part('U2', 1, 44, 16, 'U2  74HC283', A283)
U5 = Part('U5', 2, 8, 16, 'U5  CD4511', C4511)
DSP = Part('DS1', 2, 50, 10, 'DS1  7-SEG CC', DISPP)
PARTS = [SW1, U1, U3, U4, U2, U5, DSP]

def draw_board(board, title):
    y0 = YU(board, -0.7)
    h = BOARD_H * P
    e('<rect class="bd" x="%.0f" y="%.0f" width="%.0f" height="%.0f" rx="8"/>'
      % (X(1) - P * 0.8, y0, NCOL * P + P * 0.6, h))
    ch_t = Y(board, 'F') + P * 0.5
    ch_b = Y(board, 'E') - P * 0.5
    e('<rect class="ch" x="%.0f" y="%.0f" width="%.0f" height="%.0f"/>'
      % (X(1) - P * 0.8, ch_t, NCOL * P + P * 0.6, ch_b - ch_t))
    for rl, cls in (('R+T', 'rp'), ('R-T', 'rn'), ('R-B', 'rn'), ('R+B', 'rp')):
        yy = Y(board, rl)
        e('<line class="%s" x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f"/>'
          % (cls, X(1) - P * 0.4, yy, X(NCOL) + P * 0.4, yy))
    for rl in ('R+T', 'R-T', 'R-B', 'R+B'):
        yy = Y(board, rl)
        for c in range(1, NCOL + 1):
            e('<circle class="hl" cx="%.1f" cy="%.1f" r="2.1"/>' % (X(c), yy))
    for rl in ('J', 'I', 'H', 'G', 'F', 'E', 'D', 'C', 'B', 'A'):
        yy = Y(board, rl)
        for c in range(1, NCOL + 1):
            e('<circle class="hl" cx="%.1f" cy="%.1f" r="2.6"/>' % (X(c), yy))
        e('<text class="rowlab" x="%.0f" y="%.0f">%s</text>' % (X(1) - P * 1.5, yy + 3, rl))
        e('<text class="rowlab" x="%.0f" y="%.0f">%s</text>' % (X(NCOL) + P * 1.1, yy + 3, rl))
    for c in range(5, NCOL + 1, 5):
        e('<text class="collab" x="%.1f" y="%.0f">%d</text>' % (X(c), YU(board, -1.15), c))
    e('<text class="btitle" x="%.0f" y="%.0f">%s</text>' % (X(1) - P * 0.8, YU(board, -1.9), title))

def draw_part(p):
    x0 = X(p.col0) - P * 0.42
    w = (p.npins // 2 - 1) * P + P * 0.84
    yt = Y(p.board, 'F') - P * 0.40
    yb = Y(p.board, 'E') + P * 0.40
    e('<rect class="ic" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3"/>'
      % (x0, yt, w, yb - yt))
    e('<path class="notch" d="M %.1f %.1f a 7 7 0 0 0 0 14"/>' % (x0, (yt + yb) / 2 - 7))
    e('<text class="iclab" x="%.1f" y="%.1f">%s</text>' % (x0 + w / 2, (yt + yb) / 2 + 4, p.label))
    for pin in sorted(p.pins):
        name = p.pins[pin]
        c, r = dip_hole(p.col0, p.npins, pin)
        lx = X(c)
        ly = YU(p.board, 6.95) if r == 'F' else YU(p.board, 12.30)
        e('<text class="pinlab" x="%.1f" y="%.1f" transform="rotate(-90 %.1f %.1f)">%d&#183;%s</text>'
          % (lx, ly, lx, ly, pin, name))

def pt(board, col, row):
    return (X(col), Y(board, row))

RED, BLK, ORA = '#d1495b', '#3d4451', '#e08b2a'
BLU, GRN, PUR, SEG = '#2f7fd6', '#2f9e5e', '#8b5cf6', '#c2410c'

def N(net):
    return (' data-net="%s"' % net) if net else ''

def wire(a, b, color, lane, group, step, net=''):
    (x1, y1), (x2, y2) = pt(*a), pt(*b)
    ly = lane * P
    d = 'M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f' % (x1, y1, x1, ly, x2, ly, x2, y2)
    e('<path class="w sw g-%s" data-s="%d"%s d="%s" stroke="%s" stroke-width="2.2"/>'
      % (group, step, N(net), d, color))
    for (xx, yy) in ((x1, y1), (x2, y2)):
        e('<circle class="wd sw g-%s" data-s="%d"%s cx="%.1f" cy="%.1f" r="3.4" fill="%s"/>'
          % (group, step, N(net), xx, yy, color))

def stub(a, rail, color, group, step, net=''):
    board, col, row = a
    x, y1 = X(col), Y(board, row)
    y2 = Y(board, rail)
    e('<path class="w sw g-%s" data-s="%d"%s d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2.2"/>'
      % (group, step, N(net), x, y1, x, y2, color))
    e('<circle class="wd sw g-%s" data-s="%d"%s cx="%.1f" cy="%.1f" r="3.4" fill="%s"/>'
      % (group, step, N(net), x, y1, color))
    e('<circle class="wd sw g-%s" data-s="%d"%s cx="%.1f" cy="%.1f" r="3.4" fill="%s"/>'
      % (group, step, N(net), x, y2, color))

def resistor(a, b, label, group, step, net='', color='#9a7b4f'):
    (x1, y1), (x2, y2) = pt(*a), pt(*b)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    horiz = abs(x2 - x1) >= abs(y2 - y1)
    bl, bw = (26, 9) if horiz else (9, 26)
    e('<g class="sw g-%s" data-s="%d"%s>' % (group, step, N(net)))
    e('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8"/>'
      % (x1, y1, x2, y2, color))
    e('<rect class="res" x="%.1f" y="%.1f" width="%d" height="%d" rx="2"/>'
      % (mx - bl / 2, my - bw / 2, bl, bw))
    e('<text class="reslab" x="%.1f" y="%.1f">%s</text>' % (mx, my - bw / 2 - 4, label))
    for (xx, yy) in ((x1, y1), (x2, y2)):
        e('<circle cx="%.1f" cy="%.1f" r="3.2" fill="%s"/>' % (xx, yy, color))
    e('</g>')

WIRES = []
def W(*a):
    WIRES.append(('w', a))
def S(*a):
    WIRES.append(('s', a))
def R(*a):
    WIRES.append(('r', a))

# power
for p, vpin, gpin in ((U1, 16, 8), (U2, 16, 8), (U3, 14, 7), (U4, 14, 7), (U5, 16, 8)):
    S(p.hole(vpin), 'R+T', RED, 'pwr', 7, 'VCC')
    S(p.hole(gpin), 'R-B', BLK, 'pwr', 7, 'GND')
for c in range(2, 10):
    S((1, c, 'F'), 'R+T', RED, 'pwr', 13, 'VCC')

# operand entry
IN = [(2, U1, 5, 'A0'), (3, U1, 3, 'A1'), (4, U1, 14, 'A2'), (5, U1, 12, 'A3'),
      (6, U1, 6, 'B0'), (7, U1, 2, 'B1'), (8, U1, 15, 'B2'), (9, U1, 11, 'B3')]
for i, (c, p, pin, nm) in enumerate(IN):
    R((1, c, 'B'), (1, c, 'R-B'), '10k', 'in', 14, nm)
    W((1, c, 'A'), p.hole(pin), ORA, 15.4 + 0.32 * i, 'in', 15 if i < 4 else 16, nm)

# Z bus
Z = {0: U1.hole(4), 1: U1.hole(1), 2: U1.hole(13), 3: U1.hole(10)}
K = U1.hole(9)
zpairs = [(Z[0], U2.hole(5), 'Z0'), (Z[1], U2.hole(3), 'Z1'),
          (Z[2], U2.hole(14), 'Z2'), (Z[3], U2.hole(12), 'Z3'),
          (Z[3], U3.hole(1), 'Z3'), (Z[2], U3.hole(2), 'Z2'),
          (Z[3], U3.hole(4), 'Z3'), (Z[1], U3.hole(5), 'Z1')]
# Z2 and Z3 run from U1's top side to U2's top side, so route them over the top of the
# board instead of dragging them under it. Everything else crosses the channel anyway.
TOPLANE = {2: 2.3, 3: 2.9}
for i, (src, dst, nm) in enumerate(zpairs):
    W(src, dst, BLU, TOPLANE.get(i, 17.8 - 0.30 * i), 'z', 18 if i < 4 else 19, nm)
W(K, U4.hole(5), BLU, 3.6, 'z', 20, 'K')

# correction logic
W(U3.hole(3), U4.hole(1), GRN, 15.5, 'corr', 20, 'Z3\u00B7Z2')
W(U3.hole(6), U4.hole(2), GRN, 15.9, 'corr', 20, 'Z3\u00B7Z1')
W(U4.hole(3), U4.hole(4), GRN, 16.3, 'corr', 20, 'N3')
W(U4.hole(6), U2.hole(2), GRN, 16.7, 'corr', 21, 'C')
W(U4.hole(6), U2.hole(15), GRN, 17.1, 'corr', 21, 'C')
W(U4.hole(6), (1, 55, 'A'), GRN, 17.5, 'corr', 22, 'C')
R((1, 55, 'C'), (1, 58, 'C'), '330', 'corr', 22, 'LED')

# tie-offs
for h in [U3.hole(9), U3.hole(10), U3.hole(12), U3.hole(13),
          U4.hole(9), U4.hole(10), U4.hole(12), U4.hole(13)]:
    S(h, 'R-T', BLK, 'tie', 10, 'GND')
S(U2.hole(11), 'R-T', BLK, 'tie', 11, 'GND')
for h in [U1.hole(7), U2.hole(7), U2.hole(6)]:
    S(h, 'R-B', BLK, 'tie', 11, 'GND')
S(U5.hole(5), 'R-B', BLK, 'tie', 12, 'GND')
S(U5.hole(3), 'R+B', RED, 'tie', 12, 'VCC')
S(U5.hole(4), 'R+B', RED, 'tie', 12, 'VCC')

# S bus across boards
for i, (src, dst, nm) in enumerate([(U2.hole(4), U5.hole(7), 'S0'),
                                    (U2.hole(1), U5.hole(1), 'S1'),
                                    (U2.hole(13), U5.hole(2), 'S2'),
                                    (U2.hole(10), U5.hole(6), 'S3')]):
    W(src, dst, PUR, INTER + 0.45 * i, 'sbus', 23, nm)

# segment network
SEGMAP = [('a', 13, 20, 22, 7), ('b', 12, 24, 26, 6), ('c', 11, 28, 30, 4),
          ('d', 10, 32, 34, 2), ('e', 9, 36, 38, 1), ('f', 15, 40, 42, 9),
          ('g', 14, 44, 46, 10)]
for i, (nm, upin, rl, rr, dpin) in enumerate(SEGMAP):
    W(U5.hole(upin), (2, rl, 'J'), SEG, B2Y + 1.7 + 0.30 * i, 'seg', 25, nm)
    R((2, rl, 'J'), (2, rr, 'J'), '330', 'seg', 24, nm)
    db, dc, dr = DSP.hole(dpin)
    W((2, rr, 'I'), (db, dc, dr), SEG, B2Y + 3.9 - 0.30 * i, 'seg', 26, nm)
S(DSP.hole(3), 'R-B', BLK, 'seg', 27, 'GND')
S(DSP.hole(8), 'R-B', BLK, 'seg', 27, 'GND')

e('<g id="root">')
draw_board(1, 'BOARD 1   OPERAND ENTRY / ADDER / CORRECTION LOGIC')
draw_board(2, 'BOARD 2   DECODER AND DISPLAY')
for kind, a in WIRES:
    if kind == 'w':
        wire(*a)
    elif kind == 's':
        stub(*a)
    else:
        resistor(*a)

lx1, lx2 = X(58), X(60)
ly = Y(1, 'A')
e('<g class="sw g-corr" data-s="22" data-net="LED">')
e('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8"/>'
  % (lx1, ly, lx2, ly, GRN))
e('<circle class="led" cx="%.1f" cy="%.1f" r="8"/>' % ((lx1 + lx2) / 2, ly))
e('<text class="reslab" x="%.1f" y="%.1f">LED1 tens</text>' % ((lx1 + lx2) / 2, ly - 13))
e('</g>')
stub((1, 60, 'B'), 'R-B', BLK, 'corr', 22, 'GND')

for bd in (1, 2):
    e('<path class="w sw g-pwr" data-s="5" data-net="GND" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" '
      'stroke="%s" stroke-width="2.2" fill="none"/>'
      % (X(62), Y(bd, 'R-T'), X(63), Y(bd, 'R-T'), X(63), Y(bd, 'R-B'), X(62), Y(bd, 'R-B'), BLK))
    e('<path class="w sw g-pwr" data-s="5" data-net="VCC" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" '
      'stroke="%s" stroke-width="2.2" fill="none"/>'
      % (X(1), Y(bd, 'R+T'), X(1) - P * 0.55, Y(bd, 'R+T'),
         X(1) - P * 0.55, Y(bd, 'R+B'), X(1), Y(bd, 'R+B'), RED))
e('<path class="w sw g-pwr" data-s="6" data-net="VCC" d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2.2" fill="none"/>'
  % (X(2), Y(1, 'R+B'), X(2), Y(2, 'R+T'), RED))
e('<path class="w sw g-pwr" data-s="6" data-net="GND" d="M %.1f %.1f L %.1f %.1f" stroke="%s" stroke-width="2.2" fill="none"/>'
  % (X(4), Y(1, 'R-B'), X(4), Y(2, 'R-T'), BLK))

for p in PARTS:
    draw_part(p)
e('</g>')

W_PX = X(NCOL) + MARGIN_X + P
H_PX = YU(2, BOARD_H - 0.2)
svg = ('<svg id="bb" viewBox="-14 -72 %.0f %.0f" xmlns="http://www.w3.org/2000/svg" '
       'role="img" aria-label="Breadboard placement diagram for the HOP 2 BCD adder">'
       % (W_PX + 28, H_PX + 96)) + '\n'.join(out) + '</svg>'
io.open('bb.svg', 'w', encoding='utf-8').write(svg)
print('ok', len(svg))
