# -*- coding: utf-8 -*-
"""Live IC pin map: every package, every pin, addressable by id.

Each pin carries two labels. The bold one is the SIGNAL this build puts on that
pin; the small grey one is the chip's OWN pin name from its datasheet. They
differ for two reasons: the datasheet numbers its bits from 1 while this build
numbers them from 0, and the same physical pin carries a different signal in U1
than it does in U2.

Each pin also carries data-net, so the page can highlight a whole net at once.
Each package has a readout box underneath for its logic levels.
"""
import io

out = []
def e(s):
    out.append(s)

PITCH = 26.0
BW = 104.0
PADW, PADH = 23.0, 16.0
HEAD = 44.0
CHIP_Y = 40.0
RO_Y = 330.0
STEP_X = 175.0
ROW = 150.0
ROH = 50.0

# Datasheet pin names, pin 1 first.
ADDER = ['Σ2', 'B2', 'A2', 'Σ1', 'A1', 'B1', 'C0', 'GND',
         'C4', 'Σ4', 'B4', 'A4', 'Σ3', 'A3', 'B3', 'VCC']
QUAD  = ['1A', '1B', '1Y', '2A', '2B', '2Y', 'GND',
         '3Y', '3A', '3B', '4Y', '4A', '4B', 'VCC']
DIPSW = ['SW1', 'SW2', 'SW3', 'SW4', 'SW5', 'SW6', 'SW7', 'SW8',
         'SW8', 'SW7', 'SW6', 'SW5', 'SW4', 'SW3', 'SW2', 'SW1']
C4511 = ['B', 'C', '/LT', '/BL', 'LE', 'D', 'A', 'VSS',
         'e', 'd', 'c', 'b', 'a', 'g', 'f', 'VDD']
SEG7  = ['e', 'd', 'CC', 'c', 'dp', 'b', 'a', 'CC', 'f', 'g']

CHIPS = [
    # ref, part, signal per pin, datasheet name per pin, column
    ('SW1', 'DIP switch',
     ['A0', 'A1', 'A2', 'A3', 'B0', 'B1', 'B2', 'B3',
      '+5', '+5', '+5', '+5', '+5', '+5', '+5', '+5'], DIPSW, 0),
    ('U1', '74HC283',
     ['Z1', 'B1', 'A1', 'Z0', 'A0', 'B0', '0', 'GND',
      'K', 'Z3', 'B3', 'A3', 'Z2', 'A2', 'B2', '+5'], ADDER, 1),
    ('U3', '74HC08',
     ['Z3', 'Z2', 'Z3·Z2', 'Z3', 'Z1', 'Z3·Z1', 'GND',
      'n/c', '0', '0', 'n/c', '0', '0', '+5'], QUAD, 2),
    ('U4', '74HC32',
     ['Z3·Z2', 'Z3·Z1', 'N3', 'N3', 'K', 'C', 'GND',
      'n/c', '0', '0', 'n/c', '0', '0', '+5'], QUAD, 3),
    ('U2', '74HC283',
     ['S1', 'C', 'Z1', 'S0', 'Z0', '0', '0', 'GND',
      'n/c', 'S3', '0', 'Z3', 'S2', 'Z2', 'C', '+5'], ADDER, 4),
    ('U5', 'CD4511',
     ['S1', 'S2', '/LT', '/BL', 'LE', 'S3', 'S0', 'GND',
      'e', 'd', 'c', 'b', 'a', 'g', 'f', '+5'], C4511, 5),
    ('DS1', '7-seg CC',
     ['e', 'd', 'CC', 'c', 'dp', 'b', 'a', 'CC', 'f', 'g'], SEG7, 6),
]

def net_of(sig):
    """Normalise a pin's signal to the net it actually sits on."""
    if sig in ('0', 'GND', 'CC', 'VSS', 'LE'):
        return 'GND'
    if sig in ('+5', 'VCC', 'VDD', '/LT', '/BL'):
        return 'VCC'
    if sig in ('n/c', 'dp'):
        return ''
    return sig

