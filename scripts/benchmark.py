import time

from fractol.render import render_mandelbrot
from fractol.render_np import render_mandelbrot_np

SIZE, MAX_ITER = 300, 100

t0 = time.perf_counter()
render_mandelbrot(SIZE, SIZE, MAX_ITER)
t1 = time.perf_counter()
render_mandelbrot_np(SIZE, SIZE, MAX_ITER)
t2 = time.perf_counter()

print(f"Puro:  {t1 - t0:.2f}s")
print(f"NumPy: {t2 - t1:.2f}s")
print(f"Speedup: {(t1 - t0) / (t2 - t1):.1f}x")
