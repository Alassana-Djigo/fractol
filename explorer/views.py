import io
import math

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from fractol.fractals import DEFAULT_VIEWS, FRACTALS, compute_fractal
from fractol.render_np import grid_to_image

MAX_SIZE = 1200
MAX_ITER = 500


def index(request: HttpRequest) -> HttpResponse:
    views = {
        name: {"cx": center.real, "cy": center.imag, "scale": scale}
        for name, (center, scale) in DEFAULT_VIEWS.items()
    }
    return render(request, "explorer/index.html", {"views": views})


def render_fractal(request: HttpRequest) -> HttpResponse:
    """GET /render/ — query: fractal, cx, cy, scale, w, h, iter, jr, ji."""
    fractal = request.GET.get("fractal", "mandelbrot")
    if fractal not in FRACTALS:
        return HttpResponseBadRequest("fractal inválido")

    default_center, default_scale = DEFAULT_VIEWS[fractal]
    try:
        center = complex(
            float(request.GET.get("cx", default_center.real)),
            float(request.GET.get("cy", default_center.imag)),
        )
        julia_c = complex(
            float(request.GET.get("jr", -0.8)),
            float(request.GET.get("ji", 0.156)),
        )
        scale = float(request.GET.get("scale", default_scale))
        width = int(request.GET.get("w", 800))
        height = int(request.GET.get("h", 600))
        max_iter = int(request.GET.get("iter", 100))
    except ValueError:
        return HttpResponseBadRequest("parâmetros inválidos")

    values = (center.real, center.imag, julia_c.real, julia_c.imag, scale)
    if not all(math.isfinite(v) for v in values) or scale <= 0:
        return HttpResponseBadRequest("parâmetros fora dos limites")
    if not (0 < width <= MAX_SIZE and 0 < height <= MAX_SIZE):
        return HttpResponseBadRequest("tamanho fora dos limites")
    if not 0 < max_iter <= MAX_ITER:
        return HttpResponseBadRequest("iterações fora dos limites")

    iterations = compute_fractal(
        fractal, width, height, max_iter, center, scale, julia_c
    )
    buffer = io.BytesIO()
    grid_to_image(iterations, max_iter).save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")
