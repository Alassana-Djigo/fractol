// Sistema de cor, independente da matemática: recebe valores de iteração
// contínua (nu >= 0; negativo = ponto que nunca escapa) e devolve pixéis.

export const LUT_SIZE = 1024; // potência de 2 (permite usar & em vez de %)

// Paletas cíclicas, com paragens equidistantes (a última volta à primeira).
export const PALETTES = {
  psicadelico: {
    label: "Psicadélico (magenta · violeta · azul · ciano)",
    colors: [[255, 0, 170], [140, 0, 255], [30, 60, 255], [0, 230, 255],
             [30, 60, 255], [140, 0, 255]],
  },
  acido: {
    label: "Ácido (verde · amarelo · laranja · vermelho)",
    colors: [[190, 255, 0], [255, 240, 0], [255, 120, 0], [255, 0, 60],
             [255, 120, 0], [255, 240, 0]],
  },
  aurora: {
    label: "Aurora (verde · ciano · azul · violeta)",
    colors: [[0, 255, 150], [0, 200, 255], [40, 80, 255], [160, 40, 255],
             [40, 80, 255], [0, 200, 255]],
  },
  nebulosa: {
    label: "Nebulosa (roxo · magenta · rosa · laranja)",
    colors: [[25, 0, 60], [140, 0, 170], [255, 90, 130], [255, 170, 90],
             [110, 20, 150], [40, 10, 110]],
  },
  cosmica: {
    label: "Cósmica (azul-noite · eléctrico · branco · ciano)",
    colors: [[0, 0, 25], [20, 40, 200], [210, 235, 255], [0, 200, 255],
             [10, 60, 160], [0, 0, 40]],
  },
  optica: {
    label: "Óptica (preto e branco)",
    colors: [[0, 0, 0], [255, 255, 255]],
  },
};

// Como o valor nu vira uma posição na paleta (antes de tomar a parte fraccionária).
export const MODES = {
  ciclico: { label: "Cíclico", phase: (nu, period) => nu / period },
  espelhado: {
    label: "Espelhado (vai e volta)",
    phase: (nu, period) => {
      const f = (nu / period) % 1;
      return f < 0.5 ? 2 * f : 2 - 2 * f;
    },
  },
  logaritmico: {
    label: "Logarítmico (mais detalhe perto do conjunto)",
    phase: (nu, period) => (8 * Math.log2(1 + nu)) / Math.log2(1 + period),
  },
};

// Interpola as cores com uma spline de Catmull-Rom (cíclica): transições
// suaves, sem "esquinas" nas paragens. Brilho e contraste ficam já na tabela.
export function buildLut(colors, { brightness = 1, contrast = 1 } = {}) {
  const n = colors.length;
  const lut = new Uint8ClampedArray(LUT_SIZE * 3);
  for (let i = 0; i < LUT_SIZE; i++) {
    const x = (i / LUT_SIZE) * n;
    const j = Math.floor(x);
    const t = x - j;
    const p0 = colors[(j - 1 + n) % n];
    const p1 = colors[j % n];
    const p2 = colors[(j + 1) % n];
    const p3 = colors[(j + 2) % n];
    for (let k = 0; k < 3; k++) {
      const v =
        0.5 *
        (2 * p1[k] +
          (-p0[k] + p2[k]) * t +
          (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t +
          (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t * t * t);
      lut[i * 3 + k] = (((v / 255 - 0.5) * contrast + 0.5) * brightness) * 255;
    }
  }
  return lut;
}

// values: Float32Array; out: Uint8ClampedArray RGBA do mesmo tamanho em píxeis.
export function colorize(values, out, lut, { mode, period, offset }) {
  const phase = MODES[mode].phase;
  for (let i = 0, o = 0; i < values.length; i++, o += 4) {
    const nu = values[i];
    if (nu < 0) {
      out[o] = 0;
      out[o + 1] = 0;
      out[o + 2] = 0;
    } else {
      const u = phase(nu, period) + offset;
      const idx = (((u - Math.floor(u)) * LUT_SIZE) | 0) & (LUT_SIZE - 1);
      out[o] = lut[idx * 3];
      out[o + 1] = lut[idx * 3 + 1];
      out[o + 2] = lut[idx * 3 + 2];
    }
    out[o + 3] = 255;
  }
}
