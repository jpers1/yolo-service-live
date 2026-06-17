from importlib.resources import files
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


router = APIRouter()
STATIC_DIR = Path(str(files("app").joinpath("static")))


@router.get("/demo", include_in_schema=False)
def get_demo_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "demo.html", media_type="text/html")


def demo_static_files() -> StaticFiles:
    return StaticFiles(directory=STATIC_DIR)
