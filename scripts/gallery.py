"""Gera as imagens e o GIF do README e do LinkedIn, com o próprio motor.

    python scripts/gallery.py list
    python scripts/gallery.py images [--width 1920] [--format jpg|png] [--out PASTA]
    python scripts/gallery.py gif [--width 560] [--frames 56] [--out FICHEIRO.gif]

As cores vêm das mesmas paletas e modos da página.
"""

import argparse
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image

from fractol.coloring import PALETTES, build_lut, colorize
from fractol.formulas import FORMULAS
from fractol.fractals import compute_smooth


@dataclass(frozen=True)
class Scene:
    key: str
    formula: str
    center: complex
    scale: float
    iters: int
    palette: str
    mode: str = "ciclico"
    period: float = 24.0
    params: dict = field(default_factory=dict)
    flip: bool = False  # Burning Ship: orientação clássica (o navio de pé)
    aspect: float = 16 / 9


SPIRAL = complex(-0.7436438870371587, 0.13182590420531197)

SCENES = (
    Scene(
        "ship-nebula",
        "burning_ship",
        -1.76 - 0.03j,
        0.2,
        300,
        "nebulosa",
        "logaritmico",
        24,
        flip=True,
    ),
    Scene(
        "ship-nebula-square",
        "burning_ship",
        -1.76 - 0.03j,
        0.17,
        300,
        "nebulosa",
        "logaritmico",
        24,
        flip=True,
        aspect=1.0,
    ),
    Scene(
        "ship-electric",
        "burning_ship",
        -0.5 - 0.5j,
        4.0,
        200,
        "cosmica",
        "espelhado",
        14,
        flip=True,
    ),
    Scene(
        "ship-crown",
        "burning_ship",
        -1.862 + 0j,
        0.02,
        400,
        "psicadelico",
        "ciclico",
        20,
        flip=True,
    ),
    Scene(
        "mandelbrot-spiral",
        "mandelbrot",
        SPIRAL,
        0.0005,
        500,
        "psicadelico",
        "ciclico",
        24,
    ),
    Scene(
        "julia-rabbit",
        "julia",
        0j,
        3.0,
        300,
        "aurora",
        "logaritmico",
        24,
        {"jr": -0.123, "ji": 0.745},
    ),
    Scene(
        "multibrot-fractional",
        "multibrot",
        0j,
        3.0,
        250,
        "acido",
        "logaritmico",
        30,
        {"power": 2.5},
    ),
)


def render_scene(scene: Scene, width: int, offset: float = 0.0) -> Image.Image:
    height = round(width / scene.aspect)
    values = compute_smooth(
        scene.formula,
        width,
        height,
        scene.iters,
        scene.center,
        scene.scale,
        scene.params,
    )
    lut = build_lut(PALETTES[scene.palette])
    rgb = colorize(values, lut, scene.mode, scene.period, offset)
    return Image.fromarray(rgb[::-1] if scene.flip else rgb)


def zoom_path(start_center, start_scale, target, end_scale, frames):
    """Centro e escala de cada fotograma de um zoom suave até `target`."""
    ratio = end_scale / start_scale
    for k in range(frames):
        scale = start_scale * ratio ** (k / (frames - 1))
        yield target + (start_center - target) * (scale / start_scale), scale


def zoom_frames(width: int, frames: int):
    """Do navio inteiro até à coroa, em cores de nebulosa."""
    ship = FORMULAS["burning_ship"]
    target, end_scale = -1.862 + 0j, 0.02
    for center, scale in zoom_path(ship.center, ship.scale, target, end_scale, frames):
        iters = int(min(500, 120 + 35 * np.log2(ship.scale / scale)))
        scene = Scene(
            "zoom",
            "burning_ship",
            center,
            scale,
            iters,
            "nebulosa",
            "logaritmico",
            24,
            flip=True,
        )
        yield render_scene(scene, width)


def save_image(image: Image.Image, path: Path) -> None:
    if path.suffix == ".png":
        image.save(path, optimize=True)
    else:
        image.save(path, quality=93, subsampling=0)


def cmd_images(args) -> None:
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for scene in SCENES:
        start = time.perf_counter()
        width = round(args.width * 9 / 16) if scene.aspect == 1.0 else args.width
        path = out / f"{scene.key}.{args.format}"
        save_image(render_scene(scene, width), path)
        print(f"{path}  ({time.perf_counter() - start:.1f} s)")


def cmd_gif(args) -> None:
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames = [
        frame.quantize(colors=args.colors, dither=Image.Dither.NONE)
        for frame in zoom_frames(args.width, args.frames)
    ]
    count = len(frames)
    frames += [frames[-1]] * 8  # pausa no fim, antes de voltar ao início
    frames[0].save(
        out, save_all=True, append_images=frames[1:], optimize=True, duration=70, loop=0
    )
    print(f"{out}  ({out.stat().st_size / 1e6:.1f} MB, {count} fotogramas + pausa)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="mostra as cenas")
    images = sub.add_parser("images", help="gera as imagens")
    images.add_argument("--width", type=int, default=1920)
    images.add_argument("--format", choices=("jpg", "png"), default="jpg")
    images.add_argument("--out", default="assets/gallery")
    gif = sub.add_parser("gif", help="gera o GIF de zoom")
    gif.add_argument("--width", type=int, default=560)
    gif.add_argument("--frames", type=int, default=56)
    gif.add_argument("--colors", type=int, default=128)
    gif.add_argument("--out", default="assets/gallery/zoom.gif")
    args = parser.parse_args()
    if args.command == "list":
        for scene in SCENES:
            print(f"{scene.key:22s} {scene.formula:13s} {scene.palette}/{scene.mode}")
    elif args.command == "images":
        cmd_images(args)
    else:
        cmd_gif(args)


if __name__ == "__main__":
    main()
