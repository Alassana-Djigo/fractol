import io
import math

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from fractol.fractals import (
    DEFAULT_VIEWS,
    FRACTALS,
    compute_fractal,
    compute_smooth,
)
from fractol.render_np import grid_to_image

MAX_SIZE = 1200
MAX_ITER = 500


def index(request: HttpRequest) -> HttpResponse:
    views = {
        name: {"cx": center.real, "cy": center.imag, "scale": scale}
        for name, (center, scale) in DEFAULT_VIEWS.items()
    }
    return render(request, "explorer/index.html", {"views": views})


def parse_params(request: HttpRequest) -> dict:
    """Lê e valida os parâmetros comuns; levanta ValueError se forem maus."""
    fractal = request.GET.get("fractal", "mandelbrot")
    if fractal not in FRACTALS:
        raise ValueError("fractal inválido")

    default_center, default_scale = DEFAULT_VIEWS[fractal]
    get = request.GET.get
    try:
        center = complex(
            float(get("cx", default_center.real)),
            float(get("cy", default_center.imag)),
        )
        julia_c = complex(float(get("jr", -0.8)), float(get("ji", 0.156)))
        scale = float(get("scale", default_scale))
        width = int(get("w", 800))
        height = int(get("h", 600))
        max_iter = int(get("iter", 100))
    except ValueError:
        raise ValueError("parâmetros inválidos") from None

    values = (center.real, center.imag, julia_c.real, julia_c.imag, scale)
    if not all(math.isfinite(v) for v in values) or scale <= 0:
        raise ValueError("parâmetros fora dos limites")
    if not (0 < width <= MAX_SIZE and 0 < height <= MAX_SIZE):
        raise ValueError("tamanho fora dos limites")
    if not 0 < max_iter <= MAX_ITER:
        raise ValueError("iterações fora dos limites")

    return {
        "fractal": fractal,
        "width": width,
        "height": height,
        "max_iter": max_iter,
        "center": center,
        "scale": scale,
        "julia_c": julia_c,
    }


def render_fractal(request: HttpRequest) -> HttpResponse:
    """GET /render/ — PNG em tons de cinzento (exportação simples)."""
    try:
        params = parse_params(request)
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))

    iterations = compute_fractal(**params)
    buffer = io.BytesIO()
    grid_to_image(iterations, params["max_iter"]).save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")


def fractal_data(request: HttpRequest) -> HttpResponse:
    """GET /data/ — iteração contínua em float32 (little-endian), linha a linha.

    A cor é aplicada no cliente, por isso mudar de paleta não recalcula nada.
    """
    try:
        params = parse_params(request)
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))

    values = compute_smooth(**params)
    return HttpResponse(
        values.astype("<f4").tobytes(), content_type="application/octet-stream"
    )
