"""Mede o tempo do motor em pedidos típicos e no pior caso."""

import time

from fractol.formulas import FORMULAS
from fractol.fractals import compute_smooth

SPIRAL = complex(-0.7436438870371587, 0.13182590420531197)

# (descrição, fórmula, largura, altura, iterações, centro, escala, parâmetros)
CASES = [
    ("Mandelbrot inicial", "mandelbrot", 1000, 700, 100, None, None, None),
    ("Espiral profunda", "mandelbrot", 1000, 700, 300, SPIRAL, 0.0005, None),
    ("Julia", "julia", 1000, 700, 100, None, None, None),
    ("Multibrot p=3", "multibrot", 1000, 700, 100, None, None, {"power": 3.0}),
    ("Multibrot p=3,7", "multibrot", 1000, 700, 100, None, None, {"power": 3.7}),
    ("Burning Ship", "burning_ship", 1000, 700, 100, None, None, None),
    ("Pior caso (alta, 500 it)", "mandelbrot", 1200, 840, 500, SPIRAL, 0.0005, None),
]


def main() -> None:
    for name, key, width, height, iters, center, scale, params in CASES:
        formula = FORMULAS[key]
        center = formula.center if center is None else center
        scale = formula.scale if scale is None else scale
        start = time.perf_counter()
        compute_smooth(key, width, height, iters, center, scale, params)
        elapsed = (time.perf_counter() - start) * 1000
        print(f"{name:28s} {width}x{height} {iters:3d} it  {elapsed:7.0f} ms")


if __name__ == "__main__":
    main()
