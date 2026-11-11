# -*- coding: utf-8 -*-
"""Signal-flow / pinout diagram for the HOP 2 BCD adder."""
import io

out = []
def e(s):
    out.append(s)

RED, BLK, ORA = '#d1495b', '#3d4451', '#e08b2a'
BLU, GRN, PUR, SEG = '#2f7fd6', '#2f9e5e', '#8b5cf6', '#c2410c'

PINR = 8.5

def pindot(x, y, num, side):
    e('<circle class="pd" cx="%.1f" cy="%.1f" r="%.1f"/>' % (x, y, PINR))
    e('<text class="pn" x="%.1f" y="%.1f">%d</text>' % (x, y + 3.1, num))

def chip(x, y, w, title, sub, left, right, extra=None):
    """left/right: list of (pin, name) or None for a blank slot."""
    n = max(len(left), len(right))
    pitch = 30
    h = (n + 1) * pitch
    e('<g class="chip">')
    e('<rect class="pkg" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5"/>' % (x, y, w, h))
    e('<text class="pkgt" x="%.1f" y="%.1f">%s</text>' % (x + w / 2, y + 26, title))
    e('<text class="pkgs" x="%.1f" y="%.1f">%s</text>' % (x + w / 2, y + 42, sub))
    e('<line class="pkgr" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
      % (x + 10, y + 54, x + w - 10, y + 54))
    pos = {}
    for i, item in enumerate(left):
        if item is None:
            continue
        pin, name = item
        py = y + 70 + i * pitch
        pindot(x, py, pin, 'L')
        e('<text class="pname pl" x="%.1f" y="%.1f">%s</text>' % (x + PINR + 7, py + 3.6, name))
        pos[name] = (x, py)
    for i, item in enumerate(right):
        if item is None:
            continue
        pin, name = item
        py = y + 70 + i * pitch
        pindot(x + w, py, pin, 'R')
        e('<text class="pname pr" x="%.1f" y="%.1f">%s</text>' % (x + w - PINR - 7, py + 3.6, name))
        pos[name] = (x + w, py)
    if extra:
        e('<text class="pkgx" x="%.1f" y="%.1f">%s</text>' % (x + w / 2, y + h + 18, extra))
    e('</g>')
    return pos, h

