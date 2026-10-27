import io
import math
import re

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render

from fractol.formulas import FORMULAS, describe
from fractol.fractals import Cancelled, compute_fractal, compute_smooth
from fractol.render_np import grid_to_image

from .cache import DATA_CACHE
from .encoding import NU_SCALE, quantize
from .latest import LATEST

MAX_SIZE = 1200
MAX_ITER = 500
CLIENT_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")
REQUEST_NUMBER = re.compile(r"[0-9]{1,12}")


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "explorer/index.html", {"formulas": describe()})


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


def cache_key(params: dict) -> tuple:
    center = params["center"]
    return (
        params["fractal"],
        params["width"],
        params["height"],
        params["max_iter"],
        center.real,
        center.imag,
        params["scale"],
        tuple(sorted(params["params"].items())),
    )


def client_request(request: HttpRequest) -> tuple[str, int] | None:
    """Identificação opcional do pedido (client + rid), para o cancelamento."""
    client = request.GET.get("client")
    if client is None:
        return None
    rid = request.GET.get("rid", "")
    if not CLIENT_ID.fullmatch(client) or not REQUEST_NUMBER.fullmatch(rid):
        raise ValueError("identificação do pedido inválida")
    return client, int(rid)


def fractal_data(request: HttpRequest) -> HttpResponse:
    """GET /data/ — iteração contínua em uint16 (little-endian), linha a linha.

    Cada valor é a iteração contínua vezes X-Nu-Scale; 65535 marca os píxeis
    que nunca escapam. A cor é aplicada no cliente, por isso mudar de paleta
    não recalcula nada. Os resultados ficam em cache (cabeçalho X-Cache).

    Se o pedido trouxer `client` e `rid` e chegar outro mais recente do mesmo
    cliente, o cálculo em curso é largado e a resposta é 204 (sem conteúdo).
    """
    try:
        params = parse_params(request)
        who = client_request(request)
    except ValueError as exc:
        return HttpResponseBadRequest(str(exc))

    if who is not None:
        LATEST.note(*who)

    key = cache_key(params)
    body = DATA_CACHE.get(key)
    hit = body is not None
    if not hit:
        stale = None if who is None else (lambda: LATEST.is_stale(*who))
        if stale is not None and stale():
            return HttpResponse(status=204)
        try:
            values = compute_smooth(**params, should_stop=stale)
        except Cancelled:
            return HttpResponse(status=204)
        body = quantize(values).tobytes()
        DATA_CACHE.put(key, body)

    response = HttpResponse(body, content_type="application/octet-stream")
    response["X-Nu-Scale"] = str(NU_SCALE)
    response["X-Cache"] = "hit" if hit else "miss"
    return response
