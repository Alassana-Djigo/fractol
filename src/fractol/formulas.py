"""Registo de fórmulas.

Cada fórmula declara os seus parâmetros, a vista inicial e as predefinições.
O motor, o servidor e a página lêem tudo daqui: para acrescentar uma fórmula
basta definir um `Formula` e juntá-lo a `FORMULAS` (não se mexe na interface).

Convenção: se uma fórmula tiver um parâmetro `power`, esse é o grau da
iteração (usado na coloração contínua); caso contrário o grau é 2.
"""

from collections.abc import Callable
from dataclasses import asdict, dataclass, field

import numpy as np

Params = dict[str, float]


@dataclass(frozen=True)
class Param:
    key: str
    label: str
    default: float
    min: float
    max: float
    step: float


@dataclass(frozen=True)
class Preset:
    label: str
    center: complex
    scale: float
    params: Params = field(default_factory=dict)


@dataclass(frozen=True)
class Formula:
    key: str
    label: str
    description: str
    center: complex  # vista inicial
    scale: float
    init: Callable[[np.ndarray, Params], tuple[np.ndarray, np.ndarray]]
    step: Callable[[np.ndarray, np.ndarray, Params], np.ndarray]
    params: tuple[Param, ...] = ()
    presets: tuple[Preset, ...] = ()


def power(z: np.ndarray, p: float) -> np.ndarray:
    return z * z if p == 2 else z**p


def start_at_zero(grid: np.ndarray, params: Params):
    """z começa em 0 e o ponto do plano é a constante c (Mandelbrot e afins)."""
    return np.zeros_like(grid), grid


def start_at_point(grid: np.ndarray, params: Params):
    """z começa no ponto do plano e c é fixo, dado pelos parâmetros (Julia)."""
    c = complex(params["jr"], params["ji"])
    return grid.copy(), np.full_like(grid, c)


def abs_parts(z: np.ndarray) -> np.ndarray:
    return np.abs(z.real) + 1j * np.abs(z.imag)


POWER = Param("power", "Expoente", 2.0, 2.0, 8.0, 0.05)
JULIA_RE = Param("jr", "c (parte real)", -0.8, -2.0, 2.0, 0.001)
JULIA_IM = Param("ji", "c (parte imaginária)", 0.156, -2.0, 2.0, 0.001)


def with_default(param: Param, default: float) -> Param:
    return Param(param.key, param.label, default, param.min, param.max, param.step)


MANDELBROT = Formula(
    key="mandelbrot",
    label="Mandelbrot",
    description=(
        "Cada ponto c do plano é testado repetindo z → z² + c a partir de z = 0. "
        "Se z nunca se afasta, o ponto pertence ao conjunto (preto). "
        "Fora dele, a cor mostra quão depressa escapa."
    ),
    center=-0.5 + 0j,
    scale=3.0,
    init=start_at_zero,
    step=lambda z, c, p: z * z + c,
    presets=(
        Preset("Mini-Mandelbrot (auto-semelhança)", -1.7548776662466927 + 0j, 0.08),
        Preset("Vale dos cavalos-marinhos", -0.7453 + 0.1127j, 0.01),
        Preset(
            "Espiral profunda",
            complex(-0.7436438870371587, 0.13182590420531197),
            0.0005,
        ),
    ),
)

JULIA = Formula(
    key="julia",
    label="Julia",
    description=(
        "Mesma fórmula do Mandelbrot, mas c é fixo e o ponto testado é o ponto de "
        "partida z. Pequenas mudanças em c transformam a forma por completo."
    ),
    center=0j,
    scale=3.0,
    init=start_at_point,
    step=lambda z, c, p: power(z, p["power"]) + c,
    params=(JULIA_RE, JULIA_IM, POWER),
    presets=(
        Preset("Espirais", 0j, 3.0, {"jr": -0.8, "ji": 0.156}),
        Preset("Coelho de Douady", 0j, 3.0, {"jr": -0.123, "ji": 0.745}),
        Preset("Dendrite", 0j, 3.0, {"jr": 0.0, "ji": 1.0}),
        Preset("Disco de Siegel", 0j, 3.0, {"jr": -0.3905, "ji": -0.5868}),
        Preset("Julia cúbico", 0j, 3.0, {"jr": 0.4, "ji": 0.1, "power": 3.0}),
    ),
)

