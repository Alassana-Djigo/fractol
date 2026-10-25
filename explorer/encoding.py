"""Formato de transporte dos valores de iteração (servidor -> página)."""

import numpy as np

NU_SCALE = 64  # resolução de 1/64 de iteração
INTERIOR = 0xFFFF  # valor reservado: o píxel nunca escapa


def quantize(nu: np.ndarray) -> np.ndarray:
    """float32 (-1 = interior) -> uint16 little-endian (INTERIOR = interior)."""
    scaled = np.clip(np.rint(nu * NU_SCALE), 0, INTERIOR - 1)
    return np.where(nu < 0, INTERIOR, scaled).astype("<u2")
