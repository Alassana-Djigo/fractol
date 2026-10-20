import numpy as np
import pytest

from fractol.fractals import FRACTALS, compute_fractal, compute_smooth
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


def test_smooth_matches_hand_computed_value():
    # c = 3: z = 3, 12, 147, 21612 -> escapa na 4.ª iteração
    result = compute_smooth("mandelbrot", 3, 3, 50, center=3 + 0j, scale=1e-6)
    assert result.dtype == np.float32
    assert np.allclose(result, 3.15205, atol=1e-3)


def test_smooth_marks_interior_and_stays_close_to_integer_count():
    smooth = compute_smooth("mandelbrot", 60, 40, 80)
    ints = compute_fractal("mandelbrot", 60, 40, 80)
    assert (smooth[ints == 80] == -1).all()
    escaped = smooth >= 0
    assert (smooth[escaped] > ints[escaped] - 1).all()
