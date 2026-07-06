# Feature Specification: fix-floating-label

**Feature Branch**: `[###-fix-floating-label]`

**Created**: 2026-07-05

**Status**: Draft

**Input**: User description: "valida la implementación del floating ya que hay algunos elementos que no lo implementa de manera correcta, como se identifica en la imagen"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Correct Floating Label on Date Pickers (Priority: P1)

Users should see the input label (e.g., "Fecha Desde", "Fecha Hasta") cleanly float above the input field when the field has a placeholder like "dd/mm/aaaa" or when a date is selected, preventing any text overlap that makes the UI look messy and unreadable.

**Why this priority**: Overlapping text significantly degrades the user experience and the visual quality of the application. Fixing this is a high priority UI bug.

**Independent Test**: Can be fully tested by opening the UI with date pickers (e.g., advanced filters in Liquidacion/Recaudos), observing the initial state with placeholders, and interacting with the input.

**Acceptance Scenarios**:

1. **Given** a date picker input with a placeholder (e.g., "dd/mm/aaaa"), **When** the input is rendered on the screen initially (empty state), **Then** the label should float correctly above the placeholder without overlapping.
2. **Given** a date picker input, **When** the user clicks on it to select a date, **Then** the label remains cleanly floating above the input area.
3. **Given** a date picker input with a selected date, **When** the date is displayed, **Then** the label remains cleanly floating above the selected value.

---

### Edge Cases

- What happens when a date is cleared? The label should still float correctly if the placeholder is visible, or return to the base position if there's no placeholder (standard floating behavior).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Date picker inputs (or any input with placeholders) MUST correctly implement the floating label CSS logic so that the label is always in the floating state if a placeholder is present.
- **FR-002**: The fix MUST apply consistently across all instances where this specific UI component is used (e.g., `Fecha Desde`, `Fecha Hasta` filters).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero text overlap between floating labels and placeholders/values in date pickers.
- **SC-002**: Visual validation passes the "Clean Console and UI" check without overlapping text.

## Assumptions

- The issue is primarily CSS/styling related to how the floating label interacts with the `placeholder-shown` pseudo-class or Reflex's internal state for date pickers.
- The base floating label component structure remains the same, only the CSS logic or state management for the floating condition needs adjustment.
