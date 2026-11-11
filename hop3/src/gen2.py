# -*- coding: utf-8 -*-
"""Signal-flow / pinout diagram for the HOP 3 BCD counter."""
import io

out = []


def e(s):
    out.append(s)


RED, BLK, ORA = '#d1495b', '#3d4451', '#e08b2a'
BLU, GRN, PUR, SEG = '#2f7fd6', '#2f9e5e', '#8b5cf6', '#c2410c'
TIM = '#a0522d'

PINR = 8.5


def pindot(x, y, num):
    e('<circle class="pd" cx="%.1f" cy="%.1f" r="%.1f"/>' % (x, y, PINR))
    e('<text class="pn" x="%.1f" y="%.1f">%d</text>' % (x, y + 3.1, num))


def chip(x, y, w, title, sub, left, right, extra=None):
    """left/right: list of (pin, name) or None for a blank slot."""
    n = max(len(left), len(right))
    pitch = 30
    h = (n + 1) * pitch + 20
    e('<g class="chip">')
    e('<rect class="pkg" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5"/>' % (x, y, w, h))
    e('<text class="pkgt" x="%.1f" y="%.1f">%s</text>' % (x + w / 2, y + 26, title))
    e('<text class="pkgs" x="%.1f" y="%.1f">%s</text>' % (x + w / 2, y + 42, sub))
    e('<line class="pkgr" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
      % (x + 10, y + 54, x + w - 10, y + 54))
    pos = {}
    for side, lst in (('L', left), ('R', right)):
        for i, item in enumerate(lst):
            if item is None:
                continue
            pin, name = item
            py = y + 70 + i * pitch
            px = x if side == 'L' else x + w
            pindot(px, py, pin)
            if side == 'L':
                e('<text class="pname pl" x="%.1f" y="%.1f">%s</text>' % (x + PINR + 7, py + 3.6, name))
            else:
                e('<text class="pname pr" x="%.1f" y="%.1f">%s</text>' % (x + w - PINR - 7, py + 3.6, name))
            pos[name] = (px, py)
    if extra:
        e('<text class="pkgx" x="%.1f" y="%.1f">%s</text>' % (x + w / 2, y + h + 18, extra))
    e('</g>')
    return pos, h


def poly(pts, color, dash=False, end=True):
    d = 'M ' + ' L '.join('%.1f %.1f' % p for p in pts)
    e('<path class="net%s" d="%s" stroke="%s"/>' % (' dash' if dash else '', d, color))
    if end:
        e('<circle class="nd" cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (pts[-1][0], pts[-1][1], color))


def net(p1, p2, color, label=None, mid=None, lx=None, dash=False):
    (x1, y1), (x2, y2) = p1, p2
    mx = mid if mid is not None else (x1 + x2) / 2
    poly([(x1, y1), (mx, y1), (mx, y2), (x2, y2)], color, dash)
    if label:
        tx = lx if lx is not None else (x1 + mx) / 2
        e('<text class="nl" x="%.1f" y="%.1f" fill="%s">%s</text>' % (tx, y1 - 6, color, label))


def tie(p, text, color, side='L', length=40):
    (px, py) = p
    x2 = px - length if side == 'L' else px + length
    e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (x2, py, px, py, color))
    cls = 'gndl' if side == 'L' else 'gndl2'
    tx = x2 - 6 if side == 'L' else x2 + 6
    e('<text class="%s" x="%.1f" y="%.1f" fill="%s">%s</text>' % (cls, tx, py + 4, color, text))
    e('<circle class="nd" cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (px, py, color))


def res_v(x, y1, y2, label, color, sub=None):
    """Vertical resistor between y1 and y2 with leads."""
    my = (y1 + y2) / 2
    e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (x, y1, x, y2, color))
    e('<rect class="res" x="%.1f" y="%.1f" width="10" height="30" rx="2"/>' % (x - 5, my - 15))
    e('<text class="gndl2" x="%.1f" y="%.1f">%s</text>' % (x + 12, my + 1, label))
    if sub:
        e('<text class="gndl2 sm" x="%.1f" y="%.1f">%s</text>' % (x + 12, my + 13, sub))


