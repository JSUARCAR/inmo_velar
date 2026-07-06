# Tasks: fix-floating-label

**Input**: Design documents from `/specs/020-fix-floating-label/`

**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

*(No setup tasks required for this UI fix)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

*(No foundational tasks required for this UI fix)*

---

## Phase 3: User Story 1 - Correct Floating Label on Date Pickers (Priority: P1) 🎯 MVP

**Goal**: Users should see the input label (e.g., "Fecha Desde", "Fecha Hasta") cleanly float above the input field when the field has a placeholder like "dd/mm/aaaa" or when a date is selected.

**Independent Test**: Can be fully tested by opening the UI with date pickers (e.g., advanced filters in Liquidacion/Recaudos), observing the initial state with placeholders, and interacting with the input.

### Implementation for User Story 1

- [x] T001 [US1] Update `floating_input` function in `src/presentacion_reflex/components/shared/floating_label.py` to accept an `always_float` boolean argument (default `False`), and modify the state-driven style logic (`rx.cond`) to use `label_with_value_style` if `always_float` is true or if `has_value` is true.
- [x] T002 [US1] Update `floating_input` function in `src/presentacion_reflex/components/shared/floating_label.py` to auto-detect if the `type` kwarg is date-related (e.g., `date`, `month`, `time`) and set `always_float = True` internally if so, so existing usages in forms automatically get fixed.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T003 Run `quickstart.md` validation to ensure there is zero overlapping text on date pickers across the UI (e.g., Recaudos filters).

---

## Dependencies & Execution Order

### Phase Dependencies

- **User Story 1 (Phase 3)**: No dependencies - can start immediately

### Within Each User Story

- T001 and T002 should be implemented sequentially as they modify the same file and function.

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: User Story 1 (T001, T002).
2. Complete Polish phase (T003).
3. **STOP and VALIDATE**: Test User Story 1 independently.

---
