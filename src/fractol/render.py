from PIL import Image


def render_mandelbrot(width: int, height: int, max_iter: int = 100) -> Image.Image:
    """
    Gera a imagem do Mandelbrot em escala de cinzentos:
    para cada pixel, calcula o ponto complexo, corre a
    iteração de fuga, e pinta consoante o resultado.
    """
