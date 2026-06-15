# RC1 Readiness

Status: not started.

## Summary

RC1 is not ready. The repository has the initial FastAPI service shell, typed configuration loading, public health/readiness endpoints, Bearer authentication for protected `/v1` endpoints, `GET /v1/models`, mocked `POST /v1/chat/completions`, safe base64 JPEG/PNG image decoding, a detector abstraction backed by a fake detector, and CI-backed test coverage, but no real YOLO integration yet.

## Readiness matrix

| Area | Status | Evidence | Notes |
|---|---|---|---|
| Constitution | Planned | `AGENTS.md` | Initial version generated |
| Architecture docs | Planned | `docs/architecture.md` | Initial version generated |
| API contract | Planned | `docs/api-contract.md` | Initial version generated |
| Security docs | Planned | `docs/security.md` | Initial version generated |
| FastAPI service | Implemented | `app/main.py` | App factory includes settings and health router |
| Config loading | Implemented | `app/config.py`, `tests/test_config.py` | Typed settings with `YOLO_SERVICE_` env prefix |
| Bearer auth | Implemented | `app/auth.py`, `tests/test_auth.py` | Static Bearer key for protected `/v1` endpoints |
| `/healthz` | Implemented | `app/api/health.py`, `tests/test_health.py` | Public liveness endpoint |
| `/readyz` | Implemented | `app/api/health.py`, `tests/test_health.py` | Public config readiness endpoint; does not load YOLO |
| `/v1/models` | Implemented | `app/api/models.py`, `tests/test_models.py` | Protected OpenAI-like model list |
| Testing baseline | Implemented | `scripts/check.sh`, `pyproject.toml`, `tests/` | Full local suite plus 80% app coverage threshold |
| `/v1/chat/completions` | Mocked | `app/api/chat.py`, `tests/test_chat_completions.py` | Contract implemented with decoded image input and mocked detector response; no real YOLO inference |
| Image decoding | Implemented | `app/vision/image_decode.py`, `tests/test_image_decode.py` | Base64 JPEG/PNG data URLs with MIME, payload, and pixel validation |
| Detector abstraction | Implemented | `app/vision/detector.py`, `app/vision/fake_detector.py`, `tests/test_detector.py` | Chat endpoint uses app-state detector interface with fake detector |
| Fake detector tests | Implemented | `app/vision/fake_detector.py`, `tests/test_detector.py` | Placeholder detector for chat contract only |
| Real YOLO11n CPU inference | Missing | None | Not implemented |
| Native detection endpoint | Missing | None | Not implemented |
| Docker | Missing | None | Not implemented |
| CI | Implemented | `.github/workflows/ci.yml` | Ruff plus pytest coverage on PRs and `main` |
| Browser demo | Missing | None | Not implemented |
| CPU backpressure | Missing | None | Not implemented |
| Security hardening | Missing | None | Not implemented |
| OpenAI Python example | Missing | None | Not verified |
| Manual YOLO smoke test | Missing | None | Not verified |
| License note | Planned | `docs/model-card.md` | Initial warning generated |

## RC1 blockers

- No real YOLO inference implemented yet.
- No model smoke test.
- No deployment artifact.
- No browser demo.
- License review not complete for commercial/closed deployment.

## RC1 exit criteria

See `docs/release-criteria.md`.
