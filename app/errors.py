from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class OpenAIError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        message: str,
        error_type: str,
        code: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.body = openai_error_body(message=message, error_type=error_type, code=code)
        self.headers = headers


def openai_error_body(
    *,
    message: str,
    error_type: str,
    code: str,
    param: str | None = None,
) -> dict[str, dict[str, Any]]:
    return {
        "error": {
            "message": message,
            "type": error_type,
            "param": param,
            "code": code,
        }
    }


def openai_error(
    *,
    status_code: int,
    message: str,
    error_type: str,
    code: str,
    headers: dict[str, str] | None = None,
) -> OpenAIError:
    return OpenAIError(
        status_code=status_code,
        message=message,
        error_type=error_type,
        code=code,
        headers=headers,
    )


async def openai_error_handler(_request: Request, exc: OpenAIError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.body, headers=exc.headers)
