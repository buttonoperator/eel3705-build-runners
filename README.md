# EEL 3705 Build Runners

Interactive, single-file build guides for the EEL 3705 (Fundamentals of Digital Circuits,
University of South Florida) hands-on projects. Each page walks a breadboard build one
connection at a time, with a live IC pin map, a step-scoped breadboard diagram, and net
tracing by clicking any pin.

### ▶ [Open the index](https://buttonoperator.github.io/eel3705-build-runners/)

| Project | Circuit | Page | Source |
|---|---|---|---|
| HOP 2 | Single-digit BCD adder: two 74HC283s with +6 correction, CD4511, 7-segment | [open](https://buttonoperator.github.io/eel3705-build-runners/hop2/) | [`hop2/`](hop2/) |
| HOP 3 | BCD counter 0–9: NE555 clock, 74LS90, CD4511, 7-segment, kit parts only | [open](https://buttonoperator.github.io/eel3705-build-runners/hop3/) | [`hop3/`](hop3/) |

Each project folder holds its own README, a plain-text wiring sheet (`WIRING.md`), the
committed single-file page (`index.html`), and the generators in `src/`.

## Rebuilding

```bash
python build.py          # rebuild both pages
python build.py hop3     # rebuild one
```

Requires Python 3 and nothing else. Each project's build regenerates its SVG diagrams, inlines
them into `src/template.html`, runs its checks, and writes `index.html`. The HOP 3 build also
rebuilds the circuit from its breadboard drawing and compares it net by net against the design
spec before writing anything.

## License

MIT. See [LICENSE](LICENSE).
