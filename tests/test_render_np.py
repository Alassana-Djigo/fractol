from fractol.escape import escape_iterations
from fractol.mapping import pixel_to_complex
from fractol.render_np import compute_iterations_grid


def test_matches_pure_python_reference():
    width, height, max_iter = 20, 20, 50

    numpy_result = compute_iterations_grid(width, height, max_iter)

    for py in range(height):
        for px in range(width):
            c = pixel_to_complex(px, py, width, height)
            expected = escape_iterations(0, c, max_iter)
            assert numpy_result[py, px] == expected
