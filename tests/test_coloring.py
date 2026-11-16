import numpy as np
import pytest

from fractol.coloring import LUT_SIZE, MODES, PALETTES, build_lut, colorize

SAMPLES = [0, 100, 300, 512, 777, 1023]

# Valores calculados pelo coloring.js da página, para garantir que as duas
# implementações (browser e NumPy) dão exactamente as mesmas cores.
GOLDEN = {
    ("psicadelico", 1.0, 1.0): [
        [255, 0, 170],
        [199, 0, 217],
        [51, 36, 255],
        [0, 230, 255],
        [86, 17, 255],
        [255, 0, 170],
    ],
    ("nebulosa", 1.2, 1.3): [
        [0, 0, 48],
        [88, 0, 152],
        [255, 58, 177],
        [255, 219, 94],
        [53, 0, 163],
        [0, 0, 47],
    ],
}


@pytest.mark.parametrize("key", GOLDEN)
def test_lut_matches_the_javascript_implementation(key):
    name, brightness, contrast = key
    lut = build_lut(PALETTES[name], brightness, contrast)
    assert lut[SAMPLES].tolist() == GOLDEN[key]


@pytest.mark.parametrize("name", PALETTES)
def test_every_palette_wraps_around_smoothly(name):
    lut = build_lut(PALETTES[name]).astype(int)
    assert lut.shape == (LUT_SIZE, 3)
    assert np.abs(lut[-1] - lut[0]).max() <= 3


def test_interior_is_black_and_exterior_uses_the_palette():
    lut = build_lut(PALETTES["psicadelico"])
    nu = np.array([[-1.0, 0.0, 10.0]], dtype=np.float32)
    rgb = colorize(nu, lut, "ciclico", 32)
    assert rgb.shape == (1, 3, 3)
    assert rgb.dtype == np.uint8
    assert rgb[0, 0].tolist() == [0, 0, 0]
    assert rgb[0, 1].tolist() == lut[0].tolist()
    assert rgb[0, 2].tolist() != [0, 0, 0]


def test_one_full_period_gives_the_same_colour():
    lut = build_lut(PALETTES["aurora"])
    rgb = colorize(np.array([[0.0, 32.0, 64.0]]), lut, "ciclico", 32)
    assert rgb[0, 0].tolist() == rgb[0, 1].tolist() == rgb[0, 2].tolist()


@pytest.mark.parametrize("mode", MODES)
def test_every_mode_colours_a_gradient(mode):
    lut = build_lut(PALETTES["nebulosa"])
    nu = np.linspace(-1, 200, 500, dtype=np.float32).reshape(1, -1)
    rgb = colorize(nu, lut, mode, 24)
    assert rgb.shape == (1, 500, 3)
    assert len({tuple(c) for c in rgb[0]}) > 20
