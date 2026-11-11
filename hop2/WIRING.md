# EEL 3705 Hands-On Project 2: BCD Adder Wiring Sheet

Single-digit BCD adder. Two 4-bit BCD operands in, corrected BCD sum on a
CD4511-driven seven-segment display, tens digit on a discrete LED.
Sum range 0 to 18, so the tens digit is one bit.

## 1. Bill of Materials

### Integrated Circuits

| Ref | Part | Pkg | Function |
|---|---|---|---|
| U1 | 74HC283 | DIP-16 | 4-bit binary adder, computes A + B |
| U2 | 74HC283 | DIP-16 | 4-bit binary adder, adds the +6 correction |
| U3 | 74HC08 | DIP-14 | Quad 2-input AND, correction terms |
| U4 | 74HC32 | DIP-14 | Quad 2-input OR, correction detect |
| U5 | CD4511BE | DIP-16 | BCD-to-7-segment latch/decoder/driver |

**Use the HC family, not LS.** The CD4511 is CMOS. At VDD = 5 V its input
high threshold (VIH) is 3.5 V minimum, while a 74LS output guarantees only
2.7 V (VOH min). A 74LS283 driving the CD4511 directly is operating outside
the specified input range and will read sum bits incorrectly or
intermittently. HC outputs swing to within ~0.1 V of the rail and drive the
CD4511 with full margin.

If only 74LS parts are available, see Section 7 for the required pull-up
modification.

### Passives and Discretes

| Qty | Value / Part | Function |
|---|---|---|
| 1 | 8-position DIP switch (CTS 206-8 or equiv.) | Operand entry, 4 positions per operand |
| 8 | 10 kΩ | Switch pull-downs, one per input bit |
| 7 | 330 Ω | Segment current limiting |
| 1 | 330 Ω | Tens LED current limiting |
| 1 | Common-cathode 7-segment display | Ones digit |
| 1 | LED, any color | Tens digit |
| 5 | 0.1 µF ceramic | Decoupling, one per IC across VCC/GND |

The display **shall** be common cathode. The CD4511 has active-high outputs
and sources segment current. A common-anode display will not illuminate.

## 2. Signal Nomenclature

| Name | Description |
|---|---|
| A3..A0 | Operand A, A0 = LSB |
| B3..B0 | Operand B, B0 = LSB |
| Z3..Z0 | U1 sum, uncorrected |
| K | U1 carry-out |
| C | Correction / tens digit |
| S3..S0 | U2 sum, corrected BCD ones digit |

## 3. Correction Logic

The uncorrected sum is invalid BCD when it exceeds 9. The condition is:

```
C = K + Z3·Z2 + Z3·Z1
```

When C = 1, binary 0110 (decimal 6) is added to Z to restore BCD, and C is
the tens digit. Gate usage is 2 of 4 AND gates and 2 of 4 OR gates.

## 4. Pinouts

### 74HC283 / 74LS283 (DIP-16), A1 = LSB

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | Σ2 | 16 | VCC |
| 2 | B2 | 15 | B3 |
| 3 | A2 | 14 | A3 |
| 4 | Σ1 | 13 | Σ3 |
| 5 | A1 | 12 | A4 |
| 6 | B1 | 11 | B4 |
| 7 | C0 (carry in) | 10 | Σ4 |
| 8 | GND | 9 | C4 (carry out) |

### 74HC08 and 74HC32 (DIP-14), identical pin assignment

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | 1A | 14 | VCC |
| 2 | 1B | 13 | 4B |
| 3 | 1Y | 12 | 4A |
| 4 | 2A | 11 | 4Y |
| 5 | 2B | 10 | 3B |
| 6 | 2Y | 9 | 3A |
| 7 | GND | 8 | 3Y |

### CD4511BE (DIP-16)

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | B (input bit 1) | 16 | VDD |
| 2 | C (input bit 2) | 15 | f |
| 3 | /LT (lamp test) | 14 | g |
| 4 | /BL (blanking) | 13 | a |
| 5 | LE (latch enable) | 12 | b |
| 6 | D (input bit 3, MSB) | 11 | c |
| 7 | A (input bit 0, LSB) | 10 | d |
| 8 | VSS (GND) | 9 | e |

Control pin strapping, required:

- Pin 3 (/LT) to +5 V. Tying it low lights all segments.
- Pin 4 (/BL) to +5 V. Tying it low blanks the display.
- Pin 5 (LE) to GND. Tying it high freezes the last value.

These three pins **shall not** be left floating. CMOS inputs left open will
drift and produce erratic display behavior.

## 5. Net List

### Power

Every IC: VCC/VDD to +5 V, GND/VSS to 0 V, 0.1 µF from VCC to GND placed
across the package.

### Input Stage

For each of the 8 input bits: DIP switch one side to +5 V, other side to the
signal node; 10 kΩ from the signal node to GND.

### U1, A + B

