# Security Model

Status: initial design.

## Security goal

The service should be safe enough for local/internal CPU inference and browser demos. It is not initially production-certified for public internet exposure.

## Primary assets

- API key.
- Host system resources.
- CPU availability.
- User-submitted images.
- Model files.
- Logs.
- Browser demo users.

## Main threats

| Threat | Risk | MVP mitigation |
|---|---|---|
| API key leakage | Unauthorized use | Bearer key from env; no logging; no committed secrets |
| SSRF via image URLs | Server fetches internal network resources | Reject arbitrary external URLs in MVP |
| Large payload DoS | CPU/RAM exhaustion | Request size and image pixel limits |
| Frame queue buildup | Browser demo lag and resource exhaustion | Send next frame only after previous response |
| Secret logging | Credentials appear in logs or CI | No API key logging; no env dumps |
| Image persistence | Privacy leakage | Do not store images or request bodies |
| CORS overexposure | Browser misuse | Safe defaults; document changes |
| Dependency/license risk | Invalid release claims | License note and dependency review |
| False compatibility claims | Users misuse API | Explicit compatibility docs |
| GPU dependency creep | Fails on CPU target | CPU-only rule in AGENTS.md and docs |

## Authentication

All `/v1/*` endpoints require:

```http
Authorization: Bearer <YOLO_SERVICE_API_KEY>
```

Rules:

- Missing token -> 401.
- Wrong scheme -> 401.
- Wrong token -> 401.
- Do not log the provided token.
- Do not log expected token.
- Use constant-time comparison where practical.

## Secrets

Do not commit:

```text
.env
real API keys
provider keys
private SSH keys
cloud credentials
browser profiles
password-store files
```

Only `.env.example` may be committed, and it must contain fake placeholders.

## Image input policy

MVP allowed input:

```text
data:image/jpeg;base64,...
data:image/png;base64,...
```

The service validates image input by requiring base64 data URLs, using a JPEG/PNG MIME allowlist, decoding base64 with strict validation, opening the image with Pillow, verifying the decoded image format matches the declared MIME type, and enforcing configured payload and pixel limits.

MVP rejected input:

```text
http://...
https://...
file://...
ftp://...
arbitrary local paths
```

Rationale: external URL fetching requires SSRF protection, redirect handling, DNS/IP filtering, size caps, content-type validation, and timeout policy. This is out of scope for MVP.

## Payload limits

The service must enforce:

- maximum request body bytes;
- maximum decoded image pixels;
- supported MIME types;
- sane confidence/IoU bounds;
- timeout policy once available;
- concurrency/busy behavior once available.

Exact values are configured by environment and documented in `.env.example`.

Current defaults:

```text
YOLO_SERVICE_MAX_REQUEST_BYTES=5242880
YOLO_SERVICE_MAX_IMAGE_PIXELS=4194304
```

Image bytes are decoded in memory only. The service must not write uploaded image bytes to disk, persist request bodies, log base64 payloads, or return raw image bytes in API responses.

## Logging

Logs may include:

- request ID;
- endpoint;
- status code;
- latency;
- model name;
- image dimensions;
- number of detections.

Logs must not include:

- API keys;
- full Authorization headers;
- base64 image payloads;
- raw request bodies;
- production secrets;
- browser camera frames.

## Browser demo security

For local/internal demo, the page may allow the user to type the API key into a field.

Do not hard-code the real API key in public JavaScript.

The current `/demo` page keeps the entered API key in browser memory only and uses it
for same-origin calls to `/v1/vision/detections`. It must be treated as local/demo-only
because any browser-entered API key is visible to that page runtime.

Do not expose the demo on the public internet with a shared real API key.

For public deployment, a different auth/session model is needed. That is outside v0.

## CORS

Default CORS should be restrictive.

Recommended initial origins:

```text
http://localhost:8000
http://127.0.0.1:8000
```

Any widening of CORS must be documented.

## Container security

The Docker baseline follows these rules:

- the container runs as a non-root user;
- API keys are passed at runtime as environment variables;
- `.env` is excluded from the Docker build context;
- real secrets must not be baked into image layers;
- uploaded images and request bodies are not persisted;
- arbitrary external image URL fetching remains unsupported;
- debug mode is not enabled;
- `/healthz` and `/readyz` remain public;
- `/v1/*` endpoints remain Bearer-authenticated.

## Fail-closed behavior

Reject when uncertain:

- unknown model;
- unsupported image format;
- external URL in MVP;
- oversized request;
- malformed image;
- missing key;
- invalid key;
- unsupported stream mode.

## Production warning

RC1 may be suitable for local/internal demonstrations. Production public deployment requires additional review:

- TLS termination;
- reverse proxy hardening;
- real secret management;
- rate limiting;
- observability;
- vulnerability scanning;
- dependency/license review;
- abuse controls;
- public-browser auth redesign;
- operational runbook.
