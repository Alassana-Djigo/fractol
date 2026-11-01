"""Leitura do ficheiro .env (sem dependências): linhas CHAVE=valor."""

import os
from pathlib import Path


def load_env_file(path: Path) -> None:
    """Define no ambiente as variáveis do ficheiro, sem sobrepor as já definidas."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))
