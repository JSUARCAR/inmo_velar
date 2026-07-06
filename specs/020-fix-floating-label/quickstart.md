# Quickstart & Validation: fix-floating-label

## Setup
No special data setup is required. The server must be running.

```bash
reflex run
```

## Validation Steps

1. Open the application in the browser.
2. Navigate to a page with advanced date filters, such as `/recaudos` or `/liquidaciones`.
3. Locate the `Fecha Desde` and `Fecha Hasta` inputs.
4. **Initial State Check**: Without clicking or typing anything, verify that the labels ("Fecha Desde", "Fecha Hasta") are floating ABOVE the input boundary, leaving the native browser placeholder (e.g. `dd/mm/aaaa`) fully visible and legible.
5. **Interaction Check**: Click on the date picker. The label should remain floating at the top.
6. **Value Check**: Select a date. The label must remain at the top.
7. **Clear Check**: Clear the date input. The label must remain at the top to avoid overlapping with the placeholder again.

**Expected Outcome**: Zero text overlapping at any state.
