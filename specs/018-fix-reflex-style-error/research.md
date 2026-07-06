# Phase 0: Outline & Research

## Research: Floating Input Style Error

- **Decision**: Remove the duplicated `style` keyword argument in `rx.input` within `floating_label.py`.
- **Rationale**: Python keyword arguments must be unique. The component `floating_input` is likely spreading `**kwargs` which might already contain a `style` dictionary, or it passes `style` directly alongside a spread of `kwargs` that conflicts. Reflex `rx.input` inherits from `rx.Component`, and it does not allow multiple `style` definitions unless they are safely merged or deduplicated.
- **Alternatives considered**: Merging `kwargs.get('style', {})` with the custom `style` dict. This is a common pattern in Reflex to allow users to override styles, but depends on the exact implementation in `floating_label.py`. We will inspect the file during implementation to pick the best merging strategy.
