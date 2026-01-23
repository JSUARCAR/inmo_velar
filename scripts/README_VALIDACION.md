# Scripts de Validación - Fase 2

Scripts para validar la fundación del sistema antes de continuar con desarrollo.

## 🚀 Orden de Ejecución

### 1. Ejecutar Triggers de Auditoría
```bash
python scripts/01_ejecutar_triggers.py
```

**Qué hace:**
- Crea la tabla `AUDITORIA_CAMBIOS` si no existe
- Instala 8 triggers (INSERT/UPDATE) en tablas principales
- Valida que los triggers se crearon correctamente

---

### 2. Poblar Datos de Prueba
```bash
python scripts/02_poblar_datos_prueba.py
```

**Qué hace:**
- Crea usuario `admin` / contraseña `admin123`
- Crea 4 municipios principales (Bogotá, Medellín, Cali, Barranquilla)
- Crea IPCs de 2023 y 2024
- Crea 3 personas de ejemplo

---

### 3. Validar Repositorios
```bash
python scripts/03_validar_repositorios.py
```

**Qué hace:**
- Ejecuta pruebas CRUD en repositorios principales
- Valida que la auditoría está registrando cambios
- Genera reporte de validación (✅/❌)

---

## ✅ Resultado Esperado

Si todo funciona correctamente, verás:
```
========================================================
✅ VALIDACIÓN EXITOSA - TODO FUNCIONA CORRECTAMENTE
========================================================
```

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError"
- Verifica que estés en el directorio raíz del proyecto
- Ejecuta: `pip install -r requirements.txt`

### Error: "Database is locked"
- Cierra cualquier conexión abierta a `DB_Inmo_Velar.db`
- Verifica que no haya otro proceso usando la BD

### Error: "Table already exists"
- Normal si ejecutas los scripts múltiples veces
- Los scripts detectan duplicados y los omiten

---

## 📊 Próximos Pasos

Una vez completada la validación:
- **Opción 2**: Implementar vistas Flet (UI)
- **Opción 3**: Crear suite de tests automatizados
