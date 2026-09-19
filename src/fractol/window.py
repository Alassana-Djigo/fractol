"""Interactive fractol window using Pygame."""

import sys

import pygame

from fractol.render_np import compute_iterations_grid, grid_to_image

WIDTH, HEIGHT = 800, 800
MAX_ITER = 100


def render_surface(width: int, height: int, max_iter: int) -> pygame.Surface:
    """Gera o fractal e devolve já como pygame.Surface, pronto a desenhar."""
    iterations = compute_iterations_grid(width, height, max_iter)
    image = grid_to_image(iterations, max_iter).convert("RGB")
    return pygame.image.fromstring(image.tobytes(), image.size, "RGB")


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("fractol — Mandelbrot")
    clock = pygame.time.Clock()

    surface = render_surface(WIDTH, HEIGHT, MAX_ITER)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.blit(surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