def gnd(x, y):
    e('<line class="gnds" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (x - 12, y, x + 12, y))
    e('<line class="gnds" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (x - 7, y + 5, x + 7, y + 5))
    e('<line class="gnds" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (x - 2.5, y + 10, x + 2.5, y + 10))


def vcc(x, y, label='+5 V'):
    e('<line class="gnds" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (x - 12, y, x + 12, y))
    e('<text class="gndl2 ctr" x="%.1f" y="%.1f" fill="%s">%s</text>' % (x, y - 7, RED, label))


def node(x, y, color):
    e('<circle class="nd" cx="%.1f" cy="%.1f" r="4" fill="%s"/>' % (x, y, color))


# ------------------------------------------------------------------ chips
u1, h1 = chip(300, 110, 150, 'U1  NE555', 'astable clock',
              [(8, 'VCC'), (7, 'DISCH'), (6, 'THRES'), (2, 'TRIG')],
              [(3, 'OUT'), (4, 'RESET'), (5, 'CTRL'), (1, 'GND')])
u2, h2 = chip(640, 110, 165, 'U2  74LS90', 'decade counter',
              [(14, 'CKA'), (1, 'CKB'), (2, 'R0(1)'), (3, 'R0(2)'), (6, 'R9(1)'), (7, 'R9(2)')],
              [(12, 'QA'), (9, 'QB'), (8, 'QC'), (11, 'QD')],
              'pin 5 = VCC   pin 10 = GND')
u3, h3 = chip(1000, 110, 175, 'U3  CD4511', 'BCD → 7-segment',
              [(7, 'A'), (1, 'B'), (2, 'C'), (6, 'D'), (3, '/LT'), (4, '/BL'), (5, 'LE')],
              [(13, 'a'), (12, 'b'), (11, 'c'), (10, 'd'), (9, 'e'), (15, 'f'), (14, 'g')],
              'pin 16 = VDD   pin 8 = VSS')

# ------------------------------------------------------------------ timing network
e('<text class="grp" x="40" y="92">TIMING NETWORK</text>')
NX = 120
vcc(NX, 120)
res_v(NX, 120, 190, 'R1  10 kΩ', TIM, '= R_A')
TMID = (NX, 205)
node(*TMID, TIM)
e('<text class="nl" x="%.1f" y="%.1f" fill="%s">T_MID</text>' % (NX - 34, TMID[1] + 4, TIM))
net(TMID, u1['DISCH'], TIM, mid=230)
# the six-resistor chain, drawn as six small bodies
y = 205
e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (NX, 205, NX, 420, TIM))
for i in range(6):
    yy = 222 + i * 28
    e('<rect class="res" x="%.1f" y="%.1f" width="10" height="20" rx="2"/>' % (NX - 5, yy))
e('<text class="gndl2" x="%.1f" y="%.1f">R2–R7</text>' % (NX + 12, 280))
e('<text class="gndl2" x="%.1f" y="%.1f">6 × 10 kΩ</text>' % (NX + 12, 294))
e('<text class="gndl2 sm" x="%.1f" y="%.1f">R_B = 60 kΩ + RV1</text>' % (NX + 12, 308))
# RV1 as a rheostat
ry = 410
e('<rect class="res pot" x="%.1f" y="%.1f" width="10" height="34" rx="2"/>' % (NX - 5, ry))
e('<path class="net" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" stroke="%s"/>'
  % (NX + 26, ry + 17, NX + 8, ry + 17, NX + 8, ry + 17, TIM))
e('<path class="arrow" d="M %.1f %.1f l 7 -4 l 0 8 z"/>' % (NX + 6, ry + 17))
e('<path class="net" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f" stroke="%s"/>'
  % (NX + 26, ry + 17, NX + 26, ry - 4, NX, ry - 4, TIM))
e('<text class="gndl2" x="%.1f" y="%.1f">RV1  10 kΩ</text>' % (NX + 34, ry + 14))
e('<text class="gndl2 sm" x="%.1f" y="%.1f">wiper tied to one end</text>' % (NX + 34, ry + 27))
TCAP = (NX, 470)
e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (NX, ry + 34, NX, TCAP[1], TIM))
node(*TCAP, TIM)
e('<text class="nl" x="%.1f" y="%.1f" fill="%s">T_CAP</text>' % (NX - 34, TCAP[1] + 4, TIM))
net(TCAP, u1['THRES'], TIM, mid=250)
net((250, u1['THRES'][1]), u1['TRIG'], TIM, mid=250)
node(250, u1['THRES'][1], TIM)
# C1
e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (NX, TCAP[1], NX, 510, TIM))
e('<line class="capl" x1="%.1f" y1="510" x2="%.1f" y2="510"/>' % (NX - 14, NX + 14))
e('<path class="capc" d="M %.1f 520 Q %.1f 514 %.1f 520"/>' % (NX - 14, NX, NX + 14))
e('<text class="gndl2" x="%.1f" y="%.1f">+</text>' % (NX - 24, 506))
e('<text class="gndl2" x="%.1f" y="%.1f">C1  10 µF</text>' % (NX + 22, 518))
e('<line class="net" x1="%.1f" y1="520" x2="%.1f" y2="545" stroke="%s"/>' % (NX, NX, BLK))
gnd(NX, 545)
e('<text class="eqs" x="40" y="600">f = 1.44 / ((R_A + 2 R_B) C)  ≈ 0.96 to 1.11 Hz</text>')

# 555 fixed pins
tie(u1['VCC'], '+5 V', RED, 'L', 34)
tie(u1['RESET'], '+5 V', RED, 'R', 34)
tie(u1['GND'], 'GND', BLK, 'R', 34)
e('<text class="nc" x="%.1f" y="%.1f">open</text>' % (u1['CTRL'][0] + 40, u1['CTRL'][1] + 4))

# ------------------------------------------------------------------ clock
CLKY = u1['OUT'][1]
net(u1['OUT'], u2['CKA'], ORA, label='CLK', mid=560, lx=520)
# optional indicator
lx = 520
e('<path class="net dash" d="M %.1f %.1f L %.1f %.1f" stroke="%s"/>' % (lx, CLKY, lx, 360, ORA))
node(lx, CLKY, ORA)
e('<rect class="res" x="%.1f" y="%.1f" width="10" height="30" rx="2"/>' % (lx - 5, 300))
e('<circle class="ledd" cx="%.1f" cy="%.1f" r="9"/>' % (lx, 380))
e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (lx, 389, lx, 410, BLK))
gnd(lx, 410)
e('<text class="gndl2" x="%.1f" y="%.1f">R19 330 Ω</text>' % (lx + 12, 318))
e('<text class="gndl2" x="%.1f" y="%.1f">LED1 clock</text>' % (lx + 14, 384))
e('<text class="gndl2 sm" x="%.1f" y="%.1f">optional</text>' % (lx + 14, 397))

