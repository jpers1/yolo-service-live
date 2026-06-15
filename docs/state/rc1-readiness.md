# RC1 Readiness

Status: not started.

## Summary

RC1 is not ready. The repository has the initial FastAPI service shell, typed configuration loading, and public health/readiness endpoints, but no authenticated `/v1/*` API behavior or detector integration yet.

## Readiness matrix

| Area | Status | Evidence | Notes |
|---|---|---|---|
| Constitution | Planned | `AGENTS.md` | Initial version generated |
| Architecture docs | Planned | `docs/architecture.md` | Initial version generated |
| API contract | Planned | `docs/api-contract.md` | Initial version generated |
| Security docs | Planned | `docs/security.md` | Initial version generated |
| FastAPI service | Implemented | `app/main.py` | App factory includes settings and health router |
| Config loading | Implemented | `app/config.py`, `tests/test_config.py` | Typed settings with `YOLO_SERVICE_` env prefix |
| Bearer auth | Missing | None | Not implemented |
| `/healthz` | Implemented | `app/api/health.py`, `tests/test_health.py` | Public liveness endpoint |
| `/readyz` | Implemented | `app/api/health.py`, `tests/test_health.py` | Public config readiness endpoint; does not load YOLO |
| `/v1/models` | Missing | None | Not implemented |
| `/v1/chat/completions` | Missing | None | Not implemented |
| Image decoding | Missing | None | Not implemented |
| Fake detector tests | Missing | None | Not implemented |
| Real YOLO11n CPU inference | Missing | None | Not implemented |
| Native detection endpoint | Missing | None | Not implemented |
| Docker | Missing | None | Not implemented |
| CI | Missing | None | Not implemented |
| Browser demo | Missing | None | Not implemented |
| CPU backpressure | Missing | None | Not implemented |
| Security hardening | Missing | None | Not implemented |
| OpenAI Python example | Missing | None | Not verified |
| Manual YOLO smoke test | Missing | None | Not verified |
| License note | Planned | `docs/model-card.md` | Initial warning generated |

## RC1 blockers

- No Bearer auth implemented yet.
- No `/v1/*` API behavior implemented yet.
- No image decoding implemented yet.
- No detector abstraction implemented yet.
- No real YOLO inference implemented yet.
- No model smoke test.
- No deployment artifact.
- No browser demo.
- License review not complete for commercial/closed deployment.

## RC1 exit criteria

See `docs/release-criteria.md`.
