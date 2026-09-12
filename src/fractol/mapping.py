def pixel_to_complex(
    px: int,
    py: int,
    width: int,
    height: int,
    re_min: float = -2.0,
    re_max: float = 1.0,
    im_min: float = -1.5,
    im_max: float = 1.5,
) -> complex:
    """Converte o pixel (px, py) de uma image width x height
    no numero complexo correspondente dentro da janela
    [re_min, re_max] x [im_min, im_max]"""
    re = re_min + px / (width - 1) * (re_max - re_min)
    im = im_max - py / (height - 1) * (im_max - im_min)

    return complex(re, im)
