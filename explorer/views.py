import io
import math

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from fractol.formulas import FORMULAS, describe
from fractol.fractals import compute_fractal, compute_smooth
from fractol.render_np import grid_to_image

MAX_SIZE = 1200
MAX_ITER = 500


def index(request: HttpRequest) -> HttpResponse:
    formulas = describe()
    views = {
        key: {"cx": f["cx"], "cy": f["cy"], "scale": f["scale"]}
        for key, f in formulas.items()
    }
    return render(request, "explorer/index.html", {"views": views})


def parse_params(request: HttpRequest) -> dict:
    """Lê e valida os parâmetros comuns; levanta ValueError se forem maus."""
    fractal = request.GET.get("fractal", "mandelbrot")
    if fractal not in FORMULAS:
        raise ValueError("fractal inválido")
    formula = FORMULAS[fractal]

    get = request.GET.get
    try:
        center = complex(
            float(get("cx", formula.center.real)),
            float(get("cy", formula.center.imag)),
        )
        scale = float(get("scale", formula.scale))
        width = int(get("w", 800))
        height = int(get("h", 600))
        max_iter = int(get("iter", 100))
        params = {p.key: float(get(p.key, p.default)) for p in formula.params}
    except ValueError:
        raise ValueError("parâmetros inválidos") from None

    values = (center.real, center.imag, scale, *params.values())
    if not all(math.isfinite(v) for v in values) or scale <= 0:
        raise ValueError("parâmetros fora dos limites")
    for p in formula.params:
        if not p.min <= params[p.key] <= p.max:
            raise ValueError(f"{p.key} fora dos limites")
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
        "params": params,
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
