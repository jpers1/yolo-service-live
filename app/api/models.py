from typing import Annotated, Any

from fastapi import APIRouter, Depends

from app.auth import get_app_settings, require_api_key
from app.config import Settings

router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])


@router.get("/models")
def list_models(settings: Annotated[Settings, Depends(get_app_settings)]) -> dict[str, Any]:
    model_name = settings.public_model_name
    return {
        "object": "list",
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": 0,
                "owned_by": "local",
                "root": model_name,
                "parent": None,
            }
        ],
    }
