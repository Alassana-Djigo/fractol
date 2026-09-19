"""Renderização do conjunto de Mandelbrot em escala de cinzentos."""

from PIL import Image

from fractol.escape import escape_iterations
from fractol.mapping import pixel_to_complex


def _grayscale_from_iterations(iterations: int, max_iter: int) -> int:
    """
    Converte uma contagem de iterações num valor de cinza (0-255).

    Pontos que nunca escapam (pertencem ao conjunto) ficam pretos.
    Quanto mais devagar um ponto escapa (mais perto da fronteira
    do conjunto), mais claro fica.
    """
    if iterations == max_iter:
        return 0
    return int(255 * iterations / max_iter)


def render_mandelbrot(width: int, height: int, max_iter: int = 100) -> Image.Image:
    """
    Gera a imagem do conjunto de Mandelbrot em escala de cinzentos.

    Para cada pixel (px, py):
      1. converte-o no ponto complexo c correspondente;
      2. corre a iteração de fuga a partir de z0 = 0;
      3. pinta o pixel consoante o número de iterações.

    Nota de performance: Python puro, pixel a pixel, de propósito —
    é lento; resolvemos isso com NumPy na próxima fase. Por agora
    o objetivo é correção, não velocidade.
    """
    image = Image.new("L", (width, height))
    for py in range(height):
        for px in range(width):
            c = pixel_to_complex(px, py, width, height)
            iterations = escape_iterations(0, c, max_iter)
            gray = _grayscale_from_iterations(iterations, max_iter)
            image.putpixel((px, py), gray)
    return image


if __name__ == "__main__":
    render_mandelbrot(600, 600).save("assets/mandelbrot_v1.png")