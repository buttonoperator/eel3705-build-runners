# EEL 3705 Hands-On Project 3: BCD Counter Wiring Sheet

Single-digit decimal counter. An NE555 astable clock at approximately 1 Hz drives a 74LS90
decade counter. Its BCD output is decoded by a CD4511 onto a common-cathode seven-segment
display, which shows 0 through 9 repeating.

Every component is drawn from the course kit (kit ID `SVCCustomUSF-FDC-v4`). The netlist is
that of `HOP1_FullAdder_PCB/04_HOP3_Counter_Spec.md` Rev B. This sheet adds the breadboard
placement and one optional clock indicator (Section 8).

## 1. Bill of Materials

### Integrated Circuits

| Ref | Part | Pkg | Function |
|---|---|---|---|
| U1 | NE555P | DIP-8 | Astable clock |
| U2 | SN74LS90 | DIP-14 | Decade counter, wired ÷2 then ÷5 for 8421 BCD |
| U3 | CD4511BE | DIP-16 | BCD-to-7-segment latch/decoder/driver |
| DS1 | EL7SD-CC-RD-39-01 | 10-pin | 0.39 in red seven-segment, common cathode |

### Passives and Discretes

| Ref | Qty | Value | Function |
|---|---|---|---|
| R1 | 1 | 10 kΩ | 555 R_A |
| R2–R7 | 6 | 10 kΩ | 555 R_B series chain, 60 kΩ total |
| RV1 | 1 | 10 kΩ pot | Rate trim, wired as a rheostat |
| C1 | 1 | 10 µF 100 V electrolytic | 555 timing |
| R8–R11 | 4 | 4.7 kΩ | Pull-ups on Q0–Q3 |
| R12–R18 | 7 | 330 Ω | Segment current limiting, a–g |
| R19 | 1 | 330 Ω | Clock indicator, optional |
| LED1 | 1 | Green 3 mm | Clock indicator, optional |

Kit consumption: 7 of 10 × 10 kΩ, 4 of 10 × 4.7 kΩ, 8 of 10 × 330 Ω, the only pot and
the only capacitor. The kit's single breadboard and power module carry the whole build. The 9 V
battery is the only item not in the kit.

### Designator Cross-Reference

The breadboard uses its own designators. The PCB spec numbers continue from HOP-1.

| Breadboard | PCB spec | Breadboard | PCB spec |
|---|---|---|---|
| U1 | U4 | R8, R9, R10, R11 | R16, R17, R18, R19 |
| U2 | U5 | R12–R18 (a–g) | R9–R15 (a–g) |
| U3 | U6 | C1 | C5 |
| R1 | R20 | RV1 | RV1 |
| R2–R7 | R21–R26 | R19, LED1 | not in Rev B |

## 2. Signal Nomenclature

| Name | Description |
|---|---|
| T_MID | 555 DISCH node, R_A / R_B junction |
| T_CAP | 555 timing capacitor node, TRIG and THRES |
| CLK | 555 output to counter clock |
| Q0..Q3 | BCD count, Q0 = LSB. Q0 is QA, Q1 QB, Q2 QC, Q3 QD |
| a..g | CD4511 segment outputs |

## 3. Clock Timing

```
t_high = 0.693 (R_A + R_B) C        R_A = 10 kΩ
t_low  = 0.693  R_B        C        R_B = 60 kΩ + RV1 (0 to 10 kΩ)
f      = 1.44 / ((R_A + 2 R_B) C)   C   = 10 µF
```

| RV1 | Period | f | Ten counts |
|---|---|---|---|
| 0 Ω | 0.90 s | 1.11 Hz | 9.0 s |
| 5 kΩ | 0.97 s | 1.03 Hz | 9.7 s |
| 10 kΩ | 1.04 s | 0.96 Hz | 10.4 s |

C1's 20 % tolerance and leakage dominate the error. See Section 9.

## 4. Pinouts

### NE555 (DIP-8)

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | GND | 8 | VCC |
| 2 | TRIG | 7 | DISCH |
| 3 | OUT | 6 | THRES |
| 4 | RESET | 5 | CTRL |

