from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(
        title="YOLO OpenAI Vision API",
        version="0.1.0",
        description="CPU-only YOLO11 object detection service with OpenAI-compatible API endpoints.",
    )


app = create_app()

