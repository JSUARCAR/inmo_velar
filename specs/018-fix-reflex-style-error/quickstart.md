# Quickstart Validation Guide

## Prerequisites
- Python 3.11+
- Virtual environment activated with project dependencies installed.

## Setup
No special setup required beyond the standard project environment.

## Validation Steps

1. Start the Reflex development server:
   ```bash
   reflex run
   ```
2. Verify that the server compiles the application successfully without throwing `TypeError: TextField() got multiple values for keyword argument 'style'`.
3. Open the browser and navigate to `http://localhost:3000/contratos`.
4. Verify the page loads successfully and the floating inputs render correctly without server 500 errors.

## Expected Outcomes
- The terminal output shows successful compilation.
- The `contratos` page is fully functional.
