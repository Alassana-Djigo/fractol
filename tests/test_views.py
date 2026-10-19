import pytest


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
