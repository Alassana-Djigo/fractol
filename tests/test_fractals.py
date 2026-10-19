import numpy as np
import pytest

from fractol.fractals import FRACTALS, compute_fractal
from fractol.render_np import compute_iterations_grid


def test_mandelbrot_matches_previous_renderer():
    new = compute_fractal("mandelbrot", 20, 20, 50)
    old = compute_iterations_grid(20, 20, 50)
    assert np.array_equal(new, old)


@pytest.mark.parametrize("fractal", FRACTALS)
def test_origin_never_escapes(fractal):
    result = compute_fractal(fractal, 5, 5, 50, center=0j, scale=0.01, julia_c=0j)
    assert (result == 50).all()


def test_unknown_fractal_raises():
    with pytest.raises(ValueError):
        compute_fractal("nope", 5, 5)
