# Migración de SQLite a PostgreSQL
## Sistema de Gestión Inmobiliaria Velar SAS

---

## 📋 **Resumen de la Migración**

Este directorio contiene todos los scripts necesarios para migrar la base de datos completa de SQLite a PostgreSQL.

### **Configuración**
- **Base de datos**: `db_inmo_velar`
- **Usuario aplicación**: `inmo_user`
- **Contraseña**: `7323`
- **Host**: `localhost`
- **Puerto**: `5432`

### **Alcance de la Migración**
✅ 42 Tablas  
✅ 3 Vistas  
✅ 9 Triggers  
✅ 50 Índices  
✅ Todos los datos existentes  

---

## 🚀 **Pasos para la Migración**

### **Paso 1: Instalar dependencias de Python**

```bash
pip install psycopg2-binary
```

> **Nota**: Si ya tienes `psycopg2`, no necesitas `psycopg2-binary`

---

### **Paso 2: Verificar que PostgreSQL está en ejecución**

Asegúrate de que PostgreSQL 18 esté instalado y corriendo:

```bash
# En Windows, verifica el servicio:
# Ejecuta services.msc y busca "postgresql-x64-18"
# O desde PowerShell:
Get-Service -Name postgresql*
```

---

### **Paso 3: Ejecutar la extracción del esquema** (Ya completado)

Este paso ya fue ejecutado automáticamente:

```bash
python extract_schema.py
```

Esto genera: `schema_extracted.json` ✅

---

### **Paso 4: Ejecutar la migración completa**

**IMPORTANTE:** Aste script creará la basede datos desde cero.

```bash
python migrate_to_postgresql.py
```

Este script ejecutará las siguientes fases:

1. **Preparación de PostgreSQL**
   - Crear base de datos `db_inmo_velar`
   - Crear usuario `inmo_user`
   - Otorgar permisos

2. **Migración del Esquema**
   - Crear 42 tablas con tipos de datos adaptados
   - Convertir `INTEGER AUTOINCREMENT` → `SERIAL`
   - Convertir valores booleanos (0/1) → `BOOLEAN`
   - Adaptar DEFAULT values (datetime, date, etc.)

3. **Claves Foráneas**
   - Agregar todas las relaciones entre tablas

4. **Migración de Datos**
   - Transferir todos los registros
   - Convertir valores (booleanos, fechas, etc.)
   - Inserción en lotes para mejor rendimiento

5. **Secuencias**
   - Resetear secuencias al valor máximo actual

6. **Índices**
   - Crear 50 índices optimizados

7. **Triggers**
   - 9 triggers adaptados a sintaxis PostgreSQL (PL/pgSQL)
   - Auditoría, validaciones, automatizaciones

8. **Vistas**
   - 3 vistas para reportes

9. **Verificación**
   - Comparar conteo de registros SQLite vs PostgreSQL

---

### **Paso 5: Verificar la migración**

Después de ejecutar la migración:

```bash
python verify_connection.py
```

Este script verificará:
- ✅ Conexión exitosa
- ✅ Versión de PostgreSQL
- ✅ Tablas creadas
- ✅ Vistas creadas
- ✅ Triggers creados
- ✅ Conteo de registros

---

## ⚙️ **Configuración de la Aplicación Reflex**

### **Opción 1: URL de Conexión Simple**

```python
DATABASE_URL = "postgresql://inmo_user:7323@localhost:5432/db_inmo_velar"
```

### **Opción 2: Diccionario de Configuración**

```python
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'db_inmo_velar',
    'user': 'inmo_user',
    'password': '7323'
}
```

Ver `postgres_config.py` para más ejemplos detallados.

---

## 🔄 **Cambios Necesarios en el Código**

### **1. Importar psycopg2 en lugar de sqlite3**

**ANTES (SQLite):**
```python
import sqlite3
conn = sqlite3.connect('database.db')
```

**DESPUÉS (PostgreSQL):**
```python
import psycopg2
conn = psycopg2.connect(**POSTGRES_CONFIG)
```

---

### **2. Cambiar placeholders en queries**

**ANTES (SQLite usa `?`):**
```python
cursor.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,))
```

**DESPUÉS (PostgreSQL usa `%s`):**
```python
cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
```

---

### **3. Obtener ID después de INSERT**

**ANTES (SQLite):**
```python
cursor.execute("INSERT INTO tabla (nombre) VALUES (?)", (nombre,))
last_id = cursor.lastrowid
```

**DESPUÉS (PostgreSQL):**
```python
cursor.execute("INSERT INTO tabla (nombre) VALUES (%s) RETURNING id", (nombre,))
last_id = cursor.fetchone()[0]
```

---

### **4. Valores Booleanos**

PostgreSQL usa `TRUE`/`FALSE` nativos (no 0/1).

**Los datos ya están convertidos automáticamente en la migración.**

Si lees valores booleanos:
```python
# PostgreSQL devuelve True/False directamente
if usuario['estado_activo']:  # Ya es True/False, no 0/1
    print("Usuario activo")
```

---

### **5. Funciones de Fecha**

