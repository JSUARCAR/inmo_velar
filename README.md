# Sistema de Gestión Inmobiliaria

Sistema web moderno para gestión inmobiliaria construido con Clean Architecture y principios SOLID.

## 🏗️ Arquitectura

El proyecto sigue **Clean Architecture** con clara separación de responsabilidades:

```
src/
├── dominio/           # Lógica de negocio pura (0 dependencias externas)
├── aplicacion/        # Casos de uso (depende solo de dominio)
├── infraestructura/   # Detalles técnicos (BD, config, logs)
└── presentacion/      # Interfaz de usuario (Flet)
```

## ✨ Características Implementadas

### Capa de Dominio
- ✅ **Entidades**: Persona (Party Model base)
- ✅ **Value Objects**: Dinero, DocumentoIdentidad, Direccion, Email, Telefono
- ✅ **Interfaces (Protocols)**: IRepositorio, IRepositorioPersona
- ✅ **Estrategias**: Cálculo de comisiones extensible
- ✅ **Constantes**: Tipos de documento, estados, roles
- ✅ **Excepciones**: Jerarquía personalizada de errores de dominio

### Capa de Infraestructura
- ✅ **Base de Datos**: Gestor SQLite con patrón Singleton thread-safe
- ✅ **Repositorios**: RepositorioPersonaSQLite con mapeo completo
- ✅ **Configuración**: Pydantic Settings con variables de entorno

## 📁 Estructura del Proyecto

```
PYTHON-FLET/
│
├── DB_Inmo_Velar.db          # 🗄️ Base de datos SQLite (ubicación principal)
├── main.py                    # 🚀 Entry point de la aplicación
├── requirements.txt           # 📦 Dependencias del proyecto
├── pyproject.toml            # ⚙️ Configuración Python
├── .env.example              # 🔧 Variables de entorno (plantilla)
├── .gitignore                # 🚫 Exclusiones de Git
│
└── src/
    ├── dominio/              # 🎯 Lógica de negocio pura
    ├── aplicacion/           # 📋 Casos de uso
    ├── infraestructura/      # 🔌 Detalles técnicos (BD, config)
    ├── presentacion/         # 🖥️ Interfaz Flet
    └── core/                 # 🛠️ Utilidades compartidas
```

## 🚀 Instalación

### Requisitos Previos

- Python 3.10 o superior
- Base de datos SQLite (incluida en el proyecto: `DB_Inmo_Velar.db`)

### Pasos de Instalación

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno (Windows)
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
copy .env.example .env
```

### Estructura de Base de Datos

El proyecto utiliza **SQLite** para persistencia de datos:

- **Archivo**: `DB_Inmo_Velar.db` (ubicado en la raíz del proyecto)
- **Esquema**: Incluye tablas para PERSONAS, USUARIOS, PROPIEDADES, CONTRATOS, LIQUIDACIONES, PAGOS, AUDITORIA
- **Configuración**: La ruta se define en el archivo `.env` con la variable `DATABASE_PATH`

> **Nota**: El archivo `DB_Inmo_Velar.db` ya contiene el esquema completo. No es necesario ejecutar migraciones iniciales.

## 📝 Uso

### 🌐 Modo Web (Recomendado)

La aplicación se ejecuta en tu navegador web localmente:

```bash
# Opción 1: Usar script dedicado
python run_web.py

# Opción 2: Ejecutar main.py directamente (configurado para web por defecto)
python main.py
```

**Características del modo web:**
- ✅ Se abre automáticamente en tu navegador predeterminado
- ✅ Accesible en: `http://localhost:8080`
- ✅ Interfaz responsive y moderna
- ✅ Accesible desde otros dispositivos en la red local (opcional)
- ✅ Presiona `Ctrl+C` en la terminal para detener el servidor

### 🖥️ Modo Escritorio (Alternativo)

Para ejecutar como aplicación de escritorio nativa:

```python
# Modificar main.py línea 2210:
# Cambiar de:
ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8080)

# A:
ft.app(target=main)
```

**Al ejecutar por primera vez**:
- El sistema verificará la existencia de `DB_Inmo_Velar.db`
- Si todo está correcto, se abrirá el navegador (modo web) o ventana nativa (modo escritorio)
- La aplicación mostrará la pantalla de login

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=src --cov-report=html
```

## 📋 Próximos Pasos

1. **Capa de Aplicación**: Implementar DTOs, Mappers y Servicios
2. **Capa de Presentación**: Crear vistas Flet (Login, Dashboard, CRUD)
3. **Testing**: Tests unitarios del dominio
4. **Documentación**: Diagramas y manual de usuario

## 🏛️ Principios SOLID Aplicados

- **SRP**: Cada clase tiene una sola responsabilidad
- **OCP**: Extensible mediante estrategias sin modificar código existente
- **LSP**: Las entidades son sustituibles por sus subtipos
- **ISP**: Interfaces segregadas (Protocols especializados)
- **DIP**: Dependencia de abstracciones, no de implementaciones concretas

## 📄 Licencia

Propietario - Inmobiliaria Velar SAS © 2025