| U1 Pin | Connect To |
|---|---|
| 5 (A1) | A0 |
| 3 (A2) | A1 |
| 14 (A3) | A2 |
| 12 (A4) | A3 |
| 6 (B1) | B0 |
| 2 (B2) | B1 |
| 15 (B3) | B2 |
| 11 (B4) | B3 |
| 7 (C0) | GND |
| 4 (Σ1) | Z0 |
| 1 (Σ2) | Z1 |
| 13 (Σ3) | Z2 |
| 10 (Σ4) | Z3 |
| 9 (C4) | K |

### U3, 74HC08 AND

| U3 Pin | Connect To |
|---|---|
| 1 (1A) | Z3 |
| 2 (1B) | Z2 |
| 3 (1Y) | N1 = Z3·Z2 |
| 4 (2A) | Z3 |
| 5 (2B) | Z1 |
| 6 (2Y) | N2 = Z3·Z1 |

Unused inputs (pins 9, 10, 12, 13) **shall** be tied to GND. Floating CMOS
inputs cause oscillation and elevated supply current.

### U4, 74HC32 OR

| U4 Pin | Connect To |
|---|---|
| 1 (1A) | N1 |
| 2 (1B) | N2 |
| 3 (1Y) | N3 |
| 4 (2A) | N3 |
| 5 (2B) | K |
| 6 (2Y) | C |

Unused inputs (pins 9, 10, 12, 13) tied to GND.

### U2, +6 Correction

| U2 Pin | Connect To |
|---|---|
| 5 (A1) | Z0 |
| 3 (A2) | Z1 |
| 14 (A3) | Z2 |
| 12 (A4) | Z3 |
| 6 (B1) | GND |
| 2 (B2) | C |
| 15 (B3) | C |
| 11 (B4) | GND |
| 7 (C0) | GND |
| 4 (Σ1) | S0 |
| 1 (Σ2) | S1 |
| 13 (Σ3) | S2 |
| 10 (Σ4) | S3 |
| 9 (C4) | no connection |

B inputs are wired 0-C-C-0, which presents 0110 when C = 1 and 0000 when
C = 0. U2's carry-out is unused; the tens digit comes from C, not from C4.

### U5, CD4511 and Display

| U5 Pin | Connect To |
|---|---|
| 7 (A) | S0 |
| 1 (B) | S1 |
| 2 (C) | S2 |
| 6 (D) | S3 |
| 3 (/LT) | +5 V |
| 4 (/BL) | +5 V |
| 5 (LE) | GND |
| 13 (a) | 330 Ω to display segment a |
| 12 (b) | 330 Ω to display segment b |
| 11 (c) | 330 Ω to display segment c |
| 10 (d) | 330 Ω to display segment d |
| 9 (e) | 330 Ω to display segment e |
| 15 (f) | 330 Ω to display segment f |
| 14 (g) | 330 Ω to display segment g |

Display common cathode pins to GND.

### Tens LED

C to 330 Ω to LED anode; LED cathode to GND. A 74HC32 output sources 4 mA at
VOH = 4.4 V, which drives a standard LED at approximately 8 mA through 330 Ω.

## 6. Verification

| A | B | Expected Display | Expected LED | Internal Check |
|---|---|---|---|---|
| 0 | 0 | 0 | off | Z = 0000, K = 0, C = 0 |
| 3 | 4 | 7 | off | Z = 0111, no correction |
| 7 | 2 | 9 | off | Z = 1001, boundary, C must be 0 |
| 5 | 5 | 0 | on | Z = 1010, K = 0, C via Z3·Z1 |
| 8 | 9 | 7 | on | Z = 10001, C via K |
| 9 | 9 | 8 | on | Z = 10010, C via K, worst case |

The 7 + 2 = 9 case is the critical negative test. If the LED illuminates
there, the correction logic is asserting on a valid BCD sum; check that the
AND gates are wired to Z2 and Z1 and not to Z1 and Z0.

Inputs above 1001 are outside the specified operand range. Behavior is
undefined and the CD4511 will blank the display for codes 1010 through 1111.

## 7. 74LS Substitution

If 74LS283/74LS08/74LS32 must be used:

1. Install a 4.7 kΩ pull-up resistor from each of S3, S2, S1, S0 to +5 V.
   This raises the LS high level from 2.7 V to approximately 5 V, satisfying
   the CD4511 VIH = 3.5 V requirement.
2. Tie unused LS gate inputs to +5 V through a 1 kΩ resistor, or to GND
   directly. Do not tie TTL inputs directly to +5 V.
3. A 74LS32 output sources only 0.4 mA at VOH. The tens LED will be dim.
   Either accept reduced brightness with a 1 kΩ series resistor, or drive the
   LED in sink configuration from an inverted copy of C.

## 8. Layout Notes

The project statement rejects builds with long looping jumper wires. Required
practice:

- Use pre-cut solid 22 AWG wire routed flat against the board at right angles.
- Place U1, U2, U5 in a left-to-right row following the signal flow; place U3
  and U4 in a second row near U1's sum outputs.
- Run the +5 V and GND rails first, then decoupling caps, then the signal nets
  in the order of Section 5.
- Keep wire color consistent: red for +5 V, black for GND, one color per
  functional group (operand A, operand B, Z bus, S bus).