**ANTES (SQLite):**
```sql
datetime('now', 'localtime')
date('now')
```

**DESPUÉS (PostgreSQL):**
```sql
CURRENT_TIMESTAMP
CURRENT_DATE
```

---

## 📁 **Archivos Generados**

| Archivo | Descripción |
|---------|-------------|
| `extract_schema.py` | Extrae estructura completa de SQLite |
| `schema_extracted.json` | Esquema en formato JSON |
| `migrate_to_postgresql.py` | Script principal de migración |
| `verify_connection.py` | Verificación post-migración |
| `postgres_config.py` | Configuración y ejemplos |
| `README_MIGRACION.md` | Esta documentación |

---

## ⚠️ **Consideraciones Importantes**

### **Diferencias entre SQLite y PostgreSQL**

| Aspecto | SQLite | PostgreSQL |
|---------|--------|------------|
| **Tipado** | Dinámico | Estricto |
| **Autoincremento** | `AUTOINCREMENT` | `SERIAL` / `BIGSERIAL` |
| **Booleanos** | 0/1 (INTEGER) | `TRUE`/`FALSE` |
| **Placeholders** | `?` | `%s` |
| **Fechas** | `datetime('now')` | `CURRENT_TIMESTAMP` |
| **Case Sensitivity** | Insensible | Sensible (con comillas) |
| **Triggers** | SQL simple | PL/pgSQL (funciones) |

---

## 🐛 **Solución de Problemas**

### **Error: "No se puede conectar a PostgreSQL"**

1. Verifica que PostgreSQL esté corriendo:
   ```bash
   Get-Service -Name postgresql*
   ```

2. Verifica el puerto 5432:
   ```bash
   netstat -an | findstr 5432
   ```

3. Verifica las credenciales en `pgAdmin` o `psql`

---

### **Error: "Base de datos ya existe"**

El script `migrate_to_postgresql.py` eliminará y recreará la base de datos automáticamente.

Si prefieres hacerlo manualmente:
```sql
DROP DATABASE IF EXISTS db_inmo_velar;
CREATE DATABASE db_inmo_velar WITH ENCODING 'UTF8';
```

---

### **Error: "Conteo de registros no coincide"**

Ejecuta:
```bash
python verify_connection.py
```

Esto te mostrará qué tabla tiene discrepancias.

---

## 📊 **Verificación Manual con pgAdmin o psql**

### **Conectar con psql:**

```bash
psql -U inmo_user -d db_inmo_velar -h localhost
```

### **Comandos útiles:**

```sql
-- Listar tablas
\dt

-- Ver estructura de una tabla
\d USUARIOS

-- Contar registros
SELECT COUNT(*) FROM USUARIOS;

-- Ver vistas
\dv

-- Ver triggers
SELECT trigger_name, event_manipulation, event_object_table
FROM information_schema.triggers
WHERE trigger_schema = 'public';
```

---

## ✅ **Checklist de Verificación**

Después de la migración, verifica:

- [ ] Base de datos `db_inmo_velar` creada
- [ ] Usuario `inmo_user` creado con permisos
- [ ] 42 tablas creadas
- [ ] Datos migrados correctamente (conteo coincide)
- [ ] 50 índices creados
- [ ] 9 triggers funcionando
- [ ] 3 vistas creadas
- [ ] `verify_connection.py` ejecuta sin errores
- [ ] Aplicación puede conectarse a PostgreSQL

---

## 🔐 **Seguridad - Producción**

### **No uses contraseñas en texto plano en producción**

Usa variables de entorno:

1. Crea un archivo `.env`:
   ```env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=db_inmo_velar
   DB_USER=inmo_user
   DB_PASSWORD=7323
   ```

2. En tu código:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   
   POSTGRES_CONFIG = {
       'host': os.getenv('DB_HOST'),
       'port': int(os.getenv('DB_PORT')),
       'database': os.getenv('DB_NAME'),
       'user': os.getenv('DB_USER'),
       'password': os.getenv('DB_PASSWORD')
   }
   ```

3. Instala python-dotenv:
   ```bash
   pip install python-dotenv
   ```

---

## 📞 **Soporte**

Si encuentras problemas:

1. Revisa los logs de PostgreSQL
2. Ejecuta `verify_connection.py`
3. Consulta esta documentación
4. Revisa `postgres_config.py` para ejemplos

---

## ✨ **Ventajas de PostgreSQL sobre SQLite**

1. ✅ **Rendimiento**: Mejor para cargas concurrentes
2. ✅ **Escalabilidad**: Soporta millones de registros
3. ✅ **Integridad**: Mejor manejo de transacciones
4. ✅ **Tipos de datos**: Más tipos nativos (JSON, Arrays, etc.)
5. ✅ **Concurrencia**: Múltiples usuarios simultáneos
6. ✅ **Backup**: Herramientas robustas (`pg_dump`, `pg_restore`)
7. ✅ **Seguridad**: Control de acceso granular
8. ✅ **Producción**: Listo para entornos empresariales

---

**¡Migración completada! 🎉**
