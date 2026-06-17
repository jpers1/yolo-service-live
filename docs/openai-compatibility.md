# OpenAI Compatibility

Status: initial design.

## Compatibility goal

This project is OpenAI-compatible only in a limited, explicit sense.

The goal is to let users reuse the familiar OpenAI client pattern:

```python
from openai import OpenAI

client = OpenAI(
    api_key="dev-secret",
    base_url="http://localhost:8000/v1",
)
```

and send an image through a chat-completions-style request.

## Supported OpenAI-style features

Planned for MVP:

- `GET /v1/models`
- `POST /v1/chat/completions`
- `Authorization: Bearer <key>`
- `model: "yolo11n-coco"`
- `messages` with content parts
- `content` parts of type `text`
- `content` parts of type `image_url`
- base64 data URLs inside `image_url.url`
- OpenAI-shaped response envelope
- OpenAI-like error object

Current implementation note: `POST /v1/chat/completions` validates the model, rejects `stream: true`, requires exactly one `image_url` content part, decodes base64 JPEG/PNG data URLs, and returns assistant `content` as a JSON string. The endpoint calls the configured detector backend. The fake backend is used for normal tests, and the YOLO backend can run real CPU inference when the optional YOLO extra and weights are available.

## Not supported in MVP

- general text chat;
- tool/function calling;
- JSON schema response formats;
- embeddings;
- audio;
- image generation;
- multi-turn language behavior;
- multiple models;
- arbitrary external image URL fetching;
- file uploads;
- billing/token accounting;
- `stream: true`;
- organization/project/user semantics;
- full OpenAI error parity.

## Important semantic difference

The service does not answer the user's text prompt as an LLM.

For MVP, the text prompt may be accepted as part of the OpenAI request shape, but object detection behavior is determined by the image and model settings.

The assistant message `content` should be structured JSON containing detection results.

`POST /v1/vision/detections` is a service-native endpoint for browser/demo clients. It is not part of the OpenAI API surface and returns detection JSON directly instead of an OpenAI chat-completion envelope.

## Image input basis

The OpenAI chat-completions API documents image content parts using `image_url`, where the `url` field can be either an image URL or base64 encoded image data. OpenAI's vision guide shows examples using `data:image/jpeg;base64,...`.

This service supports base64 `data:image/jpeg;base64,...` and `data:image/png;base64,...` inputs first. Arbitrary HTTP(S) image URLs remain unsupported in MVP.

## Why not external URLs in MVP?

External URL fetching creates SSRF and network trust risks. The MVP rejects arbitrary `http://` and `https://` URLs until a later explicit security-hardening decision is made.

## Stream compatibility

`stream: true` is post-MVP. If implemented, it should use Server-Sent Events with chunks compatible enough for simple OpenAI-style client iteration.

For object detection, streaming is not critical for single-image inference. Browser live processing should use repeated HTTP first.

## Compatibility test expectations

Tests should prove:

- OpenAI-style auth header works.
- OpenAI-style `messages` request parses.
- `image_url.url` data URL input works.
- unsupported model is rejected.
- missing image is rejected.
- response contains OpenAI-shaped envelope.
- assistant message content is valid JSON detection payload.

## Compatibility language

Do not claim:

```text
Full OpenAI-compatible API
```

Prefer:

```text
OpenAI-compatible chat-completions-style image detection endpoint
```

or:

```text
Limited OpenAI-compatible API surface for YOLO object detection
```
