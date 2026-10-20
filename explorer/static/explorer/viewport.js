// Matemática da vista, sem DOM: uma vista é { cx, cy, scale, aspect } —
// centro no plano complexo, largura da janela e altura/largura do ecrã.

// Ponto do plano que está na posição (fx, fy) do ecrã (fracções de 0 a 1).
export function pointAt(view, fx, fy) {
  return {
    re: view.cx + (fx - 0.5) * view.scale,
    im: view.cy - (fy - 0.5) * view.scale * view.aspect,
  };
}

// Nova vista depois de um zoom que mantém o MESMO ponto sob (fx, fy).
export function zoomedView(view, fx, fy, factor, { min, max }) {
  const scale = Math.min(max, Math.max(min, view.scale * factor));
  const { re, im } = pointAt(view, fx, fy);
  return {
    ...view,
    cx: re - (fx - 0.5) * scale,
    cy: im + (fy - 0.5) * scale * view.aspect,
    scale,
  };
}

// Onde desenhar (em píxeis) uma imagem calculada para a vista `from`,
// quando a vista actual é `to`. Vista igual => ocupa o ecrã todo.
export function placement(from, to, width) {
  const k = from.scale / to.scale;
  return {
    x: (((from.cx - from.scale / 2) - (to.cx - to.scale / 2)) / to.scale) * width,
    y:
      (((to.cy + (to.scale * to.aspect) / 2) -
        (from.cy + (from.scale * from.aspect) / 2)) /
        to.scale) *
      width,
    w: width * k,
    h: width * k * from.aspect,
  };
}
