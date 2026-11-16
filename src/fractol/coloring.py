"""Cor dos fractais: as mesmas paletas e modos da página, em NumPy.

Mantém-se em sincronia com explorer/static/explorer/coloring.js (a página usa
esse ficheiro no browser; este serve para gerar imagens e GIFs no terminal).
"""

import numpy as np

LUT_SIZE = 1024

# Paletas cíclicas, com paragens equidistantes (a última volta à primeira).
PALETTES = {
    "psicadelico": [
        (255, 0, 170),
        (140, 0, 255),
        (30, 60, 255),
        (0, 230, 255),
        (30, 60, 255),
        (140, 0, 255),
    ],
    "acido": [
        (190, 255, 0),
        (255, 240, 0),
        (255, 120, 0),
        (255, 0, 60),
        (255, 120, 0),
        (255, 240, 0),
    ],
    "aurora": [
        (0, 255, 150),
        (0, 200, 255),
        (40, 80, 255),
        (160, 40, 255),
        (40, 80, 255),
        (0, 200, 255),
    ],
    "nebulosa": [
        (25, 0, 60),
        (140, 0, 170),
        (255, 90, 130),
        (255, 170, 90),
        (110, 20, 150),
        (40, 10, 110),
    ],
    "cosmica": [
        (0, 0, 25),
        (20, 40, 200),
        (210, 235, 255),
        (0, 200, 255),
        (10, 60, 160),
        (0, 0, 40),
    ],
    "optica": [(0, 0, 0), (255, 255, 255)],
}


def _cyclic(nu, period):
    return nu / period


def _mirrored(nu, period):
    f = (nu / period) % 1
    return np.where(f < 0.5, 2 * f, 2 - 2 * f)


def _logarithmic(nu, period):
    return 8 * np.log2(1 + nu) / np.log2(1 + period)


MODES = {"ciclico": _cyclic, "espelhado": _mirrored, "logaritmico": _logarithmic}


def build_lut(colors, brightness: float = 1.0, contrast: float = 1.0) -> np.ndarray:
    """Tabela (LUT_SIZE x 3) por spline de Catmull-Rom cíclica."""
    palette = np.array(colors, dtype=float)
    n = len(palette)
    x = np.arange(LUT_SIZE) / LUT_SIZE * n
    j = np.floor(x).astype(int)
    t = (x - j)[:, None]
    p0 = palette[(j - 1) % n]
    p1 = palette[j % n]
    p2 = palette[(j + 1) % n]
    p3 = palette[(j + 2) % n]
    v = 0.5 * (
        2 * p1
        + (-p0 + p2) * t
        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t**2
        + (-p0 + 3 * p1 - 3 * p2 + p3) * t**3
    )
    out = (((v / 255 - 0.5) * contrast + 0.5) * brightness) * 255
    return np.clip(np.rint(out), 0, 255).astype(np.uint8)


def colorize(
    nu: np.ndarray,
    lut: np.ndarray,
    mode: str = "ciclico",
    period: float = 32.0,
    offset: float = 0.0,
) -> np.ndarray:
    """Iteração contínua (-1 = interior) -> imagem RGB (altura x largura x 3)."""
    phase = MODES[mode](np.maximum(nu, 0), period) + offset
    index = ((phase - np.floor(phase)) * LUT_SIZE).astype(int) & (LUT_SIZE - 1)
    rgb = lut[index]
    rgb[nu < 0] = 0
    return rgb
