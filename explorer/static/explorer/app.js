"use strict";

const VIEWS = JSON.parse(document.getElementById("views-data").textContent);
const PREVIEW = 0.25;
const MAX_SIZE = 1200;
const MIN_SCALE = 1e-11; // limite prático da precisão float64

const INFO = {
  mandelbrot:
    "Cada ponto c do plano é testado repetindo z → z² + c a partir de z = 0. " +
    "Se z nunca se afasta, o ponto pertence ao conjunto (preto). " +
    "Fora dele, o brilho mostra quão depressa escapa.",
  julia:
    "Mesma fórmula, mas c é fixo e o ponto testado é o ponto de partida z. " +
    "Mexe em c e vê a forma transformar-se.",
  burning_ship:
    "Como o Mandelbrot, mas com o valor absoluto das partes real e " +
    "imaginária antes de elevar ao quadrado. Daí os 'navios em chamas'.",
};

const PRESETS = {
  mini: { fractal: "mandelbrot", cx: -1.7548776662466927, cy: 0, scale: 0.08 },
  seahorse: { fractal: "mandelbrot", cx: -0.75, cy: 0.1, scale: 0.1 },
  spiral: {
    fractal: "mandelbrot",
    cx: -0.7436438870371587,
    cy: 0.13182590420531197,
    scale: 0.0005,
  },
};

const $ = (id) => document.getElementById(id);
const canvas = $("view");
const ctx = canvas.getContext("2d");
const state = {
  fractal: "mandelbrot", cx: 0, cy: 0, scale: 3,
  jr: -0.8, ji: 0.156, iter: 100, auto: true,
};

let seq = 0;
let controller = null;
let throttle = 0;
let settle = 0;
let drag = null;

function currentIter() {
  if (!state.auto) return state.iter;
  const depth = Math.log2(VIEWS[state.fractal].scale / state.scale);
  return Math.round(Math.min(500, Math.max(60, 80 + 35 * Math.max(0, depth))));
}

