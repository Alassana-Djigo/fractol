import dataclasses
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image

from fractol.coloring import MODES, PALETTES
from fractol.formulas import FORMULAS

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "gallery.py"
spec = importlib.util.spec_from_file_location("gallery", SCRIPT)
gallery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gallery)


def test_scenes_only_use_things_that_exist():
    keys = [scene.key for scene in gallery.SCENES]
    assert len(keys) == len(set(keys))
    for scene in gallery.SCENES:
        formula = FORMULAS[scene.formula]
        assert scene.palette in PALETTES
        assert scene.mode in MODES
        assert set(scene.params) <= {p.key for p in formula.params}


def test_every_scene_renders_something_colourful():
    for scene in gallery.SCENES:
        image = gallery.render_scene(scene, 96)
        assert image.size == (96, round(96 / scene.aspect))
        colours = np.unique(np.asarray(image).reshape(-1, 3), axis=0)
        assert len(colours) > 20, scene.key


def test_flip_turns_the_image_upside_down():
    scene = next(s for s in gallery.SCENES if s.flip)
    flipped = np.asarray(gallery.render_scene(scene, 64))
    plain = np.asarray(gallery.render_scene(dataclasses.replace(scene, flip=False), 64))
    assert np.array_equal(flipped, plain[::-1])


def test_zoom_path_goes_smoothly_to_the_target():
    start, target, frames = -0.5 - 0.5j, -1.862 + 0j, 10
    path = list(gallery.zoom_path(start, 4.0, target, 0.02, frames))
    scales = [scale for _, scale in path]
    assert path[0] == (start, 4.0)
    assert scales[-1] == np.float64(0.02)
    assert all(a > b for a, b in zip(scales, scales[1:], strict=False))
    ratio = 0.02 / 4.0
    assert abs(path[-1][0] - (target + (start - target) * ratio)) < 1e-12


def test_images_command_writes_one_file_per_scene(tmp_path):
    args = SimpleNamespace(out=str(tmp_path / "g"), width=64, format="jpg")
    gallery.cmd_images(args)
    files = sorted(p.name for p in (tmp_path / "g").iterdir())
    assert files == sorted(f"{s.key}.jpg" for s in gallery.SCENES)
    assert Image.open(tmp_path / "g" / "ship-nebula.jpg").size == (64, 36)


def test_gif_command_writes_a_looping_animation(tmp_path):
    out = tmp_path / "zoom.gif"
    gallery.cmd_gif(SimpleNamespace(out=str(out), width=48, frames=4, colors=32))
    gif = Image.open(out)
    assert gif.size == (48, 27)
    assert gif.n_frames >= 4
    assert gif.info["loop"] == 0


def test_save_image_handles_large_noisy_images(tmp_path):
    # imagens muito ruidosas (como um fractal em zoom profundo) já deram erro
    # ao gravar JPEG com `optimize=True`
    noise = np.random.default_rng(0).integers(0, 256, (1080, 1920, 3), dtype=np.uint8)
    path = tmp_path / "ruido.jpg"
    gallery.save_image(Image.fromarray(noise), path)
    assert Image.open(path).size == (1920, 1080)
