import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

from .env import load_env_file

BASE_DIR = Path(__file__).resolve().parent.parent

# Variáveis de ambiente: lidas do ambiente e, se existir, do ficheiro .env
# (ver .env.example). O que já estiver definido no ambiente tem prioridade.
load_env_file(Path(os.environ.get("FRACTOL_ENV_FILE", BASE_DIR / ".env")))

# Seguro por omissão: sem DEBUG=1 explícito, o modo de depuração fica desligado.
DEBUG = os.environ.get("DEBUG", "0") == "1"

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            "Defina SECRET_KEY no ambiente ou no ficheiro .env (ver .env.example)."
        )
    SECRET_KEY = "dev-only-insecure-key"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "explorer",
]

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if not DEBUG:
    # Em produção os ficheiros estáticos são servidos pelo WhiteNoise.
    MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]

WSGI_APPLICATION = "config.wsgi.application"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # destino do collectstatic
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if DEBUG
            else "whitenoise.storage.CompressedStaticFilesStorage"
        )
    },
}

# Sem formulários nem sessões, mas fica seguro por omissão se vierem a existir.
CSRF_COOKIE_SECURE = not DEBUG

USE_TZ = True