def gate(kind, x, y, label, pins, w=52, h=42):
    """kind 'and' or 'or'. pins = (inA, inB, outY). Returns (ia, ib, oy) points."""
    e('<g class="chip">')
    if kind == 'and':
        d = ('M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f L %.1f %.1f Z'
             % (x, y, x + w * 0.5, y, h / 2, h / 2, x + w * 0.5, y + h, x, y + h))
        back = x
    else:
        d = ('M %.1f %.1f C %.1f %.1f %.1f %.1f %.1f %.1f '
             'C %.1f %.1f %.1f %.1f %.1f %.1f '
             'C %.1f %.1f %.1f %.1f %.1f %.1f Z'
             % (x, y,
                x + w * 0.42, y + h * 0.06, x + w * 0.72, y + h * 0.22, x + w, y + h / 2,
                x + w * 0.72, y + h * 0.78, x + w * 0.42, y + h * 0.94, x, y + h,
                x + w * 0.28, y + h * 0.70, x + w * 0.28, y + h * 0.30, x, y))
        back = x + w * 0.11
    e('<path class="gate" d="%s"/>' % d)
    ya, yb = y + h * 0.28, y + h * 0.72
    ox = x + w if kind == 'and' else x + w
    for px, py, pin in ((back, ya, pins[0]), (back, yb, pins[1])):
        e('<line class="lead" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (px - 16, py, px, py))
        pindot(px - 16, py, pin, 'L')
    e('<line class="lead" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
      % (ox, y + h / 2, ox + 16, y + h / 2))
    pindot(ox + 16, y + h / 2, pins[2], 'R')
    e('<text class="gl" x="%.1f" y="%.1f">%s</text>' % (x + w * 0.46, y - 9, label))
    e('</g>')
    return (back - 16, ya), (back - 16, yb), (ox + 16, y + h / 2)

def net(p1, p2, color, label=None, mid=None, lx=None, dash=False):
    (x1, y1), (x2, y2) = p1, p2
    mx = mid if mid is not None else (x1 + x2) / 2
    d = 'M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f' % (x1, y1, mx, y1, mx, y2, x2, y2)
    e('<path class="net%s" d="%s" stroke="%s"/>' % (' dash' if dash else '', d, color))
    e('<circle class="nd" cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (x2, y2, color))
    if label:
        tx = lx if lx is not None else (x1 + mx) / 2
        e('<text class="nl" x="%.1f" y="%.1f" fill="%s">%s</text>' % (tx, y1 - 6, color, label))

def tap(x, y, color):
    e('<circle class="nd" cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (x, y, color))

# ---------------------------------------------------------------- chips
A_L = [(12, 'A4'), (14, 'A3'), (3, 'A2'), (5, 'A1'),
       (11, 'B4'), (15, 'B3'), (2, 'B2'), (6, 'B1'), (7, 'C0')]
A_R = [(9, 'C4'), None, (10, 'S4'), (13, 'S3'), (1, 'S2'), (4, 'S1')]

def mark(lst, m):
    return [None if it is None else (it[0], it[1] + m) for it in lst]

u1, h1 = chip(250, 70, 165, 'U1  74HC283', 'binary adder  A + B',
              mark(A_L, '₁'), mark(A_R, '₁'),
              'pin 16 = VCC   pin 8 = GND')
u2, h2 = chip(770, 70, 165, 'U2  74HC283', 'binary adder  Z + 6',
              mark(A_L, '₂'), mark(A_R, '₂'),
              'pin 16 = VCC   pin 8 = GND')
u5, h5 = chip(1075, 118, 175, 'U5  CD4511', 'BCD → 7-segment',
              [(6, 'D'), (2, 'C'), (1, 'B'), (7, 'A'), (3, '/LT'), (4, '/BL'), (5, 'LE')],
              [(13, 'a'), (12, 'b'), (11, 'c'), (10, 'd'), (9, 'e'), (15, 'f'), (14, 'g')],
              'pin 16 = VDD   pin 8 = VSS')

# gates
e('<text class="grp" x="430" y="508">U3  74HC08</text>')
e('<text class="grp" x="605" y="508">U4  74HC32</text>')
a1i, a1j, a1o = gate('and', 448, 530, 'U3A', (1, 2, 3))
a2i, a2j, a2o = gate('and', 448, 620, 'U3B', (4, 5, 6))
o1i, o1j, o1o = gate('or', 620, 536, 'U4A', (1, 2, 3))
o2i, o2j, o2o = gate('or', 620, 630, 'U4B', (4, 5, 6))

# ------------------------------------------------------------- operands
e('<text class="grp" x="52" y="92">SW1  operand entry</text>')
sw = {}
for i, nm in enumerate(['A3', 'A2', 'A1', 'A0', 'B3', 'B2', 'B1', 'B0']):
    py = 140 + i * 30
    e('<rect class="sw" x="52" y="%.1f" width="54" height="20" rx="3"/>' % (py - 10))
    e('<text class="swl" x="79" y="%.1f">%s</text>' % (py + 4, nm))
    sw[nm] = (106, py)
for i, (s, d) in enumerate([('A3', 'A4₁'), ('A2', 'A3₁'), ('A1', 'A2₁'), ('A0', 'A1₁'),
                            ('B3', 'B4₁'), ('B2', 'B3₁'), ('B1', 'B2₁'), ('B0', 'B1₁')]):
    net(sw[s], u1[d], ORA, mid=150 + i * 11)

# ------------------------------------------------------------------ Z bus
ZL = {'Z3': u1['S4₁'], 'Z2': u1['S3₁'], 'Z1': u1['S2₁'], 'Z0': u1['S1₁']}
K = u1['C4₁']
for i, (z, d) in enumerate([('Z3', 'A4₂'), ('Z2', 'A3₂'), ('Z1', 'A2₂'), ('Z0', 'A1₂')]):
    net(ZL[z], u2[d], BLU, label=z, mid=470 + i * 16, lx=440)
for src, dst, lbl in ((ZL['Z3'], a1i, 'Z3'), (ZL['Z2'], a1j, 'Z2'),
                      (ZL['Z3'], a2i, 'Z3'), (ZL['Z1'], a2j, 'Z1')):
    net(src, dst, BLU, mid=(a1i[0] - 70))
net(K, o2j, BLU, label='K = Cy', mid=560, lx=470)

# ------------------------------------------------------------ correction
net(a1o, o1i, GRN, label='Z3·Z2', mid=596, lx=556)
net(a2o, o1j, GRN, label='Z3·Z1', mid=584, lx=556)
net(o1o, o2i, GRN, label='Z3(Z2+Z1)', mid=712, lx=730)
cpt = o2o
net(cpt, u2['B3₂'], GRN, label='C', mid=745, lx=760)
net(cpt, u2['B2₂'], GRN, mid=745)
e('<text class="nl" x="800" y="676" fill="%s">C = K + Z3·Z2 + Z3·Z1</text>' % GRN)

# ground / constant ties
for nm, lbl in (('C0₁', '0'), ('C0₂', '0'), ('B4₂', '0'), ('B1₂', '0')):
    (px, py) = u1[nm] if nm.endswith('₁') else u2[nm]
    e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>'
      % (px - 34, py, px, py, BLK))
    e('<text class="gndl" x="%.1f" y="%.1f">%s</text>' % (px - 40, py + 4, lbl))
    e('<circle class="nd" cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (px, py, BLK))

# --------------------------------------------------------------- S bus
for i, (s, d) in enumerate([('S4₂', 'D'), ('S3₂', 'C'), ('S2₂', 'B'), ('S1₂', 'A')]):
    net(u2[s], u5[d], PUR, label='S%d' % (3 - i), mid=975 + i * 16, lx=965)
e('<text class="nc" x="958" y="%.1f">n/c</text>' % (u2['C4₂'][1] + 4))

# CD4511 control strapping
for nm, lbl, col in (('/LT', '+5 V', RED), ('/BL', '+5 V', RED), ('LE', 'GND', BLK)):
    (px, py) = u5[nm]
    e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>'
      % (px - 46, py, px, py, col))
    e('<text class="gndl" x="%.1f" y="%.1f" fill="%s">%s</text>' % (px - 52, py + 4, col, lbl))
    e('<circle class="nd" cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (px, py, col))

# --------------------------------------------------------------- display
DX, DY = 1360, 170
e('<rect class="disp" x="%.1f" y="%.1f" width="104" height="168" rx="6"/>' % (DX, DY))
sx, sy, sw_, sh = DX + 30, DY + 34, 44, 46
def seg(x1, y1, x2, y2, nm, lx, ly):
    e('<line class="segl" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (x1, y1, x2, y2))
    e('<text class="segt" x="%.1f" y="%.1f">%s</text>' % (lx, ly, nm))
seg(sx, sy, sx + sw_, sy, 'a', sx + sw_ / 2, sy - 7)
seg(sx + sw_, sy, sx + sw_, sy + sh, 'b', sx + sw_ + 10, sy + sh / 2)
seg(sx + sw_, sy + sh, sx + sw_, sy + 2 * sh, 'c', sx + sw_ + 10, sy + 1.5 * sh)
seg(sx, sy + 2 * sh, sx + sw_, sy + 2 * sh, 'd', sx + sw_ / 2, sy + 2 * sh + 15)
seg(sx, sy + sh, sx, sy + 2 * sh, 'e', sx - 10, sy + 1.5 * sh)
seg(sx, sy, sx, sy + sh, 'f', sx - 10, sy + sh / 2)
seg(sx, sy + sh, sx + sw_, sy + sh, 'g', sx + sw_ / 2, sy + sh - 7)
e('<text class="pkgs" x="%.1f" y="%.1f">DS1 common cathode</text>' % (DX + 52, DY + 162))
for i, nm in enumerate(['a', 'b', 'c', 'd', 'e', 'f', 'g']):
    (px, py) = u5[nm]
    ry = py
    e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>'
      % (px, ry, px + 36, ry, SEG))
    e('<rect class="res" x="%.1f" y="%.1f" width="22" height="9" rx="2"/>' % (px + 36, ry - 4.5))
    e('<path class="net" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" stroke="%s"/>'
      % (px + 58, ry, px + 70 + i * 6, ry, px + 70 + i * 6, DY + 22 + i * 6, DX, DY + 22 + i * 6, SEG))
    e('<text class="segp" x="%.1f" y="%.1f">%s</text>' % (px + 47, ry - 8, nm))
e('<text class="gndl2" x="%.1f" y="%.1f">330 Ω × 7</text>' % (u5['a'][0] + 47, u5['a'][1] - 24))
e('<text class="pkgs" x="%.1f" y="%.1f">CC → GND</text>' % (DX + 52, DY + 182))

# ------------------------------------------------------------- tens LED
lx0, ly0 = cpt[0], 700
e('<path class="net" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" stroke="%s"/>'
  % (cpt[0], cpt[1], cpt[0] + 190, cpt[1], cpt[0] + 190, ly0 - 4, GRN))
e('<rect class="res" x="%.1f" y="%.1f" width="22" height="9" rx="2"/>' % (cpt[0] + 179, ly0))
e('<circle class="ledd" cx="%.1f" cy="%.1f" r="9"/>' % (cpt[0] + 190, ly0 + 36))
e('<path class="net" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" stroke="%s"/>'
  % (cpt[0] + 190, ly0 + 9, cpt[0] + 190, ly0 + 27, cpt[0] + 190, ly0 + 27, GRN))
e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>'
  % (cpt[0] + 190, ly0 + 45, cpt[0] + 190, ly0 + 62, BLK))
e('<line class="gnds" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
  % (cpt[0] + 176, ly0 + 62, cpt[0] + 204, ly0 + 62))
e('<text class="gndl2" x="%.1f" y="%.1f">LED1  tens digit</text>' % (cpt[0] + 212, ly0 + 40))
e('<text class="gndl2" x="%.1f" y="%.1f">330 Ω</text>' % (cpt[0] + 212, ly0 + 9))

# ------------------------------------------------------------ board rule
e('<line class="div" x1="1035" y1="40" x2="1035" y2="740"/>')
e('<text class="bdiv" x="1027" y="36">BOARD 1</text>')
e('<text class="bdiv2" x="1043" y="36">BOARD 2</text>')

svg = ('<svg id="fl" viewBox="0 0 1560 790" xmlns="http://www.w3.org/2000/svg" role="img" '
       'aria-label="Signal flow and pinout diagram for the HOP 2 BCD adder">'
       + '\n'.join(out) + '</svg>')
io.open('flow.svg', 'w', encoding='utf-8').write(svg)
print('ok', len(svg))
