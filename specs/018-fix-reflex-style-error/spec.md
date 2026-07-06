# Feature Specification: Fix Reflex Style Error in Floating Input

**Feature Branch**: `018-fix-reflex-style-error`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "valida el siguiente error que se registra en la terminal: ... TypeError: TextField() got multiple values for keyword argument 'style' Happened while evaluating page 'contratos'"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Contratos Page Without Crash (Priority: P1)

As a system user, I want to navigate to the Contratos page so that I can interact with the floating inputs without the server crashing during compilation.

**Why this priority**: Resolving a compilation crash is critical for the application to function.

**Independent Test**: Can be fully tested by running `reflex run` and navigating to the `/contratos` route without encountering the `TypeError` and compilation halt.

**Acceptance Scenarios**:

1. **Given** the Reflex server is starting, **When** it compiles the `contratos` page, **Then** it must compile successfully without throwing `TypeError: TextField() got multiple values for keyword argument 'style'`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST successfully evaluate and compile the `contratos` page.
- **FR-002**: The `floating_input` component in `src/presentacion_reflex/components/shared/floating_label.py` MUST NOT pass the `style` argument multiple times to `rx.input`.
- **FR-003**: The `neuro_floating_input` component in `src/presentacion_reflex/components/neuro_elements.py` MUST work seamlessly with `floating_input`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The application successfully compiles and starts without any backend Python tracebacks related to `TextField`.
- **SC-002**: Users can access the `/contratos` view in the browser without 500 internal server errors.

## Assumptions

- The issue is caused by passing `style` as an explicit keyword argument alongside `**kwargs` that also might contain style information, or due to a change in Reflex's internal handling of style kwargs.
- Fixing this component will solve the compilation issue for the `contratos` page and any other page using `floating_input`.
