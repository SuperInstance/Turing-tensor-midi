# Turing Tensor MIDI

**The eyes and ears for the FLUX Conservation Spectral System.**

## What Changed

Turing was a voice assistant — a JARVIS clone that listened and spoke. Now it's something different: a **web frontend** for the FLUX Tensor MIDI system.

It doesn't talk. It *shows*.

## The Concept

### Conservation Spectral Theory × Real-Time Music

Every piece of music carries spectral energy. FLUX asks a simple question: **how well does a chord progression preserve that energy?** The answer is the **Conservation Ratio (CR)**.

| Progression | CR | Interpretation |
|---|---|---|
| ii–V–I in C | 0.94 | +4.06σ above random — near-perfect conservation |
| 12-Bar Blues | 0.87 | High preservation — the blues *works* for a reason |
| Chromatic Run | 0.62 | Moderate — energy leaks but stays coherent |
| Random Notes | 0.31 | Baseline — what you get without structure |

The frontend visualizes these ratios in real time as music plays, coloring each note on the piano roll by its conservation quality.

### T-Minus Musical Prediction

Instead of predicting rocket launches, Turing now predicts **musical events**:

- **T-8 bars** → bridge predicted
- **T-4 bars** → key change predicted
- **T-2 beats** → chord change predicted
- **T-1 beat** → note resolution predicted

These countdowns let agents in the Plato fleet synchronize their responses — the harmony agent knows the bridge is coming, the bass agent knows to prepare for the key change.

### The FLUX Translation Pipeline

Music moves through representations:

```
MIDI → Spectral → Tensor → Output
```

Each stage transforms the signal. The frontend shows what's happening at each step — the original MIDI note, its spectral decomposition, its tensor representation with CR, and the final conserved output.

### Plato Agent Fleet — Musical Rooms

Plato agents don't all listen to the same thing. They decompose music into **rooms**:

- 🎸 **Bass Room** — bass line analysis, groove locking
- 🎹 **Melody Room** — contour tracking, pitch detection
- 🎻 **Harmony Room** — voice leading, CR monitoring
- 🥁 **Rhythm Room** — tempo tracking, grid synchronization

Each room has dedicated agents. The fleet panel shows who's listening where.

## Architecture

```
index.html   — Single-page app shell
style.css    — Dark theme (superinstance.ai palette)
app.js       — Piano roll, CR tracker, T-minus predictor, FLUX translator, agent router
```

All client-side. No build step. No backend. Open `index.html` and go.

## Running

```bash
# Just open it
open index.html

# Or serve it
python3 -m http.server 8000
```

## Tech Stack

- Vanilla HTML/CSS/JS — no frameworks
- Canvas API for piano roll rendering
- CSS custom properties for theming
- Dark theme: `--bg: #0a0a0a`, `--accent: #00ff88`, `--accent2: #ff6b35`

## Why

Because conservation spectral theory deserves a face. Because music analysis should be something you can *see*, not just read about. Because the Plato agents needed a dashboard.

Turing used to be a voice. Now it's a window.

---

*Part of the SuperInstance FLUX ecosystem.*
