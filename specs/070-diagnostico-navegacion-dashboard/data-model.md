# Data Model & State Architecture: Navigation Concurrency

This document outlines the state representation for the generation timestamp mechanism used to prevent race conditions during rapid navigation.

## State Modifications

### `NavigationGenerationMixin` (or `BaseState` extension)
This mixin provides the concurrency control foundation for all module states.

| Attribute/Property | Type | Description |
|--------------------|------|-------------|
| `current_generation` | `str` (UUID) or `float` (Timestamp) | The ID representing the latest valid page load attempt. |

### State Transition Lifecycle (The "Generation" Pattern)

1. **Trigger (`on_load`)**:
   - User navigates to `/personas`.
   - The synchronous `on_load` event handler fires.
   - The backend immediately generates a new `generation_id` (e.g., `time.time()`) and sets `self.current_generation = generation_id`.
   - Sets `self.is_loading = True`.
   - Returns the background event (`yield PersonasState.fetch_data(generation_id)`).

2. **Execution (`fetch_data` in background)**:
   - The background task receives the `generation_id` as an argument.
   - It performs the heavy I/O operations (fetching from DB).

3. **Resolution & Validation**:
   - Once I/O is complete, the background task compares the `generation_id` it was given against the live `self.current_generation`.
   - **Match**: The user is still on the page. The state is mutated with the new data, and `is_loading` is set to `False`.
   - **Mismatch**: The user navigated away rapidly (`< 500ms`). The background task silently discards the fetched data and returns without mutating the state.

4. **Failure (Graceful Rollback)**:
   - If an exception occurs during the background execution, the system catches it, redirects the user to the `/dashboard`, and emits an `rx.toast` warning.
