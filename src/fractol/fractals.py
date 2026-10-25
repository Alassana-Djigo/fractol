"""Motor vectorizado: calcula qualquer fórmula registada em `formulas`."""

import numpy as np

from fractol.formulas import FORMULAS, Params, resolve_params

FRACTALS = tuple(FORMULAS)

DEFAULT_VIEWS = {key: (f.center, f.scale) for key, f in FORMULAS.items()}

SMOOTH_BAILOUT = 256.0


def _iterate(
    fractal: str,
    width: int,
    height: int,
    max_iter: int,
    center: complex,
    scale: float,
    params: Params | None,
    bailout: float,
) -> tuple[np.ndarray, np.ndarray, Params]:
    """
    Núcleo do cálculo. Devolve (iterations, modulus, params):
    - iterations: nº de iterações até |z| >= bailout (max_iter se nunca escapa);
    - modulus: |z| no momento em que escapou (0 onde nunca escapou);
    - params: valores finais dos parâmetros da fórmula.
    """
    if fractal not in FORMULAS:
        raise ValueError(f"fractal desconhecido: {fractal!r}")
    formula = FORMULAS[fractal]
    values = resolve_params(formula, params)

    half_w = scale / 2
    half_h = half_w * height / width
    re = np.linspace(center.real - half_w, center.real + half_w, width)
    im = np.linspace(center.imag + half_h, center.imag - half_h, height)
    re_grid, im_grid = np.meshgrid(re, im)
    grid = re_grid + 1j * im_grid

    z, c = formula.init(grid, values)

    # Só os píxeis que ainda não escaparam continuam na conta: a cada passo
    # os que escapam saem dos arrays, que vão encolhendo (em vez de se
    # percorrer sempre a imagem inteira). `idx` guarda a posição de cada um.
    iterations = np.full(grid.size, max_iter, dtype=int)
    modulus = np.zeros(grid.size, dtype=float)
    idx = np.arange(grid.size)
    z, c = z.ravel(), c.ravel()

    for i in range(max_iter):
        z = formula.step(z, c, values)
        magnitude = np.abs(z)
        gone = magnitude >= bailout
        if gone.any():
            iterations[idx[gone]] = i + 1
            modulus[idx[gone]] = magnitude[gone]
            keep = ~gone
            idx, z, c = idx[keep], z[keep], c[keep]
            if idx.size == 0:
                break

    iterations = iterations.reshape(grid.shape)
    modulus = modulus.reshape(grid.shape)
    return iterations, modulus, values


def compute_fractal(
    fractal: str,
    width: int,
    height: int,
    max_iter: int = 100,
    center: complex = -0.5 + 0j,
    scale: float = 3.0,
    params: Params | None = None,
) -> np.ndarray:
    """
    Devolve um array (height x width) com o nº de iterações até escapar
    (ou max_iter, se nunca escapa).

    center: ponto do plano complexo no centro da imagem.
    scale: largura da janela no plano complexo (menor = mais zoom).
    params: parâmetros da fórmula (os que faltarem usam o valor predefinido).
    """
    iterations, _, _ = _iterate(
        fractal, width, height, max_iter, center, scale, params, bailout=2.0
    )
    return iterations


def compute_smooth(
    fractal: str,
    width: int,
    height: int,
    max_iter: int = 100,
    center: complex = -0.5 + 0j,
    scale: float = 3.0,
    params: Params | None = None,
) -> np.ndarray:
    """
    Iteração contínua (sem "degraus" entre bandas), em float32.

    Cada pixel que escapa recebe um valor real nu, entre n-1 e n (n = nº de
    iterações). Onde nunca escapa, devolve -1. Usa um raio de fuga grande
    (256) para o valor variar suavemente; o grau da iteração é o parâmetro
    `power` da fórmula (2 se não tiver).
    """
    iterations, modulus, values = _iterate(
        fractal, width, height, max_iter, center, scale, params, SMOOTH_BAILOUT
    )
    degree = values.get("power", 2.0)
    out = np.full(iterations.shape, -1.0, dtype=np.float32)
    escaped = modulus > 0
    ratio = np.log(modulus[escaped]) / np.log(SMOOTH_BAILOUT)
    out[escaped] = iterations[escaped] - np.log(ratio) / np.log(degree)
    return out