MULTIBROT = Formula(
    key="multibrot",
    label="Multibrot",
    description=(
        "Como o Mandelbrot, mas com z elevado a um expoente à tua escolha: "
        "z → z^p + c. Com p inteiro aparecem p−1 'bolbos' simétricos; "
        "com p fraccionário surgem cortes e formas estranhas."
    ),
    center=0j,
    scale=3.0,
    init=start_at_zero,
    step=lambda z, c, p: power(z, p["power"]) + c,
    params=(with_default(POWER, 3.0),),
    presets=(
        Preset("Cúbico (p = 3)", 0j, 3.0, {"power": 3.0}),
        Preset("Quártico (p = 4)", 0j, 3.0, {"power": 4.0}),
        Preset("Quíntico (p = 5)", 0j, 3.0, {"power": 5.0}),
        Preset("Expoente fraccionário (p = 2,5)", 0j, 3.0, {"power": 2.5}),
    ),
)

BURNING_SHIP = Formula(
    key="burning_ship",
    label="Burning Ship",
    description=(
        "Como o Mandelbrot, mas com o valor absoluto das partes real e "
        "imaginária antes de elevar ao quadrado. Daí os 'navios em chamas'. "
        "Muda o expoente para ver variantes."
    ),
    center=-0.5 - 0.5j,
    scale=4.0,
    init=start_at_zero,
    step=lambda z, c, p: power(abs_parts(z), p["power"]) + c,
    params=(POWER,),
    presets=(
        Preset("Casco e chamas", -1.76 - 0.03j, 0.2),
        Preset("Cortinas de chamas", -1.755 - 0.035j, 0.08),
        Preset("Variante cúbica (p = 3)", 0j, 4.0, {"power": 3.0}),
    ),
)

TRICORN = Formula(
    key="tricorn",
    label="Tricorn (Mandelbar)",
    description=(
        "Usa o conjugado de z em cada passo: z → conj(z)² + c. "
        "Em vez de um eixo de simetria, tem três."
    ),
    center=0j,
    scale=4.0,
    init=start_at_zero,
    step=lambda z, c, p: power(np.conj(z), p["power"]) + c,
    params=(POWER,),
    presets=(
        Preset("Detalhe lateral", -1.0 + 0j, 0.8),
        Preset("Variante cúbica (p = 3)", 0j, 4.0, {"power": 3.0}),
    ),
)

FORMULAS: dict[str, Formula] = {
    f.key: f for f in (MANDELBROT, JULIA, MULTIBROT, BURNING_SHIP, TRICORN)
}


def resolve_params(formula: Formula, given: Params | None = None) -> Params:
    """Valores finais dos parâmetros: os dados, e os predefinidos para o resto."""
    values = {p.key: p.default for p in formula.params}
    for key, value in (given or {}).items():
        if key in values:
            values[key] = float(value)
    return values


def describe() -> dict:
    """Metadados das fórmulas, em JSON, para a página construir os controlos."""
    return {
        f.key: {
            "label": f.label,
            "description": f.description,
            "cx": f.center.real,
            "cy": f.center.imag,
            "scale": f.scale,
            "params": [asdict(p) for p in f.params],
            "presets": [
                {
                    "label": s.label,
                    "cx": s.center.real,
                    "cy": s.center.imag,
                    "scale": s.scale,
                    "params": s.params,
                }
                for s in f.presets
            ],
        }
        for f in FORMULAS.values()
    }
