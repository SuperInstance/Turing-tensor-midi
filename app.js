/* ── Turing Tensor MIDI — app.js ── */

// ─── Conservation Ratio Data ───
const CR_DATA = {
  'ii-V-I': { cr: 0.94, sigma: 4.06, label: 'ii–V–I in C' },
  'blues':   { cr: 0.87, sigma: 2.80, label: '12-Bar Blues' },
  'chromatic': { cr: 0.62, sigma: 1.40, label: 'Chromatic Run' },
  'random':  { cr: 0.31, sigma: 0.00, label: 'Random Notes' },
};

// ─── Note names ───
const NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'];

// ─── Piano Roll ───
class PianoRoll {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.keys = 88;
    this.startMidi = 21; // A0
    this.activeNotes = new Map(); // midi -> { velocity, cr, time }
    this.resize();
    window.addEventListener('resize', () => this.resize());
    canvas.addEventListener('click', (e) => this.handleClick(e));
  }

  resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width - 40;
    this.canvas.height = 320;
    this.draw();
  }

  isBlack(midi) {
    const n = midi % 12;
    return [1, 3, 6, 8, 10].includes(n);
  }

  noteName(midi) {
    const octave = Math.floor(midi / 12) - 1;
    return NOTE_NAMES[midi % 12] + octave;
  }

  draw() {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    ctx.clearRect(0, 0, w, h);

    // Layout: left side = labels, right = roll area
    const labelW = 36;
    const rollW = w - labelW;
    const keyH = h / this.keys;

    // Draw keys (bottom = low, top = high, reversed so low is at bottom)
    for (let i = 0; i < this.keys; i++) {
      const midi = this.startMidi + i;
      const y = h - (i + 1) * keyH;
      const black = this.isBlack(midi);
      const active = this.activeNotes.has(midi);

      // Key background
      if (active) {
        const noteData = this.activeNotes.get(midi);
        const cr = noteData.cr;
        if (cr >= 0.85) ctx.fillStyle = 'rgba(0,255,136,0.3)';
        else if (cr >= 0.50) ctx.fillStyle = 'rgba(240,192,64,0.3)';
        else ctx.fillStyle = 'rgba(255,107,53,0.3)';
      } else {
        ctx.fillStyle = black ? '#1a1a1a' : '#2a2a2a';
      }
      ctx.fillRect(0, y, labelW, keyH);

      // Label
      const nName = this.noteName(midi);
      if (nName.includes('C') && !nName.includes('#')) {
        ctx.fillStyle = active ? '#fff' : '#888';
        ctx.font = '9px monospace';
        ctx.fillText(nName, 4, y + keyH / 2 + 3);
      }

      // Roll area — grid lines
      ctx.fillStyle = black ? '#0e0e0e' : '#141414';
      ctx.fillRect(labelW, y, rollW, keyH);
      ctx.strokeStyle = '#1a1a1a';
      ctx.beginPath();
      ctx.moveTo(labelW, y + keyH);
      ctx.lineTo(w, y + keyH);
      ctx.stroke();

      // Active note glow in roll
      if (active) {
        const noteData = this.activeNotes.get(midi);
        const age = Date.now() - noteData.time;
        const alpha = Math.max(0.1, 1 - age / 3000);
        const cr = noteData.cr;
        let color;
        if (cr >= 0.85) color = `rgba(0,255,136,${alpha})`;
        else if (cr >= 0.50) color = `rgba(240,192,64,${alpha})`;
        else color = `rgba(255,107,53,${alpha})`;
        ctx.fillStyle = color;
        ctx.fillRect(labelW, y, rollW * 0.6, keyH);

        // CR label
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 10px monospace';
        ctx.fillText(`CR=${cr.toFixed(2)}`, labelW + 6, y + keyH / 2 + 3);
      }
    }

    // Border between labels and roll
    ctx.strokeStyle = '#333';
    ctx.beginPath();
    ctx.moveTo(labelW, 0);
    ctx.lineTo(labelW, h);
    ctx.stroke();
  }

  handleClick(e) {
    const rect = this.canvas.getBoundingClientRect();
    const y = e.clientY - rect.top;
    const keyH = this.canvas.height / this.keys;
    const idx = Math.floor((this.canvas.height - y) / keyH);
    const midi = this.startMidi + idx;
    if (midi >= this.startMidi && midi < this.startMidi + this.keys) {
      const cr = 0.3 + Math.random() * 0.7;
      this.activeNotes.set(midi, { velocity: 80 + Math.floor(Math.random() * 47), cr, time: Date.now() });
      this.draw();
      // Auto-release after a moment
      setTimeout(() => { this.activeNotes.delete(midi); this.draw(); }, 2000);
    }
  }

  activateNote(midi, velocity, cr) {
    if (midi >= this.startMidi && midi < this.startMidi + this.keys) {
      this.activeNotes.set(midi, { velocity, cr, time: Date.now() });
      this.draw();
    }
  }

  deactivateNote(midi) {
    this.activeNotes.delete(midi);
    this.draw();
  }

  clear() {
    this.activeNotes.clear();
    this.draw();
  }
}

