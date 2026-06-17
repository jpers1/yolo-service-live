# API Contract

Status: initial design. This document defines the intended public API. Code must not silently diverge from this document.

## Authentication

All `/v1/*` endpoints require:

```http
Authorization: Bearer <YOLO_SERVICE_API_KEY>
```

`/healthz` may be public.

`/readyz` may be public but must not expose secrets.

## Public model name

```text
yolo11n-coco
```

## Endpoints

```text
GET  /healthz
GET  /readyz
GET  /v1/models
POST /v1/chat/completions
POST /v1/vision/detections
```

Later:

```text
GET /demo
WebSocket /v1/vision/detections/stream
```

## GET /healthz

Purpose: process liveness.

Response:

```json
{
  "status": "ok"
}
```

No auth required.

## GET /readyz

Purpose: configuration/model readiness.

Initial response shape:

```json
{
  "status": "ok",
  "model": "yolo11n-coco"
}
```

The response must not include API keys, secrets, full paths with sensitive data, or environment dumps.

## GET /v1/models

Purpose: OpenAI-like model listing.

Requires auth.

Planned response:

```json
{
  "object": "list",
  "data": [
    {
      "id": "yolo11n-coco",
      "object": "model",
      "created": 0,
      "owned_by": "local"
    }
  ]
}
```

## POST /v1/chat/completions

Purpose: OpenAI-compatible wrapper for object detection.

Requires auth.

### Minimal supported request

```json
{
  "model": "yolo11n-coco",
  "messages": [
    {
      "role": "user",
      "content": [
        { "type": "text", "text": "detect objects" },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,..."
          }
        }
      ]
    }
  ]
}
```

### MVP request rules

- `model` must be `yolo11n-coco`.
- `messages` must contain exactly one supported image.
- Supported image content type is `image_url`.
- Supported `image_url.url` values are base64 data URLs:
  - `data:image/jpeg;base64,...`
  - `data:image/png;base64,...`
- JPEG and PNG data URLs are base64-decoded and validated before returning success.
- The decoded image format must match the declared data URL MIME type.
- Encoded payload size and decoded image pixel limits are enforced from service settings.
- Arbitrary external `http://` or `https://` image URLs are rejected in MVP.
- `stream: true` is not supported in MVP unless a later PR implements it.
- Text prompt content may be accepted but should not alter detection behavior in MVP.
- Unknown fields may be ignored if this is documented and tested.

Current implementation note: the endpoint requires exactly one `image_url` content part, decodes and validates base64 JPEG/PNG data URLs, and rejects external URLs. It calls the configured detector backend. The fake backend returns `"mock": true`; the YOLO backend returns real detections with `"mock": false`.

### Planned response

The response should use an OpenAI-shaped chat-completion envelope.

The assistant `content` is a JSON string, not prose.

```json
{
  "id": "chatcmpl-local-...",
  "object": "chat.completion",
  "created": 0,
  "model": "yolo11n-coco",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{\"task\":\"object_detection\",\"model\":\"yolo11n-coco\",\"mock\":true,\"detections\":[]}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": null
}
```

`usage` may be `null` because there is no token accounting.

## POST /v1/vision/detections

Purpose: native computer-vision endpoint.

Requires auth.

Supported request:

```json
{
  "image": {
    "url": "data:image/jpeg;base64,..."
  },
  "model": "yolo11n-coco",
  "include_normalized_boxes": true
}
```

Rules:

- `model` defaults to `yolo11n-coco` when omitted.
- Supplied `model` must match `yolo11n-coco`.
- `image.url` follows the same base64 JPEG/PNG data URL rules as `/v1/chat/completions`.
- Arbitrary external `http://` or `https://` image URLs are rejected in MVP.
- The endpoint calls the same configured detector backend as `/v1/chat/completions`.
- The response is the detection payload directly, not an OpenAI chat-completion envelope.

Successful response:

```json
{
  "task": "object_detection",
  "model": "yolo11n-coco",
  "source": {
    "kind": "image_url",
    "decoded": true,
    "mime_type": "image/jpeg",
    "width": 640,
    "height": 480
  },
  "detections": [
    {
      "class_id": 0,
      "class_name": "person",
      "confidence": 0.91,
      "box_xyxy": [102.4, 55.2, 310.1, 460.8],
      "box_xywh": [102.4, 55.2, 207.7, 405.6],
      "box_normalized_xyxy": [0.16, 0.12, 0.48, 0.96]
    }
  ],
  "mock": false
}
```

## Error shape

Use OpenAI-like errors.

Example:

```json
{
  "error": {
    "message": "Invalid API key.",
    "type": "authentication_error",
    "param": null,
    "code": "invalid_api_key"
  }
}
```

Common error codes:

| HTTP | Type | Code | Meaning |
|---:|---|---|---|
| 401 | authentication_error | missing_api_key | Missing Bearer token |
| 401 | authentication_error | invalid_api_key | Wrong Bearer token |
| 400 | invalid_request_error | unsupported_model | Model is not supported |
| 400 | invalid_request_error | missing_image | No image content part found |
| 400 | invalid_request_error | multiple_images_not_supported | More than one image provided when unsupported |
| 400 | invalid_request_error | streaming_not_supported | Streaming is not supported |
| 400 | invalid_request_error | external_image_url_not_supported | Non-data image URLs are not supported |
| 400 | invalid_request_error | invalid_image_data | Base64/image decoding failed |
| 400 | invalid_request_error | unsupported_image_mime | MIME type is not allowed |
| 413 | invalid_request_error | payload_too_large | Request or image too large |
| 413 | invalid_request_error | image_too_large | Decoded image dimensions are too large |
| 422 | invalid_request_error | invalid_schema | JSON does not match supported schema |
| 429 | rate_limit_error | service_busy | CPU worker busy or concurrency limit reached |
| 503 | server_error | detector_not_available | Detector backend is unavailable or missing dependencies |
| 500 | server_error | inference_failed | Unexpected inference failure |

## Contract stability

Breaking API changes require updating this file and a decision record.
