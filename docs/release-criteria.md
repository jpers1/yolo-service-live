# Release Criteria

Status: initial design.

## Release language

Use release language precisely.

Do not call the project production-ready unless production security, deployment, abuse, licensing, and operational requirements have been explicitly reviewed.

## MVP-minimal criteria

MVP-minimal may be declared when:

- FastAPI service runs locally on CPU.
- `/healthz` works.
- `/readyz` works.
- `/v1/models` works with auth.
- `/v1/chat/completions` accepts one base64 image.
- real YOLO11n CPU inference works manually.
- tests cover API behavior using fake detector.
- README includes working local instructions.
- limitations are documented.

## MVP-plus criteria

MVP-plus may be declared when MVP-minimal is complete and:

- `/v1/vision/detections` works.
- Dockerfile exists and local Docker run is documented.
- basic CI runs tests and lint.
- deployment docs exist.

## RC1 criteria

RC1 may be declared when:

- MVP-plus is complete.
- browser demo works locally.
- browser live mode uses backpressure and low FPS.
- full automated test suite passes.
- manual real YOLO smoke test passes.
- Docker smoke test is documented and passes manually.
- OpenAI Python example is verified.
- security document is aligned with code.
- API contract document is aligned with code.
- compatibility document is honest.
- known limitations are public.
- license note is present.
- `docs/state/rc1-readiness.md` is complete.
- human release authority approves.

## RC1 may claim

- CPU-only YOLO11n COCO object detection.
- Limited OpenAI-compatible chat-completions-style image detection endpoint.
- One-key Bearer-protected API.
- Native vision detection endpoint.
- Local browser camera demo.
- Dockerized local/internal deployment path.
- Test-backed behavior for supported API contract.

## RC1 must not claim

- full OpenAI API compatibility;
- general chatbot behavior;
- production certification;
- commercial license clearance;
- high-FPS CPU video analytics;
- public internet hardening;
- multi-user SaaS readiness;
- GPU optimization;
- real-time guarantees.

## Human release decision

The human release authority must review:

- goal match;
- test evidence;
- manual smoke evidence;
- security limitations;
- license limitations;
- performance limitations;
- documentation honesty.
