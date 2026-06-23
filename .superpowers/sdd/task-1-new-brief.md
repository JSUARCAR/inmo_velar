# Task 1: Instalar dependencias faltantes y fijar requirements.txt

## Ubicación en el Plan
Task 1 del Plan Maestro de Estabilización. Es la primera tarea, sin dependencias de otras tareas.
Base commit del plan: ec14ba4

## Objetivo
Los paquetes `holidays` y `python-barcode` no están instalados en el venv del proyecto, causando ~8 fallos en:
- `tests/test_calculadora_contratos.py` — ModuleNotFoundError: No module named 'holidays'
- `tests/pdf_elite/test_components.py` — ModuleNotFoundError: No module named 'barcode'

## Global Constraints
- Rama activa: `feat/desarrollo-experto-elite`
- Directorio de trabajo: `C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX`
- Venv: `venv\Scripts\activate`
- Commits en español con Conventional Commits
- Ruff + Black limpios antes de cada commit

## Pasos

### Step 1: Verificar estado actual de requirements.txt
```powershell
Select-String "holidays|barcode|python-barcode" requirements.txt
```

### Step 2: Instalar dependencias en el venv activo
```powershell
venv\Scripts\activate
pip install holidays python-barcode
```

### Step 3: Actualizar requirements.txt
Añadir (si no existen) al final del archivo:
```
holidays>=0.46
python-barcode>=0.15.1
```

### Step 4: Verificar que los tests afectados pasan
```powershell
venv\Scripts\activate
pytest tests/test_calculadora_contratos.py tests/pdf_elite/test_components.py -q
```
Resultado esperado: todos los tests de calculadora pasan (6+). Los de barcode pasan.

### Step 5: Commit
```bash
git add requirements.txt
git commit -m "chore(deps): agrega holidays y python-barcode faltantes en requirements"
```

## Criterio de Aceptación
- `pytest tests/test_calculadora_contratos.py tests/pdf_elite/test_components.py -q` → 0 failed
- `requirements.txt` contiene `holidays` y `python-barcode`
- Ruff y Black limpios
