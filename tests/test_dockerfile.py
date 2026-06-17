from pathlib import Path


def test_dockerfile_uses_buildkit_pip_cache() -> None:
    dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

    assert dockerfile.startswith("# syntax=docker/dockerfile:1.6")
    assert "--mount=type=cache,target=/root/.cache/pip" in dockerfile
    assert 'python -m pip install "${INSTALL_TARGET}"' in dockerfile
    assert "--no-cache-dir" not in dockerfile
    assert "PIP_NO_CACHE_DIR" not in dockerfile
