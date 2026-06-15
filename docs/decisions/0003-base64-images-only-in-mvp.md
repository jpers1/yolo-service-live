# 0003 Accept base64 image data URLs only in MVP

Status: accepted

## Context

OpenAI-style image content can reference either image URLs or base64 image data. Fetching arbitrary external URLs from the backend creates SSRF and network trust risks.

## Decision

For MVP, support only:

```text
data:image/jpeg;base64,...
data:image/png;base64,...
```

Reject:

```text
http://...
https://...
file://...
local paths
```

## Consequences

- Simpler and safer MVP.
- Browser demo can send camera frames as JPEG data URLs.
- Users cannot submit arbitrary remote image URLs in MVP.
- Documentation must clearly state this limitation.

## May be revisited when

External URL fetching is explicitly required and a hardened fetch policy is designed, including:

- DNS/IP filtering;
- timeout;
- max download bytes;
- content-type validation;
- redirect limits;
- private-network blocking;
- tests.
