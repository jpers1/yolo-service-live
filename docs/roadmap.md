# Roadmap

Status: initial design.

## Guiding principle

Work must be split into micro-PRs suitable for a small/medium execution coding agent.

One PR = one behavior.

## MVP-minimal

MVP-minimal is complete when the repository has:

- `AGENTS.md`;
- documentation skeleton;
- FastAPI app;
- config loading;
- Bearer API-key auth;
- `/healthz`;
- `/readyz`;
- `/v1/models`;
- `/v1/chat/completions`;
- base64 data URL image input;
- safe image decoding;
- YOLO11n CPU inference;
- structured detection JSON;
- tests using fake detector;
- manual real-model smoke test;
- README with OpenAI Python example.

## MVP-plus

MVP-plus additionally includes:

- `/v1/vision/detections`;
- Dockerfile;
- basic CI;
- deployment docs.

Recommended first target: MVP-plus.

## RC1

RC1 is complete when MVP-plus is stable and the project also has:

- browser camera demo;
- adaptive CPU live loop;
- Docker smoke instructions;
- stronger security hardening;
- documented limitations;
- manual real YOLO smoke test;
- OpenAI Python example verified;
- browser demo verification;
- `docs/state/rc1-readiness.md` complete;
- release criteria accepted by human release authority.

## Post-RC1

Possible later work:

- WebSocket live detection stream;
- OpenAI-style `stream: true` SSE;
- external image URL fetching with SSRF protections;
- more YOLO models;
- ONNX export path;
- rate limiting;
- Redis only if queue/rate/multi-worker state becomes necessary;
- user accounts only if multi-user product scope is approved;
- GPU deployment path only if CPU-only constraint changes.

## Micro-PR plan

### Phase 0: Governance

- PR 0.1: Add `AGENTS.md`.
- PR 0.2: Add docs skeleton.
- PR 0.3: Add `.env.example` and repo hygiene.

### Phase 1: FastAPI shell

- PR 1.1: Add Python project structure.
- PR 1.2: Add minimal FastAPI app.
- PR 1.3: Add `/healthz`.
- PR 1.4: Add config loading.
- PR 1.5: Add `/readyz`.

### Phase 2: Auth and model listing

- PR 2.1: Add Bearer auth helper.
- PR 2.2: Protect `/v1/models`.
- PR 2.3: Add OpenAI-like model list.
- PR 2.4: Add OpenAI-like error response helpers.

### Phase 3: Chat contract with fake detector

- PR 3.1: Add minimal `/v1/chat/completions`.
- PR 3.2: Add request schema.
- PR 3.3: Validate supported model only.
- PR 3.4: Extract image content part.
- PR 3.5: Reject missing/multiple images.
- PR 3.6: Return OpenAI-shaped response envelope.

### Phase 4: Image input

- PR 4.1: Parse base64 data URLs.
- PR 4.2: Reject non-data URLs.
- PR 4.3: Decode JPEG/PNG with Pillow.
- PR 4.4: Enforce payload size.
- PR 4.5: Enforce image dimensions.
- PR 4.6: Convert decoded image to RGB.

### Phase 5: Detector abstraction

- PR 5.1: Define detection schema.
- PR 5.2: Define detector interface.
- PR 5.3: Add fake detector.
- PR 5.4: Connect fake detector to chat endpoint.

### Phase 6: Real YOLO

- PR 6.1: Add Ultralytics dependency.
- PR 6.2: Add YOLO service loader.
- PR 6.3: Add YOLO result postprocessing.
- PR 6.4: Add manual smoke script.
- PR 6.5: Switch runtime detector from fake to real by config.
- PR 6.6: Document first-run model download.

### Phase 7: Native endpoint

- PR 7.1: Add `/v1/vision/detections` schema.
- PR 7.2: Implement endpoint with fake detector.
- PR 7.3: Connect endpoint to real detector path.
- PR 7.4: Add curl examples.

### Phase 8: Docker and CI

- PR 8.1: Add basic CI.
- PR 8.2: Add Ruff config.
- PR 8.3: Add Dockerfile.
- PR 8.4: Add Docker run docs.
- PR 8.5: Add Docker smoke test instructions.

### Phase 9: Browser demo

- PR 9.1: Serve static demo page.
- PR 9.2: Add camera preview.
- PR 9.3: Add one-frame capture.
- PR 9.4: Send one frame to API and display JSON.
- PR 9.5: Draw boxes.
- PR 9.6: Add simple live loop.
- PR 9.7: Add FPS/latency display.
- PR 9.8: Add confidence slider.

### Phase 10: RC1 hardening

- PR 10.1: Add request ID logging.
- PR 10.2: Add no-secret logging checks.
- PR 10.3: Add concurrency guard.
- PR 10.4: Add timeout policy.
- PR 10.5: Add CORS config.
- PR 10.6: Improve errors.
- PR 10.7: Add known limitations doc.
- PR 10.8: Add RC1 verification checklist.
