import assert from "node:assert/strict";
import test from "node:test";

import { placement, pointAt, zoomedView } from "../../explorer/static/explorer/viewport.js";

const LIMITS = { min: 1e-11, max: 12 };
const view = { cx: -0.75, cy: 0.1, scale: 0.4, aspect: 0.7 };
const near = (a, b) => assert.ok(Math.abs(a - b) < 1e-12, `${a} != ${b}`);

test("zoom mantém o ponto sob o cursor", () => {
  for (const [fx, fy, factor] of [[0.2, 0.8, 0.5], [0.9, 0.1, 2], [0.5, 0.5, 0.01]]) {
    const before = pointAt(view, fx, fy);
    const after = pointAt(zoomedView(view, fx, fy, factor, LIMITS), fx, fy);
    near(before.re, after.re);
    near(before.im, after.im);
  }
});

test("zoom respeita os limites", () => {
  assert.equal(zoomedView(view, 0.5, 0.5, 1e-30, LIMITS).scale, LIMITS.min);
  assert.equal(zoomedView(view, 0.5, 0.5, 1e30, LIMITS).scale, LIMITS.max);
});

test("a mesma vista ocupa o ecrã todo", () => {
  const p = placement(view, view, 1000);
  near(p.x, 0);
  near(p.y, 0);
  near(p.w, 1000);
  near(p.h, 1000 * view.aspect);
});

test("um ponto da imagem antiga cai onde a vista nova o põe", () => {
  const from = { cx: -0.5, cy: 0, scale: 3, aspect: 0.5067 }; // prévia arredondada
  const to = { cx: -0.6, cy: 0.05, scale: 1.1, aspect: 0.5 };
  const width = 800;
  const p = placement(from, to, width);
  for (const [u, v] of [[0.1, 0.2], [0.5, 0.5], [0.93, 0.71]]) {
    const world = pointAt(from, u, v); // ponto no plano, dentro da imagem antiga
    const x = p.x + u * p.w; // onde a imagem antiga o desenha
    const y = p.y + v * p.h;
    const seen = pointAt(to, x / width, y / (width * to.aspect));
    near(world.re, seen.re);
    near(world.im, seen.im);
  }
});
