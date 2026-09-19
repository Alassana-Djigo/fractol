"""Renderização vectorizada do Mandelbrot, usando NumPy."""

import numpy as np
from PIL import Image


def compute_iterations_grid(
    width: int,
    height: int,
    max_iter: int = 100,
    re_min: float = -2.0,
    re_max: float = 1.0,
    im_min: float = -1.5,
    im_max: float = 1.5,
) -> np.ndarray:
    """
    Calcula, para todos os pixels de uma vez, quantas iterações
    levou até escapar (ou max_iter, se nunca escapou).

    É a mesma ideia de escape_iterations aplicada pixel a pixel,
    mas em bloco — devolve um array 2D (height x width) de inteiros.
    """
    re = np.linspace(re_min, re_max, width)
    im = np.linspace(im_max, im_min, height)
    re_grid, im_grid = np.meshgrid(re, im)
    c = re_grid + 1j * im_grid

    z = np.zeros_like(c)
    iterations = np.zeros(c.shape, dtype=int)
    active = np.ones(c.shape, dtype=bool)

    for i in range(max_iter):
        z[active] = z[active] * z[active] + c[active]
        escaped_now = active & (np.abs(z) >= 2)
        iterations[escaped_now] = i + 1
        active &= ~escaped_now

    iterations[active] = max_iter
    return iterations


def grid_to_image(iterations: np.ndarray, max_iter: int) -> Image.Image:
    """Converte a grelha de iterações numa imagem em escala de cinzentos."""
    in_set = iterations == max_iter
    gray = np.zeros(iterations.shape, dtype=np.uint8)
    gray[~in_set] = (255 * iterations[~in_set] / max_iter).astype(np.uint8)
    return Image.fromarray(gray, mode="L")


def render_mandelbrot_np(width: int, height: int, max_iter: int = 100) -> Image.Image:
    """Gera a imagem do Mandelbrot usando a versão vectorizada."""
    iterations = compute_iterations_grid(width, height, max_iter)
    return grid_to_image(iterations, max_iter)


if __name__ == "__main__":
    render_mandelbrot_np(600, 600).save("assets/mandelbrot_v2_numpy.png")
