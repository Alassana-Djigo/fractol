import pytest

from fractol.formulas import FORMULAS


def test_render_returns_png(client):
    response = client.get("/render/?fractal=julia&w=40&h=30&iter=20")
    assert response.status_code == 200
    assert response["Content-Type"] == "image/png"
    assert response.content.startswith(b"\x89PNG")


@pytest.mark.parametrize(
    "query",
    ["fractal=nope", "w=0", "w=abc", "iter=99999", "scale=-1", "cx=nan"],
)
def test_render_rejects_bad_input(client, query):
    assert client.get(f"/render/?{query}").status_code == 400


def test_index_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"fractol" in response.content.lower()


def test_julia_parameters_change_the_image(client):
    base = "/render/?fractal=julia&w=40&h=30&iter=50"
    a = client.get(f"{base}&jr=-0.8&ji=0.156")
    b = client.get(f"{base}&jr=0.285&ji=0.01")
    assert a.content != b.content


def test_data_returns_float32_grid(client):
    response = client.get("/data/?fractal=mandelbrot&w=40&h=30&iter=50")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/octet-stream"
    assert len(response.content) == 40 * 30 * 4


@pytest.mark.parametrize("query", ["fractal=nope", "w=0", "iter=99999", "cx=nan"])
def test_data_rejects_bad_input(client, query):
    assert client.get(f"/data/?{query}").status_code == 400


@pytest.mark.parametrize(
    "query",
    [
        "fractal=multibrot&power=1",
        "fractal=multibrot&power=9",
        "fractal=julia&jr=5",
        "fractal=burning_ship&power=abc",
    ],
)
def test_data_rejects_params_outside_declared_range(client, query):
    assert client.get(f"/data/?{query}").status_code == 400


def test_every_formula_is_served(client):
    for key in FORMULAS:
        response = client.get(f"/data/?fractal={key}&w=20&h=10&iter=30")
        assert response.status_code == 200, key