# ------------------------------------------------------------------ counter
for nm in ('R0(1)', 'R0(2)', 'R9(1)', 'R9(2)'):
    tie(u2[nm], '0', BLK, 'L', 30)
# QA back into CKB: out the right side, over the top, down the left side
qa, ckb = u2['QA'], u2['CKB']
poly([qa, (qa[0] + 26, qa[1]), (qa[0] + 26, 84), (ckb[0] - 46, 84), (ckb[0] - 46, ckb[1]), ckb], BLU)
node(qa[0] + 26, qa[1], BLU)
e('<text class="nl" x="%.1f" y="%.1f" fill="%s">QA → CKB : ÷2 then ÷5 = BCD</text>'
  % ((qa[0] + ckb[0]) / 2 - 10, 78, BLU))

# ------------------------------------------------------------------ Q bus and pull-ups
pairs = [('QA', 'A', 'Q0'), ('QB', 'B', 'Q1'), ('QC', 'C', 'Q2'), ('QD', 'D', 'Q3')]
for i, (src, dst, lbl) in enumerate(pairs):
    net(u2[src], u3[dst], BLU, label=lbl, lx=920)
PUX = [838, 860, 882, 904]
PUY = 420
e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (PUX[0] - 10, PUY, PUX[-1] + 10, PUY, RED))
e('<text class="gndl2 ctr" x="%.1f" y="%.1f" fill="%s">+5 V</text>' % ((PUX[0] + PUX[-1]) / 2, PUY + 16, RED))
for i, (src, dst, lbl) in enumerate(pairs):
    x = PUX[i]
    y = u3[dst][1]
    node(x, y, BLU)
    e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (x, y, x, PUY, BLU))
    e('<rect class="res" x="%.1f" y="%.1f" width="8" height="22" rx="2"/>' % (x - 4, 360))
e('<text class="gndl2" x="%.1f" y="%.1f">R8\u2013R11  4 \u00d7 4.7 k\u03a9 pull-ups</text>' % (PUX[0] - 14, PUY + 34))
e('<text class="gndl2 sm" x="%.1f" y="%.1f">lift 74LS highs to CMOS levels</text>' % (PUX[0] - 14, PUY + 47))

# CD4511 control strapping
for nm, lbl, col in (('/LT', '+5 V', RED), ('/BL', '+5 V', RED), ('LE', 'GND', BLK)):
    tie(u3[nm], lbl, col, 'L', 40)

# ------------------------------------------------------------------ display
DX, DY = 1360, 150
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
    (px, py) = u3[nm]
    e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (px, py, px + 36, py, SEG))
    e('<rect class="res" x="%.1f" y="%.1f" width="22" height="9" rx="2"/>' % (px + 36, py - 4.5))
    e('<path class="net" d="M %.1f %.1f L %.1f %.1f L %.1f %.1f L %.1f %.1f" stroke="%s"/>'
      % (px + 58, py, px + 70 + i * 6, py, px + 70 + i * 6, DY + 22 + i * 6, DX, DY + 22 + i * 6, SEG))
    e('<text class="segp" x="%.1f" y="%.1f">%s</text>' % (px + 47, py - 8, nm))
e('<text class="gndl2" x="%.1f" y="%.1f">R12–R18  7 × 330 Ω</text>' % (u3['a'][0] + 22, u3['a'][1] - 26))
e('<line class="net" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s"/>' % (DX + 52, DY + 168, DX + 52, DY + 200, BLK))
gnd(DX + 52, DY + 200)
e('<text class="gndl2" x="%.1f" y="%.1f">CC pins 3 and 8</text>' % (DX + 64, DY + 190))

svg = ('<svg id="fl" viewBox="0 0 1520 640" xmlns="http://www.w3.org/2000/svg" role="img" '
       'aria-label="Signal flow and pinout diagram for the HOP 3 BCD counter">'
       + '\n'.join(out) + '</svg>')
io.open('flow.svg', 'w', encoding='utf-8').write(svg)
print('ok', len(svg))
