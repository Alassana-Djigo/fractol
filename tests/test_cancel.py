import threading
import time

import pytest

from explorer.latest import LatestRequests
from fractol.fractals import Cancelled, compute_smooth

SPIRAL = complex(-0.7436438870371587, 0.13182590420531197)


def test_latest_marks_older_requests_as_stale():
    latest = LatestRequests()
    latest.note("a", 1)
    assert not latest.is_stale("a", 1)
    latest.note("a", 3)
    assert latest.is_stale("a", 1)
    assert not latest.is_stale("a", 3)
    assert not latest.is_stale("outro", 0)  # cada cliente tem o seu


def test_latest_ignores_out_of_order_notes_and_forgets_old_clients():
    latest = LatestRequests(max_clients=2)
    latest.note("a", 5)
    latest.note("a", 2)  # chegou atrasado: não recua
    assert latest.is_stale("a", 4)
    latest.note("b", 1)
    latest.note("c", 1)  # passa o limite: "a" é esquecido
    assert not latest.is_stale("a", 0)


def test_engine_stops_when_asked():
    with pytest.raises(Cancelled):
        compute_smooth("mandelbrot", 20, 20, 50, should_stop=lambda: True)


def test_engine_with_a_calm_stop_function_gives_the_same_result():
    plain = compute_smooth("julia", 30, 20, 60)
    watched = compute_smooth("julia", 30, 20, 60, should_stop=lambda: False)
    assert (plain == watched).all()


def test_a_running_computation_is_cancelled_quickly():
    stop = threading.Event()
    outcome = {}

    def work():
        try:
            compute_smooth(
                "mandelbrot", 1200, 840, 500, SPIRAL, 0.0005, should_stop=stop.is_set
            )
            outcome["result"] = "terminou"
        except Cancelled:
            outcome["result"] = "cancelado"

    thread = threading.Thread(target=work)
    thread.start()
    time.sleep(0.2)
    started = time.perf_counter()
    stop.set()
    thread.join(timeout=5)
    assert outcome.get("result") == "cancelado"
    assert time.perf_counter() - started < 1.0
