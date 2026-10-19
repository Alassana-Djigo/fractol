import io
import math

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest

from fractol.fractals import DEFAULT_VIEWS, FRACTALS, compute_fractal
from fractol.render_np import grid_to_image

MAX_SIZE = 1200
MAX_ITER = 500


def render_fractal(request: HttpRequest) -> HttpResponse:
    """GET /render/?fractal=julia&cx=0&cy=0&scale=3&w=800&h=600&iter=100"""
    fractal = request.GET.get("fractal", "mandelbrot")
    if fractal not in FRACTALS:
        return HttpResponseBadRequest("fractal inválido")

    default_center, default_scale = DEFAULT_VIEWS[fractal]
    try:
        center = complex(
            float(request.GET.get("cx", default_center.real)),
            float(request.GET.get("cy", default_center.imag)),
        )
        scale = float(request.GET.get("scale", default_scale))
        width = int(request.GET.get("w", 800))
        height = int(request.GET.get("h", 600))
        max_iter = int(request.GET.get("iter", 100))
    except ValueError:
        return HttpResponseBadRequest("parâmetros inválidos")

    values = (center.real, center.imag, scale)
    if not all(math.isfinite(v) for v in values) or scale <= 0:
        return HttpResponseBadRequest("parâmetros fora dos limites")
    if not (0 < width <= MAX_SIZE and 0 < height <= MAX_SIZE):
        return HttpResponseBadRequest("tamanho fora dos limites")
    if not 0 < max_iter <= MAX_ITER:
        return HttpResponseBadRequest("iterações fora dos limites")

    iterations = compute_fractal(fractal, width, height, max_iter, center, scale)
    buffer = io.BytesIO()
    grid_to_image(iterations, max_iter).save(buffer, format="PNG")
    return HttpResponse(buffer.getvalue(), content_type="image/png")