def draw(ref, part, names, dsn, col):
    x = 30.0 + col * STEP_X
    y, roy = CHIP_Y, RO_Y
    n = len(names)
    half = n // 2
    h = HEAD + half * PITCH + 10
    e('<g class="pkgwrap">')
    e('<rect class="cbody" id="c-%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="6"/>'
      % (ref, x, y, BW, h))
    e('<path class="cnotch" d="M %.1f %.1f a 9 9 0 0 0 18 0"/>' % (x + BW / 2 - 9, y))
    e('<text class="cref" x="%.1f" y="%.1f">%s</text>' % (x + BW / 2, y + 22, ref))
    e('<text class="cpart" x="%.1f" y="%.1f">%s</text>' % (x + BW / 2, y + 35, part))

    def pin(p, side, py):
        sig = names[p - 1]
        net = net_of(sig)
        chip = dsn[p - 1] if dsn[p - 1] != sig else ''
        e('<g class="pin%s" id="p-%s-%d"%s>'
          % ('' if net else ' dead', ref, p, (' data-net="%s"' % net) if net else ''))
        if side == 'L':
            e('<rect class="pad" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3"/>'
              % (x - PADW - 1, py - PADH / 2, PADW, PADH))
            e('<text class="pnum" x="%.1f" y="%.1f">%d</text>' % (x - PADW / 2 - 1, py + 3.8, p))
            e('<text class="pnet pnl" x="%.1f" y="%.1f">%s</text>' % (x + 7, py + 0.8, sig))
            if chip:
                e('<text class="pds pnl" x="%.1f" y="%.1f">%s</text>' % (x + 7, py + 10.4, chip))
        else:
            e('<rect class="pad" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3"/>'
              % (x + BW + 1, py - PADH / 2, PADW, PADH))
            e('<text class="pnum" x="%.1f" y="%.1f">%d</text>'
              % (x + BW + PADW / 2 + 1, py + 3.8, p))
            e('<text class="pnet pnr" x="%.1f" y="%.1f">%s</text>' % (x + BW - 7, py + 0.8, sig))
            if chip:
                e('<text class="pds pnr" x="%.1f" y="%.1f">%s</text>'
                  % (x + BW - 7, py + 10.4, chip))
        e('</g>')

    for i in range(half):
        py = y + HEAD + i * PITCH + PADH / 2 + 2
        pin(i + 1, 'L', py)
        pin(n - i, 'R', py)

    e('<line class="rostem" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>'
      % (x + BW / 2, y + h, x + BW / 2, roy))
    rx = x - PADW - 1
    e('<g class="ro" id="ro-%s">' % ref)
    e('<rect class="robox" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="7"/>'
      % (rx, roy, ROW, ROH))
    e('<rect class="robar" x="%.1f" y="%.1f" width="3.5" height="%.1f" rx="2"/>'
      % (rx, roy + 7, ROH - 14))
    e('<text class="rotag" id="rotag-%s" x="%.1f" y="%.1f">TARGET</text>'
      % (ref, rx + 11, roy + 15))
    e('<text class="rol1" id="rol1-%s" x="%.1f" y="%.1f"></text>' % (ref, rx + 11, roy + 30))
    e('<text class="rol2" id="rol2-%s" x="%.1f" y="%.1f"></text>' % (ref, rx + 11, roy + 43))
    e('</g>')
    e('</g>')
    return roy + ROH

maxb = 0
for ref, part, names, dsn, col in CHIPS:
    maxb = max(maxb, draw(ref, part, names, dsn, col))

W = 30 + (len(CHIPS) - 1) * STEP_X + BW + PADW + 40
svg = ('<svg id="cm" viewBox="0 0 %.0f %.0f" xmlns="http://www.w3.org/2000/svg" role="img" '
       'aria-label="Pin map of every IC in the build, with the logic levels each one produces">'
       % (W, maxb + 20)) + '\n'.join(out) + '</svg>'
io.open('chips.svg', 'w', encoding='utf-8').write(svg)
print('ok', len(svg), 'w', W, 'h', maxb + 20)
