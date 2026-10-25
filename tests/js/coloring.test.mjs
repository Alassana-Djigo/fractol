import assert from "node:assert/strict";
import test from "node:test";

import {
  INTERIOR,
  PALETTES,
  buildLut,
  colorize,
} from "../../explorer/static/explorer/coloring.js";

const lut = buildLut(PALETTES.psicadelico.colors);
const options = { mode: "ciclico", period: 32, offset: 0, nuScale: 64 };

function colour(raw, overrides = {}) {
  const out = new Uint8ClampedArray(4);
  colorize(new Uint16Array([raw]), out, lut, { ...options, ...overrides });
  return [...out];
}

test("o valor reservado fica preto e opaco", () => {
  assert.deepEqual(colour(INTERIOR), [0, 0, 0, 255]);
});

test("nuScale converte o valor guardado em iterações", () => {
  // 32 iterações = um ciclo completo = a mesma cor que 0 iterações
  assert.deepEqual(colour(32 * 64), colour(0));
});

test("meio ciclo dá uma cor diferente do início", () => {
  assert.notDeepEqual(colour(16 * 64), colour(0));
});

test("todos os valores possíveis dão cores válidas e opacas", () => {
  for (const raw of [0, 1, 63, 64, 1000, 32000, INTERIOR - 1]) {
    const [r, g, b, a] = colour(raw);
    assert.ok([r, g, b].every((v) => v >= 0 && v <= 255), `raw=${raw}`);
    assert.equal(a, 255);
  }
});
