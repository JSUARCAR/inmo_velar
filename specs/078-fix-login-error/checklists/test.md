# Test & Validation Requirements Quality Checklist: Corrección del error de producción tras el inicio de sesión (TypeError en protección de rutas)

**Purpose**: Validate the quality, clarity, completeness and coverage of the TEST, REGRESSION and VALIDATION requirements written in spec.md (FR-008, FR-009, SC-001..SC-006, Edge Cases) plus their consistency with the design artifacts (plan.md, research.md, contracts/proteccion_rutas.md)
**Created**: 2026-09-23
**Feature**: [spec.md](../spec.md)

---

## Requirement Completeness

- [x] CHK001 - Are requirements defined that prescribe updating the pre-existing tests that codified the erroneous signature (`test_proteccion_rutas.py` asserts `end_navigation_generation("test-gen-N")`; `test_auth_login.py` mocks the method), so the suite does not re-encode the bug? [Gap, Spec §FR-008, research §Hallazgo 2]
- [x] CHK002 - Are requirements defined for the dedicated regression test (FR-008) to exercise the REAL `end_navigation_generation` method (no mocking), precluding false-green suites that accept any signature? [Clarity, Spec §FR-008, research §Hallazgo 2]
- [x] CHK003 - Does the spec require the regression test to fail with the bug present (RED) before the fix, per constitution §13 (Corregir Raíz → Blindar) and TDD? [Gap, Spec §FR-008, constitution §13]
- [x] CHK004 - Are requirements defined that cover BOTH terminal paths of `require_login_background` (acceso permitido y acceso denegado) with observable log evidence (FR-009), not only the success path? [Completeness, Spec §FR-009]
- [x] CHK005 - Are validation requirements defined that span screen-observable outcomes (SC-001/SC-003) AND log-observable outcomes (SC-002/SC-006) without leaving any of SC-001..SC-006 without an evidence path? [Completeness, Spec §SC-001..§SC-006]

## Requirement Clarity

- [x] CHK006 - Is the START of the SC-002 validation window unambiguous: "tras el despliegue" means deploy completion, or first login in production? [Ambiguity, Spec §SC-002]
- [x] CHK007 - Is "matriz de regresión de autenticación" (SC-004) unambiguous: does it equal the 077 ten-point matrix or the six behaviors enumerated in the spec, and is their reconciliation documented? [Ambiguity, Spec §SC-004, 077 quickstart]
- [x] CHK008 - Is "se invoca sin argumento" (FR-008/FR-001) specified at assertion level, so the objective check is unambiguous (a call with an argument raises `TypeError`)? [Clarity, Spec §FR-001, §FR-008]
- [x] CHK009 - Is "guardia permanente" (SC-006) defined regarding WHERE it lives (unit/integration/E2E) and HOW it runs in the suite, or is that left unresolved? [Clarity, Spec §SC-006]

## Requirement Consistency

- [x] CHK010 - Are FR-008 (dedicated real-mixin test) and the existing mocked test suite consistent — is the mock-strategy change (un-mocking `end_navigation_generation`) made explicit in the requirements? [Conflict, Spec §FR-008, tests existinges]
- [x] CHK011 - Is FR-009 (desenlace log) consistent with the Zero Leak protocol (constitution §4) — does the requirement-level text forbid credentials/token/user data as strongly as the contract does? [Consistency, Spec §FR-009, contract §3]
- [x] CHK012 - Are SC-003 (inventory in the validation plan) and FR-003 (objective criterion) consistent about how the 18-route inventory is fixed and maintained when pages are added? [Consistency, Spec §FR-003, §SC-003, contract §4]
- [x] CHK013 - Are the blocking deployed validation (Assumptions) and the log-based evidence (FR-009/SC-002) consistent with SC-001's screen-observable outcome — which artifact proves "0 % pantallas de error" in production? [Consistency, Spec §Assumptions, §SC-001]
- [x] CHK014 - Is the idempotency edge case (Clarification Q3: no guard condition, no double-invocation scenario) consistent with FR-008's defined scope, so no implementer adds a contradictory scenario? [Consistency, Spec §Edge Cases 5, Clarification Q3]

## Acceptance Criteria Quality