// ─── Conservation Tracker ───
class ConservationTracker {
  constructor() {
    this.currentCR = 0;
    this.history = [];
  }

  compute(progression) {
    if (CR_DATA[progression]) {
      this.currentCR = CR_DATA[progression].cr;
    } else {
      this.currentCR = 0.3 + Math.random() * 0.65;
    }
    this.history.push({ cr: this.currentCR, time: Date.now() });
    return this.currentCR;
  }

  getLive() { return this.currentCR; }
}

// ─── T-Minus Predictor ───
class TMinusPredictor {
  constructor(container) {
    this.container = container;
    this.events = [
      { label: 'Bridge', unit: 'bars', total: 8, remaining: 8 },
      { label: 'Key Change', unit: 'bars', total: 4, remaining: 4 },
      { label: 'Chord Change', unit: 'beats', total: 2, remaining: 2 },
      { label: 'Note Resolution', unit: 'beat', total: 1, remaining: 1 },
    ];
    this.render();
  }

  tick() {
    this.events.forEach(ev => {
      ev.remaining = Math.max(0, ev.remaining - 0.1);
      if (ev.remaining <= 0) ev.remaining = ev.total;
    });
    this.render();
  }

  render() {
    const items = this.container.querySelectorAll('.tminus-item');
    items.forEach((item, i) => {
      const ev = this.events[i];
      const countEl = item.querySelector('.tminus-countdown');
      const barEl = item.querySelector('.tminus-fill');
      const r = ev.remaining;
      const unit = r === 1 ? ev.unit.replace(/s$/, '') : ev.unit;
      countEl.textContent = `T-${r < 1 ? r.toFixed(1) : Math.ceil(r)} ${unit}`;
      barEl.style.width = `${(1 - r / ev.total) * 100}%`;
    });
  }
}

// ─── FLUX Translator ───
class FluxTranslator {
  constructor() {
    this.stages = ['midi', 'spectral', 'tensor', 'output'];
    this.currentStage = 0;
    this.stageData = {
      midi: 'Note: C4 Vel: 96',
      spectral: 'f₀=261.6Hz A=-6.2dB',
      tensor: 'CR=0.94 dim=12',
      output: 'Conserved phrase',
    };
  }

  cycle() {
    // Highlight next stage
    const stages = document.querySelectorAll('.flux-stage');
    stages.forEach(s => s.classList.remove('active'));
    this.currentStage = (this.currentStage + 1) % 4;
    stages[this.currentStage].classList.add('active');

    // Update data with slight variation
    const notes = ['C4','E4','G4','D4','F#4','A4','Bb4'];
    const note = notes[Math.floor(Math.random() * notes.length)];
    const vel = 60 + Math.floor(Math.random() * 60);
    const freqs = [261.6, 329.6, 392.0, 293.7, 370.0, 440.0, 466.2];
    const freq = freqs[Math.floor(Math.random() * freqs.length)];
    const cr = (0.5 + Math.random() * 0.5).toFixed(2);

    document.querySelector('#flux-midi .flux-data').textContent = `Note: ${note} Vel: ${vel}`;
    document.querySelector('#flux-spectral .flux-data').textContent = `f₀=${freq}Hz A=${(-3 - Math.random()*8).toFixed(1)}dB`;
    document.querySelector('#flux-tensor .flux-data').textContent = `CR=${cr} dim=12`;
    document.querySelector('#flux-output .flux-data').textContent = `Conserved phrase`;
  }
}

