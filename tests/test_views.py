import pytest

from explorer.cache import DATA_CACHE
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


def test_data_returns_uint16_grid(client):
    response = client.get("/data/?fractal=mandelbrot&w=40&h=30&iter=50")
    assert response.status_code == 200
    assert response["Content-Type"] == "application/octet-stream"
    assert response["X-Nu-Scale"] == "64"
    assert len(response.content) == 40 * 30 * 2


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


def test_index_embeds_formula_metadata(client):
    assert b"formulas-data" in client.get("/").content


def test_data_is_cached_and_reports_it(client):
    DATA_CACHE.clear()
    url = "/data/?fractal=julia&w=30&h=20&iter=40&jr=-0.4&ji=0.6"
    first = client.get(url)
    second = client.get(url)
    other = client.get(url + "&power=3")
    assert first["X-Cache"] == "miss"
    assert second["X-Cache"] == "hit"
    assert first.content == second.content
    assert other["X-Cache"] == "miss"
    assert other.content != first.content


def test_data_is_gzipped_when_the_browser_accepts_it(client):
    response = client.get(
        "/data/?w=60&h=40&iter=30", headers={"accept-encoding": "gzip"}
    )
    assert response["Content-Encoding"] == "gzip"


def test_stale_request_is_dropped_with_204(client):
    DATA_CACHE.clear()
    new = client.get("/data/?w=30&h=20&iter=40&client=pagina1&rid=5")
    old = client.get("/data/?w=31&h=20&iter=40&client=pagina1&rid=3")
    assert new.status_code == 200
    assert old.status_code == 204
    assert old.content == b""


def test_request_ids_are_optional_and_validated(client):
    assert client.get("/data/?w=30&h=20&iter=40").status_code == 200
    assert client.get("/data/?w=30&h=20&client=a b&rid=1").status_code == 400
    assert client.get("/data/?w=30&h=20&client=ok&rid=x").status_code == 400
