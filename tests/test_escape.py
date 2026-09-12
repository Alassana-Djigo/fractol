from fractol.escape import escape_iterations


def test_c_zero_stays_bounded():
    assert escape_iterations(0, 0, max_iter=100) == 100


def test_c_one_escapes_fast():
    assert escape_iterations(0, 1, max_iter=100) < 100


def test_c_minus_one_stays_bounded():
    assert escape_iterations(0, -1, max_iter=100) == 100
