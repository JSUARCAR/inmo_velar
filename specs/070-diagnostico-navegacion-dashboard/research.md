# Research: Concurrency & Infrastructure for Background Navigation Fix

## Background Event Infrastructure
- **Decision**: Native `asyncio` for Reflex background tasks.
- **Rationale**: Reflex defaults to standard python `asyncio` in local and standard single-worker deployments. Given the current scope on Railway and to minimize provisioning complexity, relying on `asyncio` avoids the overhead of managing a Redis instance for the MVP.
- **Alternatives considered**: Provisioning a Redis broker (rejected temporarily due to over-engineering for the current phase).

## UI Loading Feedback
- **Decision**: Use Radix `rx.spinner()` component.
- **Rationale**: Simple, native to Reflex, highly recognizable, and avoids the CSS complexity of animating full page `Skeleton` components. Ensures instant visual response (<500ms).
- **Alternatives considered**: Custom CSS Skeleton matching Claude Design System (rejected to prioritize stability and speed).

## Concurrency Control (Generation ID)
- **Decision**: Server-side timestamp ID generation.
- **Rationale**: State is heavily centralized in the Reflex backend. Generating the timestamp when the `on_load` triggers prevents clock synchronization issues between frontend clients and backend servers.
- **Alternatives considered**: Client-side timestamp injection via JS events (rejected due to complexity mapping to `on_load` triggers).

## Error Handling / Timeout
- **Decision**: Graceful Rollback to Dashboard.
- **Rationale**: If a background event fails or times out, mutating the state to a broken view is dangerous. Rolling back to the secure root (Dashboard) and showing a warning `toast` preserves user trust and application stability.
- **Alternatives considered**: Persistent error `callout` on the destination page (rejected as it strands the user in a broken view).
