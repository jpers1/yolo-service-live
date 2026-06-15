# 0004 No database in v0

Status: accepted

## Context

The service has one static API key, no users, no billing, no persistent jobs, no request history requirement, and no image storage.

## Decision

Do not add a database in v0.

## Consequences

- Simpler architecture.
- Fewer deployment requirements.
- No migrations.
- No persistent state.
- If the process restarts, no application data should be lost because no application data is stored.

## May be revisited when

- users are added;
- per-user quotas are added;
- audit logs are required;
- saved jobs/results are required;
- admin UI is required.
