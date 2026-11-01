import os
import re
import subprocess
import sys
from pathlib import Path

from django.core.management import call_command

from config.env import load_env_file
from explorer import views

ROOT = Path(__file__).resolve().parent.parent
MANAGED = ("DEBUG", "SECRET_KEY", "ALLOWED_HOSTS")


def settings_value(expression, **env):
    """Avalia uma expressão sobre as definições, num processo à parte."""
    full_env = {k: v for k, v in os.environ.items() if k not in MANAGED}
    full_env["DJANGO_SETTINGS_MODULE"] = "config.settings"
    full_env["FRACTOL_ENV_FILE"] = str(ROOT / "nao-existe.env")
    full_env.update(env)
    code = f"from django.conf import settings; print({expression})"
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=full_env,
        capture_output=True,
        text=True,
    )


def test_production_refuses_to_start_without_a_secret_key():
    result = settings_value("settings.DEBUG", DEBUG="0")
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_debug_is_off_unless_explicitly_enabled():
    result = settings_value("settings.DEBUG", SECRET_KEY="x")
    assert result.stdout.strip() == "False"


def test_development_mode_works_without_a_secret_key():
    result = settings_value("settings.DEBUG", DEBUG="1")
    assert result.stdout.strip() == "True"


def test_allowed_hosts_come_from_the_environment():
    result = settings_value(
        "settings.ALLOWED_HOSTS", SECRET_KEY="x", ALLOWED_HOSTS="a.com, b.com"
    )
    assert result.stdout.strip() == "['a.com', 'b.com']"


def test_whitenoise_is_only_active_in_production():
    check = "'whitenoise.middleware.WhiteNoiseMiddleware' in settings.MIDDLEWARE"
    assert settings_value(check, SECRET_KEY="x").stdout.strip() == "True"
    assert settings_value(check, DEBUG="1").stdout.strip() == "False"


def test_deploy_check_only_reports_the_https_settings_left_to_the_host():
    env = {k: v for k, v in os.environ.items() if k not in MANAGED}
    env.update(
        DJANGO_SETTINGS_MODULE="config.settings",
        FRACTOL_ENV_FILE=str(ROOT / "nao-existe.env"),
        DEBUG="0",
        SECRET_KEY="abcdefghijklmnopqrstuvwxyz0123456789" * 2,
        ALLOWED_HOSTS="exemplo.com",
    )
    result = subprocess.run(
        [sys.executable, "manage.py", "check", "--deploy"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    found = set(re.findall(r"\((security\.W\d+)\)", result.stdout + result.stderr))
    # HSTS (W004) e redirecção para HTTPS (W008) ficam a cargo do alojamento
    assert found == {"security.W004", "security.W008"}


def test_env_file_fills_only_missing_variables(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "environ", {"EXISTENTE": "do-ambiente"})
    env_file = tmp_path / ".env"
    env_file.write_text(
        '# comentário\nA_VAR=1\nB_VAR="dois"\n\nC_VAR = três \nEXISTENTE=do-ficheiro\n'
    )
    load_env_file(env_file)
    assert os.environ == {
        "EXISTENTE": "do-ambiente",
        "A_VAR": "1",
        "B_VAR": "dois",
        "C_VAR": "três",
    }


def test_missing_env_file_is_fine(tmp_path):
    load_env_file(tmp_path / "nao-existe.env")


def test_collectstatic_gathers_the_page_files(settings, tmp_path):
    settings.STATIC_ROOT = tmp_path
    call_command("collectstatic", interactive=False, verbosity=0)
    assert (tmp_path / "explorer" / "app.js").is_file()
    assert (tmp_path / "explorer" / "coloring.js").is_file()


def test_server_limits_are_configurable(client, monkeypatch):
    monkeypatch.setattr(views, "MAX_ITER", 50)
    monkeypatch.setattr(views, "MAX_SIZE", 100)
    assert client.get("/data/?w=30&h=20&iter=50").status_code == 200
    assert client.get("/data/?w=30&h=20&iter=51").status_code == 400
    assert client.get("/data/?w=101&h=20&iter=10").status_code == 400


def test_index_tells_the_page_about_the_limits(client):
    assert b"limits-data" in client.get("/").content