### SN74LS90 (DIP-14)

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | CKB | 14 | CKA |
| 2 | R0(1) | 13 | NC |
| 3 | R0(2) | 12 | QA |
| 4 | NC | 11 | QD |
| 5 | **VCC** | 10 | **GND** |
| 6 | R9(1) | 9 | QB |
| 7 | R9(2) | 8 | QC |

Power is pins 5 and 10, not 14 and 7.

### CD4511BE (DIP-16)

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | B (bit 1) | 16 | VDD |
| 2 | C (bit 2) | 15 | f |
| 3 | /LT | 14 | g |
| 4 | /BL | 13 | a |
| 5 | LE | 12 | b |
| 6 | D (bit 3, MSB) | 11 | c |
| 7 | A (bit 0, LSB) | 10 | d |
| 8 | VSS | 9 | e |

### DS1 (10-pin, assumed map, confirm with the lamp test)

| Pin | Segment | Pin | Segment |
|---|---|---|---|
| 1 | e | 10 | g |
| 2 | d | 9 | f |
| 3 | CC | 8 | CC |
| 4 | c | 7 | a |
| 5 | dp | 6 | b |

## 5. Breadboard Placement

830-point board, 63 columns, rows A–E below the channel and F–J above it. The power module
sits over columns 1–5 and feeds both rail pairs at 5 V. Every chip has its notch to the left
and pin 1 at the lower left.

| Part | Columns | Rows |
|---|---|---|
| U1 NE555 | 18–21 | E / F |
| U2 74LS90 | 25–31 | E / F |
| U3 CD4511 | 36–43 | E / F |
| DS1 | 58–62 | D / H (0.6 in row spacing) |

No lead shares a hole with a chip pin or with another lead. Each connection to a pin lands in a
free hole of that pin's strip.

## 6. Net List

Top rails: outer + , inner −. Bottom rails: inner −, outer +.

### Power and Tie-Offs

| From | To |
|---|---|
| U1 pin 8, col 18 J | top + |
| U1 pin 1, col 18 A | bottom − |
| U2 pin 5, col 29 A | bottom + |
| U2 pin 10, col 29 J | top − |
| U3 pin 16, col 36 J | top + |
| U3 pin 8, col 43 A | bottom − |
| U1 pin 4 RESET, col 21 A | bottom + |
| U1 pin 5 CTRL | open |
| U2 pins 2, 3, 6, 7 (R0, R9), cols 26, 27, 30, 31 A | bottom − |
| U3 pin 3 /LT, col 38 A | bottom + |
| U3 pin 4 /BL, col 39 A | bottom + |
| U3 pin 5 LE, col 40 A | bottom − |

### Clock

| Part / wire | From | To |
|---|---|---|
| R1 10 kΩ | top + | col 19 J (T_MID, U1 pin 7) |
| R2 10 kΩ | col 19 H | col 16 H |
| R3 10 kΩ | col 16 I | col 13 I |
| R4 10 kΩ | col 13 H | col 10 H |
| R5 10 kΩ | col 10 I | col 7 I |
| R6 10 kΩ | col 7 G | col 7 D (across the channel) |
| R7 10 kΩ | col 7 C | col 10 C |
| RV1 | cols 10, 11, 12 A | pin 1, wiper, pin 3 |
| wiper tie | col 11 B | col 10 B |
| T_CAP wire | col 12 C (RV1 pin 3) | col 19 C (U1 pin 2 TRIG) |
| TRIG–THRES wire | col 19 D | col 20 G (U1 pin 6) |
| C1 10 µF | + col 20 J | − top − |

### Counter

| From | To |
|---|---|
| U1 pin 3 OUT, col 20 C | U2 pin 14 CKA, col 25 J |
| U2 pin 12 QA, col 27 I | U2 pin 1 CKB, col 25 D |

### Q Bus and Pull-Ups

