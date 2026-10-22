import json
import math
import time

import numpy as np
import pytest

from fractol.formulas import FORMULAS, describe, resolve_params
from fractol.fractals import compute_fractal, compute_smooth
from fractol.mapping import pixel_to_complex

SIZE, MAX_ITER = 16, 40
VIEW = (-0.5 + 0j, 3.0)  # a janela por omissão de pixel_to_complex


def reference_grid(step, start, params=None):
    """Referência em Python puro: percorre os píxeis um a um."""
    out = np.zeros((SIZE, SIZE), dtype=int)
    for py in range(SIZE):
        for px in range(SIZE):
            z, c = start(pixel_to_complex(px, py, SIZE, SIZE))
            count = MAX_ITER
            for i in range(MAX_ITER):
                z = step(z, c)
                if abs(z) >= 2:
                    count = i + 1
                    break
            out[py, px] = count
    return out


def from_engine(fractal, params=None):
    return compute_fractal(fractal, SIZE, SIZE, MAX_ITER, *VIEW, params)


def at_zero(pixel):
    return 0j, pixel


def test_julia_matches_reference():
    c = complex(-0.4, 0.6)
    expected = reference_grid(lambda z, c: z * z + c, lambda p: (p, c))
    assert np.array_equal(from_engine("julia", {"jr": -0.4, "ji": 0.6}), expected)


def test_burning_ship_matches_reference():
    def step(z, c):
        return complex(abs(z.real), abs(z.imag)) ** 2 + c

    assert np.array_equal(from_engine("burning_ship"), reference_grid(step, at_zero))


def test_tricorn_matches_reference():
    expected = reference_grid(lambda z, c: z.conjugate() ** 2 + c, at_zero)
    assert np.array_equal(from_engine("tricorn"), expected)


def test_multibrot_matches_reference_for_integer_power():
    expected = reference_grid(lambda z, c: z**3 + c, at_zero)
    got = from_engine("multibrot", {"power": 3.0})
    # z**3 em NumPy e em Python podem diferir na última casa decimal:
    # toleramos um ou outro píxel na fronteira, nunca mais do que isso.
    assert np.mean(got != expected) < 0.02


def test_multibrot_with_power_two_is_mandelbrot():
    assert np.array_equal(
        from_engine("multibrot", {"power": 2.0}), from_engine("mandelbrot")
    )


def test_smooth_uses_the_degree_of_the_formula():
    # c = 3, p = 3: z = 3, 30, 27003 -> escapa na 3.ª iteração (raio 256)
    result = compute_smooth("multibrot", 3, 3, 50, 3 + 0j, 1e-6, {"power": 3.0})
    expected = 3 - math.log(math.log(27003) / math.log(256)) / math.log(3)
    assert np.allclose(result, expected, atol=1e-3)


def test_resolve_params_fills_defaults_and_ignores_unknown_keys():
    values = resolve_params(FORMULAS["julia"], {"jr": 0.5, "nope": 1})
    assert values == {"jr": 0.5, "ji": 0.156, "power": 2.0}


def test_registry_is_consistent():
    for key, formula in FORMULAS.items():
        assert formula.key == key
        keys = [p.key for p in formula.params]
        assert len(keys) == len(set(keys))
        for p in formula.params:
            assert p.min <= p.default <= p.max
            assert p.step > 0
        for preset in formula.presets:
            assert preset.scale > 0
            for name, value in preset.params.items():
                param = next(p for p in formula.params if p.key == name)
                assert param.min <= value <= param.max


def test_describe_is_json_serialisable():
    data = json.loads(json.dumps(describe()))
    assert set(data) == set(FORMULAS)


ALL_PRESETS = [(key, preset) for key, f in FORMULAS.items() for preset in f.presets]


@pytest.mark.parametrize(
    "key,preset", ALL_PRESETS, ids=lambda v: getattr(v, "label", v)
)
def test_presets_show_something(key, preset):
    values = compute_smooth(
        key, 48, 32, 150, preset.center, preset.scale, preset.params
    )
    assert np.isfinite(values).all()
    assert len(np.unique(values)) > 1


def test_engine_stays_fast():
    start = time.perf_counter()
    compute_smooth("mandelbrot", 400, 300, 100)
    elapsed = time.perf_counter() - start
    assert elapsed < 3.0  # margem larga: só apanha regressões graves