- [x] CHK015 - Are all six success criteria quantified with specific metrics and free of implementation details, and are they measurable solely from observable evidence (logs/screen) as the domain requires? [Measurability, Spec §SC-001..§SC-006]
- [x] CHK016 - Can "sin spinner atascado" (SC-005) be objectively measured — is the indicator (`is_loading == False`) specified at requirement level across the verification matrix? [Measurability, Spec §SC-005]
- [x] CHK017 - Is the acceptance criterion defined such that FR-008's test gates feature closure (SC-006 as permanent guard in every suite run), not a one-off validation? [Acceptance Criteria, Spec §SC-006]

## Scenario Coverage

- [x] CHK018 - Are requirements/criteria defined to cover the stale-generation path (navigate away while background task pending) within the regression test scope? [Coverage, Spec §Edge Cases 1]
- [x] CHK019 - Are requirements/criteria defined for the transient DB-error validation path (must NOT invalidate session nor throw) as a covered test scenario? [Coverage, Spec §Edge Cases 3]
- [x] CHK020 - Are requirements defined to cover page reload on a protected route (Edge Case §4) within SC-003 verification? [Coverage, Spec §Edge Cases 4]
- [x] CHK021 - Are negative-verification requirements defined — an explicit procedure to actively search the production logs for re-occurrence of the `TypeError` (SC-002), rather than relying only on visual absence? [Gap, Spec §SC-002, §FR-009]

## Edge Case Coverage

- [x] CHK022 - Is the boundary between the unit regression test (FR-008) and the E2E matrix (SC-003/SC-004) defined in requirements, avoiding overlap or omission of responsibility? [Gap, Spec §SC-003, §SC-004]
- [x] CHK023 - Are requirements defined for the "invalid session + valid generation" path (Edge Case §2) to be exercised by the regression suite (redirect without exception)? [Coverage, Spec §Edge Cases 2]
- [x] CHK024 - Is the exclusion of the double-invocation test scope explicit, so the test suite (FR-008 + existing) does not silently contradict the idempotency decision? [Clarity, Spec §Edge Cases 5, Clarification Q3]

## Non-Functional Requirements

- [x] CHK025 - Is the dependency on the E2E/Playwright infrastructure (reused from 077, currently not runnable — T042 open) documented in the requirements as a prerequisite/risk for SC-003/SC-004, or is it an untracked assumption? [Dependency, Spec §Assumptions]
- [x] CHK026 - Are the 077 timing/performance limits (5/10 s) explicitly excluded from this feature's validation scope, preventing acceptance tests from validating out-of-scope performance? [Completeness, Spec §Assumptions]
- [x] CHK027 - Is the security requirement for the desenlace log specified at requirements level with forbidden fields (credentials, token, user data, cookies), not only in the contract? [Gap, Spec §FR-009, contract §3]

## Dependencies & Assumptions

- [x] CHK028 - Is the dependency on the 077 ten-point matrix reconciled with SC-004 (which lists six behaviors) — which artifact governs the regression validation gate? [Dependency, Spec §SC-004, 077 quickstart]
- [x] CHK029 - Is the blocking deployed validation tied to concrete evidence artifacts (Railway logs, FR-009 desenlace lines) and is that evidence dependency documented as required to close the feature? [Assumption, Spec §Assumptions, Clarification Q4]

## Ambiguities & Conflicts

- [x] CHK030 - Does the spec leave ambiguity about whether FR-008's dedicated test is unit (sin I/O) or E2E — is the test type stated as a requirement or decided only in plan.md? [Ambiguity, Spec §FR-008, plan §Project Structure]
- [x] CHK031 - Is there a conflict between SC-001 (screen-observable, "0 % pantallas de error") and the deployed evidence being log-based (FR-009) — is it specified which evidence satisfies each criterion? [Conflict, Spec §SC-001, §FR-009]
- [x] CHK032 - Is an explicit FR → SC → evidence-artifact mapping established in the requirements (traceability), or does the spec lack an ID/trace scheme that gates acceptance? [Traceability, Spec §FR-001..§FR-009, §SC-001..§SC-006]

## Notes

- Items marked `[Gap]` indicate requirement aspects that may need to be added or clarified in spec.md before `/speckit-tasks`
- De los 32 ítems, 24 referencian una sección del spec y 8 referencian marcadores de brecha/ambigüedad/conflicto/dependencia: cobertura de trazabilidad > 80 %
- Este checklist prueba la CALIDAD de los requisitos de test/validación/observabilidad, no la implementación; los hallazgos de `research.md` (Hallazgos 2-4) y `contracts/proteccion_rutas.md` (§3 log, §4 inventario) son las fuentes de verificación de los ítems con [Gap]/[Clarity]