async function draw(quality) {
  const id = ++seq;
  controller?.abort();
  controller = new AbortController();
  const params = new URLSearchParams({
    fractal: state.fractal,
    cx: state.cx,
    cy: state.cy,
    scale: state.scale,
    w: Math.max(1, Math.round(canvas.width * quality)),
    h: Math.max(1, Math.round(canvas.height * quality)),
    iter: currentIter(),
    jr: state.jr,
    ji: state.ji,
  });
  try {
    const res = await fetch(`/render/?${params}`, { signal: controller.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const bitmap = await createImageBitmap(await res.blob());
    if (id !== seq) return;
    ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
    if (quality === 1) $("status").textContent = "pronto";
  } catch (err) {
    if (err.name !== "AbortError") $("status").textContent = "erro";
  }
}

function updateHud() {
  const zoom = VIEWS[state.fractal].scale / state.scale;
  $("zoom").textContent =
    zoom < 1000 ? `${zoom.toFixed(1)}×` : `${zoom.toExponential(2)}×`;
  const sign = state.cy < 0 ? "−" : "+";
  $("coords").textContent =
    `${state.cx.toPrecision(12)} ${sign} ${Math.abs(state.cy).toPrecision(12)}i`;
  const it = currentIter();
  $("iter-val").textContent = it;
  if (state.auto) $("iter").value = it;
}

function schedule() {
  updateHud();
  $("status").textContent = "a calcular…";
  if (!throttle) {
    throttle = setTimeout(() => {
      throttle = 0;
      draw(PREVIEW);
    }, 80);
  }
  clearTimeout(settle);
  settle = setTimeout(() => draw(1), 300);
}

function syncUi() {
  $("fractal").value = state.fractal;
  $("julia-controls").hidden = state.fractal !== "julia";
  $("jr").value = state.jr;
  $("ji").value = state.ji;
  $("jr-val").textContent = state.jr.toFixed(3);
  $("ji-val").textContent = state.ji.toFixed(3);
  $("auto-iter").checked = state.auto;
  $("iter").value = state.iter;
  $("explain").textContent = INFO[state.fractal];
}

function resetView() {
  const v = VIEWS[state.fractal];
  Object.assign(state, { cx: v.cx, cy: v.cy, scale: v.scale });
}

function resetAll() {
  Object.assign(state, { jr: -0.8, ji: 0.156, iter: 100, auto: true });
  resetView();
  syncUi();
  schedule();
}

function zoomAt(fx, fy, factor) {
  const aspect = canvas.height / canvas.width;
  const maxScale = VIEWS[state.fractal].scale * 4;
  const next = Math.min(maxScale, Math.max(MIN_SCALE, state.scale * factor));
  const re = state.cx + (fx - 0.5) * state.scale;
  const im = state.cy - (fy - 0.5) * state.scale * aspect;
  state.cx = re - (fx - 0.5) * next;
  state.cy = im + (fy - 0.5) * next * aspect;
  state.scale = next;
  schedule();
}

function resize() {
  const rect = canvas.getBoundingClientRect();
  if (!rect.width || !rect.height) return;
  const k = Math.min(1, MAX_SIZE / Math.max(rect.width, rect.height));
  canvas.width = Math.round(rect.width * k);
  canvas.height = Math.round(rect.height * k);
  schedule();
}

canvas.addEventListener(
  "wheel",
  (e) => {
    e.preventDefault();
    const fx = e.offsetX / canvas.clientWidth;
    const fy = e.offsetY / canvas.clientHeight;
    zoomAt(fx, fy, Math.exp(e.deltaY * 0.0015));
  },
  { passive: false },
);

canvas.addEventListener("pointerdown", (e) => {
  drag = { x: e.clientX, y: e.clientY };
  canvas.setPointerCapture(e.pointerId);
  canvas.classList.add("dragging");
});

canvas.addEventListener("pointermove", (e) => {
  if (!drag) return;
  const unit = state.scale / canvas.clientWidth; // unidades do plano por pixel
  state.cx -= (e.clientX - drag.x) * unit;
  state.cy += (e.clientY - drag.y) * unit;
  drag = { x: e.clientX, y: e.clientY };
  schedule();
});

const endDrag = () => {
  drag = null;
  canvas.classList.remove("dragging");
};
canvas.addEventListener("pointerup", endDrag);
canvas.addEventListener("pointercancel", endDrag);

window.addEventListener("keydown", (e) => {
  if (e.target.matches("input, select")) return;
  const step = state.scale * 0.1;
  switch (e.key) {
    case "ArrowLeft": state.cx -= step; break;
    case "ArrowRight": state.cx += step; break;
    case "ArrowUp": state.cy += step; break;
    case "ArrowDown": state.cy -= step; break;
    case "+": case "=": zoomAt(0.5, 0.5, 0.8); return;
    case "-": zoomAt(0.5, 0.5, 1.25); return;
    case "r": case "R": resetAll(); return;
    default: return;
  }
  e.preventDefault();
  schedule();
});

$("fractal").addEventListener("change", (e) => {
  state.fractal = e.target.value;
  resetView();
  syncUi();
  schedule();
});

for (const id of ["jr", "ji"]) {
  $(id).addEventListener("input", (e) => {
    state[id] = parseFloat(e.target.value);
    $(`${id}-val`).textContent = state[id].toFixed(3);
    schedule();
  });
}

$("iter").addEventListener("input", (e) => {
  state.iter = Number(e.target.value);
  state.auto = false;
  $("auto-iter").checked = false;
  schedule();
});

$("auto-iter").addEventListener("change", (e) => {
  state.auto = e.target.checked;
  schedule();
});

$("reset").addEventListener("click", resetAll);

document.querySelectorAll("[data-preset]").forEach((button) => {
  button.addEventListener("click", () => {
    Object.assign(state, PRESETS[button.dataset.preset]);
    syncUi();
    schedule();
  });
});

document.querySelector("aside").addEventListener("change", (e) => e.target.blur());

new ResizeObserver(resize).observe(canvas);
resetAll();