// ─── Agent Router ───
class AgentRouter {
  constructor() {
    this.rooms = {
      bass:    ['plato-bass-01', 'harmonics-α', 'groove-lock'],
      melody:  ['plato-melody-01', 'contour-β', 'pitch-track'],
      harmony: ['plato-harmony-01', 'voicelead-γ', 'cr-monitor'],
      rhythm:  ['plato-rhythm-01', 'tempo-δ', 'grid-sync'],
    };
    this.render();
  }

  render() {
    Object.entries(this.rooms).forEach(([room, agents]) => {
      const list = document.getElementById(`agents-${room}`);
      if (!list) return;
      list.innerHTML = agents.map(a => `<li>${a}</li>`).join('');
    });
  }

  addAgent(room, name) {
    if (this.rooms[room]) {
      this.rooms[room].push(name);
      this.render();
    }
  }

  removeAgent(room, name) {
    if (this.rooms[room]) {
      this.rooms[room] = this.rooms[room].filter(a => a !== name);
      this.render();
    }
  }
}

// ─── Demo Sequence ───
function runDemo(piano, tracker, predictor, translator) {
  const progressions = ['ii-V-I', 'blues', 'chromatic', 'random'];
  let progIdx = 0;

  // ii-V-I notes (C major)
  const phrases = {
    'ii-V-I': [
      [62,65,69], // Dm
      [67,71,74], // G
      [60,64,67], // C
    ],
    'blues': [
      [48,55,60], // C blues
      [53,58,60],
      [55,59,60],
    ],
    'chromatic': [
      [60],[61],[62],[63],[64],[65],[66],[67],
    ],
    'random': [
      [55+Math.floor(Math.random()*24)],
      [55+Math.floor(Math.random()*24)],
      [55+Math.floor(Math.random()*24)],
    ],
  };

  let phraseIdx = 0;

  function step() {
    const prog = progressions[progIdx];
    const cr = tracker.compute(prog);
    const phrase = phrases[prog];
    const chord = phrase[phraseIdx % phrase.length];

    // Activate notes
    piano.clear();
    chord.forEach(midi => piano.activateNote(midi, 90, cr));

    // Update live CR
    document.getElementById('cr-live').textContent = cr.toFixed(2);

    // Highlight matching CR card
    document.querySelectorAll('.cr-card').forEach(card => {
      card.style.borderColor = card.dataset.progression === prog ? '#00ff88' : '#222';
    });

    // Cycle translator
    translator.cycle();

    phraseIdx++;
    if (phraseIdx >= phrase.length) {
      phraseIdx = 0;
      progIdx = (progIdx + 1) % progressions.length;
    }
  }

  return step;
}

// ─── Init ───
document.addEventListener('DOMContentLoaded', () => {
  const piano = new PianoRoll(document.getElementById('piano-canvas'));
  const tracker = new ConservationTracker();
  const predictor = new TMinusPredictor(document.getElementById('tminus-events'));
  const translator = new FluxTranslator();
  const router = new AgentRouter();

  const status = document.getElementById('status');
  let playing = false;
  let demoInterval = null;
  let tminusInterval = null;
  const demoStep = runDemo(piano, tracker, predictor, translator);

  document.getElementById('btn-play').addEventListener('click', () => {
    playing = !playing;
    document.getElementById('btn-play').textContent = playing ? '⏸' : '▶';
    status.textContent = playing ? 'LIVE' : 'PAUSED';
    status.style.color = playing ? '#00ff88' : '#ff6b35';

    if (playing) {
      demoStep(); // immediate first step
      demoInterval = setInterval(demoStep, 1500);
      tminusInterval = setInterval(() => predictor.tick(), 500);
    } else {
      clearInterval(demoInterval);
      clearInterval(tminusInterval);
    }
  });

  document.getElementById('btn-reset').addEventListener('click', () => {
    playing = false;
    clearInterval(demoInterval);
    clearInterval(tminusInterval);
    document.getElementById('btn-play').textContent = '▶';
    status.textContent = 'IDLE';
    status.style.color = '#00ff88';
    piano.clear();
    document.getElementById('cr-live').textContent = '—';
    document.querySelectorAll('.cr-card').forEach(c => c.style.borderColor = '#222');
    document.querySelectorAll('.flux-stage').forEach(s => s.classList.remove('active'));
    document.querySelector('#flux-output').classList.add('active');
  });
});