| From | To | Pull-up, 4.7 kΩ to bottom + |
|---|---|---|
| U2 pin 12 QA (Q0), col 27 G | U3 pin 7 A, col 42 D | R8 at col 42 A |
| U2 pin 9 QB (Q1), col 30 G | U3 pin 1 B, col 36 D | R9 at col 36 A |
| U2 pin 8 QC (Q2), col 31 G | U3 pin 2 C, col 37 D | R10 at col 37 A |
| U2 pin 11 QD (Q3), col 28 G | U3 pin 6 D, col 41 D | R11 at col 41 A |

### Segment Network

Seven 330 Ω across the channel, row G to row D. Bank order is the CD4511 output order
reversed, so the feed wires nest without crossing.

| Seg | U3 pin, col | Resistor, col | DS1 pin, landing |
|---|---|---|---|
| e | 9, 43 | R16, 47 | 1, col 58 A |
| d | 10, 42 | R15, 48 | 2, col 59 A |
| c | 11, 41 | R14, 49 | 4, col 61 A |
| b | 12, 40 | R13, 50 | 6, col 62 J |
| a | 13, 39 | R12, 51 | 7, col 61 J |
| g | 14, 38 | R18, 52 | 10, col 58 J |
| f | 15, 37 | R17, 53 | 9, col 59 J |

Feeds land in row J of the resistor column. Outputs leave from row A of the resistor column.

DS1 pin 3, col 60 A to bottom −. DS1 pin 8, col 60 J to top −.

## 7. Interface Notes

**74LS90 to CD4511.** 74LS guarantees V_OH ≥ 2.7 V. The CD4511 at V_DD = 5 V needs
V_IH ≥ 3.5 V. R8–R11 lift Q0–Q3 to near 5 V when high and add 1.06 mA each to the counter's
8 mA sink load when low. They are mandatory.

**555 to 74LS90.** The 555 output swings close to the rails and drives one 74LS input with
margin. No conditioning is needed.

**CD4511 to DS1.** Outputs source current, so the display must be common cathode. Segment
current is (5.0 − 0.5 − 2.0) / 330 ≈ 7.6 mA.

**No decoupling.** C1 is the only capacitor in the kit. At a 1 Hz clock with one fast edge
per cycle, this is acceptable on a breadboard.

## 8. Optional Clock Indicator

Not in the Rev B spec. R19 (330 Ω) from U1 pin 3 strip (col 20 B) to col 23 B, and LED1 (green)
from col 23 A, anode, to the bottom − rail. It blinks at the clock rate and makes the clock
visible in the demo video. It loads the 555 output by about 5 mA, which is negligible against
its 200 mA rating, and does not affect timing.

## 9. Verification

| Test | Condition | Expected |
|---|---|---|
| Rail short | Unpowered, + to − | Open |
| Timing chain | Unpowered, top + to col 20, RV1 end to end | 70–80 kΩ, monotonic |
| Supply current | 5 V applied | About 60–85 mA |
| Clock | LED1 or U1 pin 3 | About 1 Hz square wave |
| Pull-ups | Q0–Q3 high level | ≥ 4.9 V |
| Lamp test | U3 pin 3 to GND momentarily | All 7 segments lit |
| Sequence | Observe DS1 | 0–9 repeating, no blanks, no skips |
| Rate | Time ten counts | 9.0–10.4 s |

Fault interpretation:

- **Blank digit.** A Q-line fault reaching U3 as code 10–15. A pull-up is missing or the wrong value.
- **Counts 0–4 and repeats.** The QA-to-CKB jumper is open.
- **Digits out of order.** The clock is on CKB instead of CKA.
- **Display frozen on one digit.** The clock is not reaching CKA, or a reset input is floating high.
- **Clock will not start.** Check RESET and the TRIG–THRES jumper, then C1 leakage. At the
  top of each charge C1 receives only 24 µA, and leakage approaching that stalls the
  oscillator. Leave it powered for a few minutes to reform it. Failing that, bridge one or two
  chain resistors with a jumper and accept a faster clock.

The counter has no reset input: the kit contains no momentary switch. It may start on any
digit.
