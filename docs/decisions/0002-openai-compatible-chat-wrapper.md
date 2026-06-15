# 0002 Expose YOLO through an OpenAI-compatible chat wrapper

Status: accepted

## Context

The product should allow users to reuse an OpenAI-style client configuration with a local `base_url` and API key.

OpenAI chat-completions requests can include image content parts using `image_url`.

## Decision

Implement:

```text
POST /v1/chat/completions
```

as the OpenAI-compatible API surface for image detection.

The endpoint accepts an image in a chat-style request and returns an OpenAI-shaped chat-completion response. The assistant message content is JSON containing YOLO detections.

## Consequences

- Existing OpenAI client examples become easier to adapt.
- The service must document that compatibility is limited.
- The service must not pretend to be a general LLM chatbot.
- The native CV endpoint is still needed for clean non-chat usage.

## May be revisited when

- OpenAI compatibility becomes less important than pure CV API clarity.
- The newer Responses API becomes a better compatibility target.
- A client requires a different compatibility envelope.
