"""Motor vectorizado: Mandelbrot, Julia e Burning Ship."""

import numpy as np

FRACTALS = ("mandelbrot", "julia", "burning_ship")

DEFAULT_VIEWS = {
    "mandelbrot": (-0.5 + 0j, 3.0),
    "julia": (0j, 3.0),
    "burning_ship": (-0.5 - 0.5j, 4.0),
}


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
    active = np.ones(grid.shape, dtype=bool)

    for i in range(max_iter):
        zi = z[active]
        if fractal == "burning_ship":
            zi = np.abs(zi.real) + 1j * np.abs(zi.imag)
        z[active] = zi * zi + c[active]

        escaped = np.zeros_like(active)
        escaped[active] = np.abs(z[active]) >= 2
        iterations[escaped] = i + 1
        active &= ~escaped

    iterations[active] = max_iter
    return iterations
