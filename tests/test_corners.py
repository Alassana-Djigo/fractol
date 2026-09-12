from fractol.mapping import pixel_to_complex


def test_top_left_corner():
    result = pixel_to_complex(0, 0, 600, 600)

    assert result == complex(-2.0, 1.5)


def test_top_right_corner():
    result = pixel_to_complex(599, 0, 600, 600)

    assert result == complex(1.0, 1.5)


def test_bottom_left_corner():
    result = pixel_to_complex(0, 599, 600, 600)

    assert result == complex(-2.0, -1.5)


def test_bottom_right_corner():
    result = pixel_to_complex(599, 599, 600, 600)

    assert result == complex(1.0, -1.5)
