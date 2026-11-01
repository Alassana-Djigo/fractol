"""Definições para os testes: modo de desenvolvimento, sem depender de .env."""

import os

os.environ.setdefault("DEBUG", "1")
os.environ.setdefault("SECRET_KEY", "test-only-key")

from .settings import *  # noqa: E402, F403
