"""Motor vectorizado: Mandelbrot, Julia e Burning Ship."""

import numpy as np

FRACTALS = ("mandelbrot", "julia", "burning_ship")

DEFAULT_VIEWS = {
    "mandelbrot": (-0.5 + 0j, 3.0),
    "julia": (0j, 3.0),
    "burning_ship": (-0.5 - 0.5j, 4.0),
}


SMOOTH_BAILOUT = 256.0


def _iterate(
    fractal: str,
    width: int,
    height: int,
    max_iter: int,
    center: complex,
    scale: float,
    julia_c: complex,
    bailout: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Núcleo do cálculo. Devolve (iterations, modulus):
    - iterations: nº de iterações até |z| >= bailout (max_iter se nunca escapa);
    - modulus: |z| no momento em que escapou (0 onde nunca escapou).
    """
    if fractal not in FRACTALS:
        raise ValueError(f"fractal desconhecido: {fractal!r}")

    half_w = scale / 2
    half_h = half_w * height / width
    re = np.linspace(center.real - half_w, center.real + half_w, width)
    im = np.linspace(center.imag + half_h, center.imag - half_h, height)
    re_grid, im_grid = np.meshgrid(re, im)
    grid = re_grid + 1j * im_grid

    if fractal == "julia":
        z = grid.copy()
        c = np.full_like(grid, julia_c)
    else:
        z = np.zeros_like(grid)
        c = grid

    iterations = np.zeros(grid.shape, dtype=int)
    modulus = np.zeros(grid.shape, dtype=float)
    active = np.ones(grid.shape, dtype=bool)

    for i in range(max_iter):
        zi = z[active]
        if fractal == "burning_ship":
            zi = np.abs(zi.real) + 1j * np.abs(zi.imag)
        z[active] = zi * zi + c[active]

        magnitude = np.abs(z[active])
        gone = magnitude >= bailout
        escaped = np.zeros_like(active)
        escaped[active] = gone
        iterations[escaped] = i + 1
        modulus[escaped] = magnitude[gone]
        active &= ~escaped

    iterations[active] = max_iter
    return iterations, modulus


def compute_fractal(
    fractal: str,
    width: int,
    height: int,
    max_iter: int = 100,
    center: complex = -0.5 + 0j,
    scale: float = 3.0,
    julia_c: complex = -0.8 + 0.156j,
) -> np.ndarray:
    """
    Devolve um array (height x width) com o nº de iterações até escapar
    (ou max_iter, se nunca escapa).

    center: ponto do plano complexo no centro da imagem.
    scale: largura da janela no plano complexo (menor = mais zoom).
    julia_c: constante c, usada só pelo Julia.
    """
    iterations, _ = _iterate(
        fractal, width, height, max_iter, center, scale, julia_c, bailout=2.0
    )
    return iterations


def compute_smooth(
    fractal: str,
    width: int,
    height: int,
    max_iter: int = 100,
    center: complex = -0.5 + 0j,
    scale: float = 3.0,
    julia_c: complex = -0.8 + 0.156j,
) -> np.ndarray:
    """
    Iteração contínua (sem "degraus" entre bandas), em float32.

    Cada pixel que escapa recebe um valor real nu, entre n-1 e n (n = nº de
    iterações). Onde nunca escapa, devolve -1. Usa um raio de fuga grande
    (256) para o valor variar suavemente; a fórmula assume grau 2 (z² + c).
    """
    iterations, modulus = _iterate(
        fractal, width, height, max_iter, center, scale, julia_c, SMOOTH_BAILOUT
    )
    out = np.full(iterations.shape, -1.0, dtype=np.float32)
    escaped = modulus > 0
    ratio = np.log(modulus[escaped]) / np.log(SMOOTH_BAILOUT)
    out[escaped] = iterations[escaped] - np.log2(ratio)
    return out
