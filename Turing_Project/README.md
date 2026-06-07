# Turing v2.0 — Voice Assistant for SuperInstance

> British personality. z.ai + DeepInfra AI. Self-Improving Band integration. MIDI tensor mapping.

## What's New in 2.0

- **Restructured** from monolithic 542-line `App.py` into a proper Python package
- **AI Engine**: z.ai GLM-5.1 (primary) + DeepInfra Seed-2.0-mini (fallback) — **no OpenAI**
- **Self-Improving Band**: Voice-controlled ensemble with conservation law (γ + H = C)
- **MIDI Tensor Map**: velocity→weight, pitch class→dimension, rhythm→temporal kernel
- **261 site shortcuts** loaded from `config/sites.yaml` (not hardcoded)
- **25+ tests** with full module coverage

## Quick Start

```bash
cd Turing_Project
pip install -e ".[all]"

# Set API keys
cp .env.example .env
# Edit .env with your keys

# Run
python -m turing
```

## Configuration

### Environment Variables

| Variable | Purpose |
|---|---|
| `ZAI_API_KEY` | z.ai GLM-5.1 API key |
| `DEEPINFRA_API_KEY` | DeepInfra fallback key |
| `WEATHER_API_KEY` | Visual Crossing weather |
| `NEWS_API_KEY` | NewsAPI key |

### YAML Config

- `config/default.yaml` — default settings
- `config/sites.yaml` — 261 website shortcuts
- `config/user.yaml` — user overrides (gitignored)

## Architecture

```
turing/
├── config.py            # Env + YAML configuration
├── engine/
│   ├── speech.py        # SpeechRecognition wrapper
│   ├── tts.py           # pyttsx3 text-to-speech
│   ├── completion.py    # Provider protocol + z.ai/DeepInfra
│   └── ai.py            # Primary → fallback router
├── skills/
│   ├── web.py           # Site shortcuts, search
│   ├── weather.py       # Weather reports
│   ├── news.py          # News headlines
│   ├── music.py         # YouTube playback
│   ├── system.py        # Greetings, time, identity
│   └── band.py          # Band voice control
├── router.py            # Command dispatch → skill chain
├── listener.py          # Wake word + active mode
├── sites.py             # YAML site registry
├── midi/
│   ├── listener.py      # MIDI input → commands
│   ├── synth.py         # Band agents → MIDI output
│   └── tensor_map.py    # MIDI ↔ tensor ops
└── band/
    ├── agent.py         # Spectral identity + conservation
    ├── ensemble.py      # Hodge tempo negotiation
    ├── tminus.py        # Local countdown clocks
    └── protocol.py      # Inter-agent messages
```

## AI Providers

| Provider | Model | Role | Base URL |
|---|---|---|---|
| z.ai | GLM-5.1 | Primary | `https://api.z.ai/v1` |
| DeepInfra | Seed-2.0-mini | Fallback | `https://api.deepinfra.com/v1/openai` |

API-agnostic — swap providers in `config/default.yaml`. No OpenAI, no OpenRouter, no Ollama.

## Voice Commands

- "Hello Turing" — greeting
- "What's the time" — current time
- "Open YouTube" — open a site (261 shortcuts)
- "Search for quantum computing" — Google search
- "What's the weather in Tokyo" — weather report
- "News about AI" — latest headlines
- "Play Bohemian Rhapsody on YouTube" — music
- "Start a Bb blues with 5 agents" — band session
- "Tell horns to lay out" — band control
- "What's the spectral state" — band diagnostics

## Self-Improving Band

The killer feature. Each agent has:
- **Spectral identity** — fundamental frequency, harmonics, phase
- **Conservation envelope** — γ + H = C (spectral energy + harmonic entropy = constant)
- **Dial position** — creative parameter [0, 1]
- **T-minus clock** — local countdown, no shared clock

The ensemble negotiates tempo via **Hodge decomposition** and enforces conservation across all agents.

## MIDI Tensor Mapping

| MIDI | Tensor |
|---|---|
| Velocity (0–127) | Weight [0, 1] |
| Pitch class (0–11) | Harmonic dimension |
| Rhythm / beat position | Temporal kernel [0, 1] |

## Development

```bash
pip install -e ".[dev]"
pytest               # run 25+ tests
ruff check turing/   # lint
```

## License

MIT — See [LICENSE](../LICENSE)
