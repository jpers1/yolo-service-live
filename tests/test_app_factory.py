from fastapi import FastAPI

from app.main import app, create_app


def test_create_app_returns_fastapi_instance() -> None:
    created_app = create_app()

    assert isinstance(created_app, FastAPI)
    assert created_app.title == "YOLO OpenAI Vision API"


def test_module_level_app_exists() -> None:
    assert isinstance(app, FastAPI)
