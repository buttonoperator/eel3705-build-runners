# BCD Counter, 0 to 9 — Build Runner

An interactive, single-file build guide for a breadboard decimal counter: a 555 astable clock,
a 74LS90 decade counter, a CD4511 decoder, and a common-cathode seven-segment display.

Built for EEL 3705 (Fundamentals of Digital Circuits, University of South Florida),
Hands-On Project 3. Every part comes from the course kit, on the kit's one 830-point board.

### ▶ [Open the build runner](https://buttonoperator.github.io/eel3705-build-runners/hop3/)

One HTML file, no build step, no dependencies. Works offline once loaded. Clone the repo and
open [`index.html`](index.html) directly if you would rather not rely on the network at the
bench.

---

## What the circuit does

The 555 ticks about once a second. The 74LS90 counts the falling edges in BCD. The CD4511
turns the count into segment drive, and the display shows 0 through 9 on repeat.

| Chip | Part | Takes in | Puts out | Meaning |
|---|---|---|---|---|
| U1 | NE555 | C1 voltage | `CLK` | square wave, 0.96–1.11 Hz |
| U2 | 74LS90 | `CLK` | `Q3..Q0` | count of falling edges, 0–9 in 8421 BCD |
| U3 | CD4511 | `Q3..Q0` | `a`–`g` | segment drive |
| DS1 | 7-seg CC | `a`–`g` | light | the digit |

### The clock

```
f = 1.44 / ((R_A + 2 R_B) C)      R_A = 10 kΩ, R_B = 60 kΩ + RV1, C = 10 µF
```

The kit contains exactly one capacitor, 10 µF, and no resistor above 10 kΩ. A 1 s period
needs R_A + 2R_B near 144 kΩ, so R_B is built from six 10 kΩ in series, with the 10 kΩ pot
as trim. RV1 end to end moves the period from 0.90 s to 1.04 s.

### The counter

The 74LS90 is a ÷2 (CKA → QA) and a ÷5 (CKB → QB QC QD) in one package. Clock into CKA and
feed QA into CKB, and the outputs count `0000` to `1001` in 8421 BCD, then wrap. Wired the
other way round, it counts in 5421 bi-quinary and the decoder shows the wrong digits.

All four reset inputs are grounded. A floating 74LS input reads as high, and R9(1) and R9(2)
both high freeze the count at 9.

### The interface trap

> The 74LS90 is TTL and guarantees only 2.7 V on a high output. The CD4511 is CMOS and needs
> 3.5 V. Without the four 4.7 kΩ pull-ups on Q0–Q3, the counter counts correctly and the
> display still shows wrong or blank digits.

### Expected behaviour

| Observation | Meaning |
|---|---|
| 0–9 repeating, about 1 s per digit | Correct |
| A digit blank | Pull-up fault, code 10–15 reaching the decoder |
| 0–4 repeating | QA → CKB jumper open |
| Digits out of order | Clock on CKB instead of CKA |
| Frozen on one digit | No clock at CKA, or a reset input floating |
| LED1 dark or solid | Clock stopped: check RESET, the TRIG–THRES jumper, then C1 leakage |

---

## What the page does

- **27 steps, one at a time.** Each shows where on the board you are, what to do, and a table
  of exact hole-to-hole connections.
- **A live IC pin map.** Every package with every pin numbered and labelled by the net it
  carries. Pins light blue for the current step and green once wired.
- **A step-scoped breadboard diagram.** Every drawn element carries its step index, so only
  the current step's connections are lit; completed wires dim, future wires ghost.
- **Every lead in a real, free hole.** Wires never share a pin's own hole. They land in a free
  hole of that pin's strip, which is how the board is actually built.
- **Click any pin to trace its net.** One click on Q0 lights U2 pins 1 and 12, U3 pin 7, the
  QA-to-CKB jumper, the Q bus wire and the pull-up, and dims everything else.
- **A clock you can run.** The rail holds the count, a slider for RV1, and a run button that
  clocks the counter at the real 555 rate, high for t_high and low for t_low, stepping on the
  falling edge exactly as the 74LS90 does. Each chip's readout under the pin map reads
  **NOW** once its step is done and **TARGET → step N** before that.
- **A seven-segment preview** using the CD4511's real patterns, including its tail-less 6 and 9.
- **"Why this step."** The steps that carry design intent say what that wiring is for.
- **Progress saved** in `localStorage`, with per-step undo.
- Reference drawers: what each chip is doing, signal flow schematic, pinouts, parts list with
  kit quantities, troubleshooting, and verification.

### Keyboard

| Key | Action |
|---|---|
| <kbd>←</kbd> <kbd>→</kbd> | previous / next step |
| <kbd>+</kbd> <kbd>−</kbd> | zoom the diagrams |
| <kbd>0</kbd> | reset diagram zoom |
| <kbd>.</kbd> | one clock edge |

---

## Notes on the parts

**Kit parts only.** The parts list drawer shows each part used against the kit quantity. The
only outside item is the 9 V battery for the power module.

**U2 is powered on pins 5 and 10**, not 14 and 7. It is the only 74LS90 in the kit.

**The display pins land in rows D and H.** The 0.39 in display's pin rows are 0.6 in apart.
Its pinout is the common map for this size; the kit part ships without a datasheet, so the
lamp test at step 26 is the confirmation.

**Strap the CD4511's control pins.** `/LT` (3) and `/BL` (4) to +5 V, `LE` (5) to GND.
Grounding `/LT` momentarily lights all seven segments, which is a one-wire test of the whole
display subassembly.

**No decoupling.** The kit's one capacitor is the timing capacitor. At 1 Hz this is
acceptable.

---

## Rebuilding

The page is generated. `index.html` is committed, so you only need this if you change a
diagram or a step.

```bash
python build.py
```

Requires Python 3 and nothing else. The build runs three generators and then verifies the
result before writing:

- the breadboard drawing is rebuilt into a netlist (strips, rails, parts) and compared net by
  net against the Rev B spec; any pin on the wrong net, or two leads in one hole, stops the build
- every pin reference in the step data resolves to a real element in the pin map
- every breadboard step stamp falls inside the step range, and the step count agrees between
  the generator and the page
- every step that lists connections actually draws them
- required element IDs appear exactly once

| File | Produces |
|---|---|
| `src/gen.py` | `bb.svg`: hole-accurate breadboard placement, stamped by step, plus the netlist check |
| `src/gen2.py` | `flow.svg`: signal flow schematic |
| `src/gen3.py` | `chips.svg`: pin map in signal order, every pin and readout addressable |
| `src/build.py` | inlines all three into `src/template.html` → `index.html` |

See [WIRING.md](WIRING.md) for the full net list in plain text, including the designator
cross-reference to the PCB spec.

---

## License

MIT. See [LICENSE](../LICENSE).
