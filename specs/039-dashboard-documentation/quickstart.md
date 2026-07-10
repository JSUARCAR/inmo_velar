# Quickstart: Dashboard Documentation Validation

**Feature**: 039-dashboard-documentation  
**Date**: 2026-07-08  
**Status**: Complete

## Overview

Guía rápida para validar que la documentación del Dashboard está completa y funciona correctamente con MkDocs.

## Prerequisites

### Required Software
- Python 3.8+
- pip (Python package manager)
- MkDocs
- Material for MkDocs theme

### Installation

```bash
# Instalar MkDocs y Material theme
pip install mkdocs-material

# O usar requirements.txt si existe
pip install -r requirements.txt
```

### Environment Setup

```bash
# Navegar al directorio raíz del proyecto
cd /path/to/inmobiliaria-velar/PYTHON-REFLEX

# Verificar que MkDocs está instalado
mkdocs --version
```

## Validation Scenarios

### Scenario 1: Documentation Structure Validation

**Objective**: Verify that the documentation file has the correct structure and all required sections.

**Steps**:

1. **Check file existence**:
   ```bash
   ls -la docs/manual-usuario/modulos/dashboard.md
   ```

2. **Verify section count** (should be 15 sections):
   ```bash
   grep -c "^## " docs/manual-usuario/modulos/dashboard.md
   ```

3. **Verify required sections exist**:
   ```bash
   grep -E "^## (1\.|2\.|3\.|4\.|5\.|6\.|7\.|8\.|9\.|10\.|11\.|12\.|13\.|14\.|15\.)" docs/manual-usuario/modulos/dashboard.md
   ```

**Expected Outcome**: All 15 sections present and correctly numbered.

**Pass Criteria**: 15/15 sections found.

---

### Scenario 2: MkDocs Build Validation

**Objective**: Verify that the documentation builds successfully with MkDocs.

**Steps**:

1. **Run MkDocs build in strict mode**:
   ```bash
   mkdocs build --strict
   ```

2. **Check for errors**:
   ```bash
   # Should output no errors
   echo $?
   ```

3. **Verify output directory**:
   ```bash
   ls -la site/
   ```

**Expected Outcome**: Build completes without errors, `site/` directory created.

**Pass Criteria**: Exit code 0, no warnings in output.

---

### Scenario 3: Screenshot References Validation

**Objective**: Verify that all screenshot references in the documentation are valid.

**Steps**:

1. **Count image references**:
   ```bash
   grep -c "!\[.*\](.*\.png)" docs/manual-usuario/modulos/dashboard.md
   ```

2. **Verify screenshot directory exists**:
   ```bash
   ls -la docs/assets/screenshots/Dashboard/
   ```

3. **Check that referenced images exist** (manual verification):
   - Open `dashboard.md`
   - Verify each image path points to an existing file

**Expected Outcome**: All image references are valid and images exist.

**Pass Criteria**: All 12 screenshots referenced and available.

---

### Scenario 4: Content Completeness Validation

**Objective**: Verify that all functional requirements are documented.

**Steps**:

1. **Check Introduction section**:
   ```bash
   grep -A 5 "### Objetivo" docs/manual-usuario/modulos/dashboard.md
   ```

2. **Check Access section**:
   ```bash
   grep -A 10 "## 3. Acceso" docs/manual-usuario/modulos/dashboard.md
   ```

3. **Check Functionalities section**:
   ```bash
   grep -c "^### 5\." docs/manual-usuario/modulos/dashboard.md
   ```

4. **Check FAQ section**:
   ```bash
   grep -c "<summary>" docs/manual-usuario/modulos/dashboard.md
   ```

5. **Check Troubleshooting table**:
   ```bash
   grep -A 20 "## 12. Solución de Problemas" docs/manual-usuario/modulos/dashboard.md
   ```

**Expected Outcome**: All major sections contain substantial content.

