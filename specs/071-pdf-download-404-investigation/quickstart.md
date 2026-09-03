# Quickstart & Validation Guide: PDF Download Fix

## Overview
This guide provides the steps to validate that the PDF download functionality works locally after fixing the routing issues.

## Prerequisites
1. A local development environment set up with Reflex and PostgreSQL.
2. An active user session (login required) to pass the _s cookie.

## Validation Steps

1. **Start the application in dev mode**:
   `ash
   reflex run --env dev
   `
2. **Verify backend startup logs**:
   Ensure the following log appears without exceptions:
   `	ext
   [PDF-REGISTER] Rutas montadas exitosamente en /api/pdf usando .mount()
   `

3. **Navigate to the application**:
   Open a browser and log in at http://localhost:3000.

4. **Generate a PDF**:
   - Go to the **Contratos** module.
   - Select a contract (e.g., Contrato de Mandato).
   - Click the generate/download button.

5. **Verify the download**:
   - The browser should successfully download the PDF file instead of showing an alert with a 404 error.
   - Inspect the Network tab to confirm the request to http://localhost:8000/api/pdf/download/{filename} returns a 200 OK status.

6. **Verify CORS preflight (Local Dev)**:
   - Since the frontend runs on port 3000 and the backend on 8000 locally, a CORS preflight request (OPTIONS) will occur.
   - Ensure the preflight request succeeds and allows credentials.