**Pass Criteria**: No empty sections, all subsections have content.

---

### Scenario 5: MkDocs Serve Validation

**Objective**: Verify that the documentation renders correctly in a browser.

**Steps**:

1. **Start MkDocs development server**:
   ```bash
   mkdocs serve
   ```

2. **Open browser**:
   ```
   http://127.0.0.1:8000
   ```

3. **Navigate to Dashboard documentation**:
   - Click on "Manual de Usuario" in sidebar
   - Click on "Dashboard" module

4. **Verify rendering**:
   - [ ] Headings display correctly
   - [ ] Tables render properly
   - [ ] Admonitions (NOTA, IMPORTANTE, etc.) display with icons
   - [ ] Images load correctly
   - [ ] Code blocks have syntax highlighting
   - [ ] Links are clickable

**Expected Outcome**: Documentation renders correctly with all visual elements.

**Pass Criteria**: All visual elements display correctly.

---

### Scenario 6: Spanish Language Validation

**Objective**: Verify that the documentation is written in professional Spanish.

**Steps**:

1. **Check for English words** (should be minimal):
   ```bash
   grep -iE "\b(the|and|or|but|in|on|at|to|for|of|with|is|are|was|were)\b" docs/manual-usuario/modulos/dashboard.md | head -20
   ```

2. **Verify Spanish-specific characters**:
   ```bash
   grep -E "[áéíóúñ¿¡]" docs/manual-usuario/modulos/dashboard.md | head -10
   ```

3. **Check admonition titles are in Spanish**:
   ```bash
   grep "> \[!NOTE\]" docs/manual-usuario/modulos/dashboard.md
   ```

**Expected Outcome**: Documentation is predominantly in Spanish.

**Pass Criteria**: Less than 5% English words, Spanish admonition titles.

---

## Validation Commands Summary

```bash
# Quick validation suite
cd /path/to/project

# 1. Check file exists
test -f docs/manual-usuario/modulos/dashboard.md && echo "✅ File exists" || echo "❌ File missing"

# 2. Count sections
SECTIONS=$(grep -c "^## " docs/manual-usuario/modulos/dashboard.md)
echo "Sections found: $SECTIONS/15"

# 3. Count screenshots
SCREENSHOTS=$(grep -c "!\[.*\](.*\.png)" docs/manual-usuario/modulos/dashboard.md)
echo "Screenshots referenced: $SCREENSHOTS/12"

# 4. Build validation
mkdocs build --strict 2>&1 | tee build.log
if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed - check build.log"
fi

# 5. Start serve for manual verification
mkdocs serve
```

## Expected Outcomes

### All Scenarios Pass
- ✅ Documentation file exists and has 15 sections
- ✅ MkDocs builds without errors
- ✅ All 12 screenshots are referenced
- ✅ All functional requirements are documented
- ✅ Documentation renders correctly
- ✅ Content is in professional Spanish

### Some Scenarios Fail
- ❌ Document missing sections → Add missing sections
- ❌ MkDocs build fails → Fix formatting errors
- ❌ Screenshots missing → Capture and add screenshots
- ❌ Content incomplete → Add missing content
- ❌ Rendering issues → Fix Markdown formatting
- ❌ English content → Translate to Spanish

## Troubleshooting

### Build Errors

**Error**: `WARNING: Documentation file 'dashboard.md' contains an unrecognized attribute`

**Solution**: Check admonition syntax. Use `> [!NOTE]` format.

### Image Not Found

**Error**: `WARNING: Documentation file 'dashboard.md' references image 'filename.png' which does not exist`

**Solution**: Verify image path and filename. Check case sensitivity.

### Table Formatting

**Error**: Table not rendering correctly

**Solution**: Ensure proper Markdown table syntax with header separator.

## Next Steps

After successful validation:
1. Review content with stakeholders
2. Add any missing screenshots
3. Update documentation based on feedback
4. Publish to production documentation site