# Sistema de Gestión Inmobiliaria Velar

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Reflex](https://img.shields.io/badge/framework-Reflex-orange.svg)](https://reflex.dev/)
[![SQLite](https://img.shields.io/badge/database-SQLite-green.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

Un sistema integral de gestión inmobiliaria de nivel empresarial construido con tecnologías Python modernas, siguiendo los principios de Arquitectura Limpia y patrones de diseño SOLID. Este sistema proporciona capacidades completas de gestión de propiedades, manejo de contratos, operaciones financieras y gestión de usuarios para empresas inmobiliarias.

## 📋 Tabla de Contenidos

- [Resumen](#resumen)
- [Características Principales](#características-principales)
- [Arquitectura](#arquitectura)
- [Pila Tecnológica](#pila-tecnológica)
- [Prerrequisitos](#prerrequisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Esquema de Base de Datos](#esquema-de-base-de-datos)
- [Pruebas](#pruebas)
- [Despliegue](#despliegue)
- [Solución de Problemas](#solución-de-problemas)
- [Desarrollo](#desarrollo)
- [Contribución](#contribución)
- [Licencia](#licencia)

## 🎯 Resumen

El Sistema de Gestión Inmobiliaria Velar es una aplicación web completa diseñada para agilizar las operaciones inmobiliarias. Maneja todo, desde listados de propiedades y gestión de inquilinos hasta liquidaciones financieras, generación de contratos e informes integrales. El sistema está construido con escalabilidad, mantenibilidad y experiencia del usuario en mente.

### Capacidades Principales

- **Gestión de Propiedades**: Operaciones CRUD completas para propiedades, incluyendo imágenes, documentos y seguimiento de mantenimiento
- **Gestión de Contratos**: Generación automatizada de contratos, ajustes IPC y flujos de renovación
- **Operaciones Financieras**: Cálculos de comisiones, liquidaciones, pagos e informes financieros
- **Gestión de Usuarios**: Control de acceso basado en roles con permisos personalizables
- **Gestión Documental**: Generación integrada de PDF y almacenamiento de documentos
- **Seguimiento de Incidentes**: Sistema de gestión de incidentes estilo Kanban
- **Registro de Auditoría**: Capacidades de logging y auditoría integrales

## ✨ Características Principales

### 🏢 Gestión de Propiedades
- Búsqueda y filtrado avanzados de propiedades
- Galería de imágenes con carga de arrastrar y soltar
- Sistema de adjuntos de documentos
- Seguimiento de valoración de propiedades
- Gestión de estado de ocupación

### 📄 Operaciones de Contratos
- Generación automatizada de contratos (Arrendamiento y Mandato)
- Cálculos de ajustes IPC (Inflación)
- Flujos de renovación de contratos
- Integración de firma digital
- Seguimiento de estado de contratos

### 💰 Gestión Financiera
- Motores de cálculo de comisiones
- Liquidaciones y pagos de asesores
- Procesamiento masivo de liquidaciones
- Informes y análisis financieros
- Seguimiento y conciliación de pagos

### 👥 Gestión de Usuarios y Acceso
- Sistema de usuarios multi-rol (Admin, Asesor, Gerente, etc.)
- Sistema de permisos granulares
- Logging de actividad de usuarios
- Autenticación segura con gestión de sesiones

### 📊 Análisis e Informes
- Paneles en tiempo real con tarjetas KPI
- Gráficos y gráficos interactivos
- Generación de informes personalizados
- Capacidades de exportación (PDF, CSV, Excel)

### 🔧 Características Avanzadas
- Notificaciones y alertas en tiempo real
- Procesamiento de trabajos en segundo plano
- Integraciones API
- Diseño responsivo para móviles
- Soporte para arquitectura multi-tenant

## 🏗️ Arquitectura

Este proyecto implementa **Arquitectura Limpia** con estricta separación de responsabilidades, asegurando alta mantenibilidad, capacidad de prueba y escalabilidad.

### Capas Arquitectónicas

```
┌─────────────────────────────────────────┐
│           CAPA DE PRESENTACIÓN          │
│  ┌─────────────────────────────────────┐ │
│  │   Componentes Web Reflex & Páginas  │ │
│  │   Gestión de Estado & Manejo de Eventos │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         CAPA DE APLICACIÓN              │
│  ┌─────────────────────────────────────┐ │
│  │   Casos de Uso & Lógica de Negocio  │ │
│  │   DTOs, Mapeadores & Servicios      │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           CAPA DE DOMINIO               │
│  ┌─────────────────────────────────────┐ │
│  │   Entidades & Objetos de Valor      │ │
│  │   Servicios de Dominio & Reglas     │ │
│  │   Interfaces de Repositorio         │ │
└─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       CAPA DE INFRAESTRUCTURA           │
│  ┌─────────────────────────────────────┐ │
│  │   Implementaciones de Base de Datos │ │
│  │   APIs Externas & Servicios         │ │
│  │   Configuración & Logging           │ │
└─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Capa de Dominio
- **Entidades**: Objetos de negocio principales (Persona, Propiedad, Contrato, etc.)
- **Objetos de Valor**: Objetos inmutables (Dinero, IdentidadDocumento, Dirección, etc.)
- **Servicios de Dominio**: Lógica de negocio que no pertenece a entidades
- **Interfaces de Repositorio**: Contratos abstractos de acceso a datos
- **Eventos de Dominio**: Soporte para arquitectura orientada a eventos

### Capa de Aplicación
- **Casos de Uso**: Lógica de negocio específica de la aplicación
- **DTOs**: Objetos de Transferencia de Datos para comunicación entre capas
- **Mapeadores**: Utilidades de transformación de objetos
- **Servicios de Aplicación**: Orquestación de operaciones de dominio

### Capa de Infraestructura
- **Implementaciones de Repositorio**: Acceso a base de datos SQLite
- **Servicios Externos**: Generación de PDF, email, almacenamiento de archivos
- **Gestión de Configuración**: Configuraciones basadas en entorno
- **Logging y Monitoreo**: Logging estructurado y métricas

### Capa de Presentación
- **Componentes Reflex**: Componentes UI web modernos
- **Gestión de Estado**: Manejo reactivo de estado
- **Enrutamiento**: Navegación del lado del cliente
- **Integración API**: Comunicación RESTful con backend

## 🛠️ Pila Tecnológica

### Backend
- **Python 3.10+**: Lenguaje principal
- **Reflex**: Framework web moderno para Python
- **SQLite**: Base de datos primaria (con soporte de migración a PostgreSQL)
- **Pydantic**: Validación de datos y gestión de configuraciones
- **SQLAlchemy**: ORM para consultas complejas (planeado)

### Frontend
- **Reflex**: Framework UI basado en componentes
- **Plotly**: Gráficos y visualizaciones interactivas
- **Tailwind CSS**: Estilización utility-first (vía Reflex)

### Desarrollo y Pruebas
- **Pytest**: Framework de pruebas integral
- **Coverage.py**: Análisis de cobertura de código
- **Black**: Formateo de código
- **MyPy**: Verificación de tipos estáticos
- **Pre-commit**: Hooks de Git para aseguramiento de calidad

### DevOps y Despliegue
- **Docker**: Soporte de contenedorización
- **GitHub Actions**: Pipelines CI/CD
- **Poetry**: Gestión de dependencias (planeado)
- **PostgreSQL**: Soporte de base de datos de producción

## 📋 Prerrequisitos

### Requisitos del Sistema
- **Python**: 3.10 o superior
- **Node.js**: 16+ (para desarrollo Reflex)
- **Git**: 2.30+
- **SQLite**: 3.35+ (generalmente preinstalado)

### Requisitos de Hardware
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **Almacenamiento**: 2GB de espacio libre para aplicación y base de datos
- **Red**: Conexión a internet estable para instalación de paquetes

### Soporte de Sistema Operativo
- ✅ **Windows 10/11** (Plataforma de desarrollo primaria)
- ✅ **macOS 12+**
- ✅ **Ubuntu 20.04+**
- ⚠️ **Otras distribuciones Linux** (Pueden requerir configuración adicional)

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/your-org/inmobiliaria-velar.git
cd inmobiliaria-velar
```

### 2. Configuración del Entorno

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
# Instalar paquetes Python
pip install -r requirements.txt

# Para dependencias de desarrollo
pip install -r requirements-dev.txt
```

### 4. Configuración del Entorno

```bash
# Copiar plantilla de entorno
cp .env.example .env

# Editar .env con tus configuraciones
# DATABASE_PATH=./DB_Inmo_Velar.db
# SECRET_KEY=your-secret-key-here
# DEBUG=True
```

### 5. Inicialización de Base de Datos

La base de datos está preconfigurada e incluida en el repositorio:

```bash
# Verificar que la base de datos existe
ls -la DB_Inmo_Velar.db
```

> **Nota**: El archivo `DB_Inmo_Velar.db` contiene el esquema completo y datos iniciales. No se requieren migraciones para configuración básica.

### 6. Verificar Instalación

```bash
# Ejecutar verificación básica de salud
python -c "import reflex as rx; print('Versión de Reflex:', rx.__version__)"
```

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Predeterminado | Requerido |
|----------|-------------|---------------|-----------|
| `DATABASE_PATH` | Ruta del archivo de base de datos SQLite | `./DB_Inmo_Velar.db` | Sí |
| `SECRET_KEY` | Clave secreta de la aplicación | Auto-generada | Sí |
| `DEBUG` | Habilitar modo debug | `False` | No |
| `HOST` | Host del servidor | `0.0.0.0` | No |
| `PORT` | Puerto del servidor | `8000` | No |
| `LOG_LEVEL` | Nivel de logging | `INFO` | No |

### Configuración Avanzada

#### Configuración de Base de Datos
```python
# En .env
DATABASE_PATH=./data/production.db
DATABASE_BACKUP_DIR=./backups/
DATABASE_MAX_CONNECTIONS=10
```

#### Configuraciones de Seguridad
```python
# En .env
SECRET_KEY=your-256-bit-secret-key
SESSION_TIMEOUT=3600
PASSWORD_MIN_LENGTH=8
```

#### Configuración de Email (Opcional)
```python
# En .env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📝 Uso

### Modo Desarrollo

```bash
# Iniciar servidor de desarrollo
reflex run

# O usar el script dedicado
python main_reflex.py
```

La aplicación estará disponible en `http://localhost:8000`

### Modo Producción

```bash
# Construir para producción
reflex build

# Iniciar servidor de producción
reflex run --env prod
```

### Opciones de Línea de Comandos

```bash
# Mostrar ayuda
python main_reflex.py --help

# Ejecutar con puerto personalizado
reflex run --port 3000

# Habilitar logging de debug
reflex run --loglevel debug
```

### Interfaz de Usuario

#### Inicio de Sesión
- Acceder a la aplicación en la URL raíz
- Usar credenciales de administrador (configuradas en base de datos)
- Soporte de autenticación multifactor (planeado)

#### Panel de Control
- KPIs y métricas en tiempo real
- Gráficos y gráficos interactivos
- Acceso rápido a actividades recientes
- Centro de notificaciones

#### Navegación de Módulos
- **Propiedades**: Gestión y listados de propiedades
- **Contratos**: Creación y gestión de contratos
- **Financiero**: Liquidaciones y pagos
- **Usuarios**: Gestión de usuarios y permisos
- **Informes**: Análisis e informes
- **Configuraciones**: Configuración del sistema

## 🗄️ Esquema de Base de Datos

### Tablas Principales

| Tabla | Descripción | Campos Clave |
|-------|-------------|--------------|
| `personas` | Personas/entidades en el sistema | id, tipo_documento, numero_documento, nombre |
| `usuarios` | Usuarios del sistema | id, username, password_hash, rol |
| `propiedades` | Propiedades | id, direccion, tipo, valor, estado |
| `contratos` | Contratos | id, propiedad_id, arrendatario_id, fecha_inicio, fecha_fin |
| `liquidaciones` | Liquidaciones | id, asesor_id, periodo, total_comision |
| `pagos` | Pagos | id, liquidacion_id, monto, fecha_pago |
| `auditoria` | Registro de auditoría | id, tabla, operacion, usuario_id, fecha |

### Relaciones

```
personas (1) ──── (N) contratos
personas (1) ──── (N) liquidaciones (asesores)
propiedades (1) ──── (N) contratos
contratos (1) ──── (N) pagos
liquidaciones (1) ──── (N) pagos
```

### Índices y Restricciones

- Claves primarias en todas las tablas
- Restricciones de clave foránea con eliminaciones en cascada
- Restricciones únicas en campos críticos
- Índices de búsqueda de texto completo en campos de texto
- Restricciones de verificación para validación de datos

## 🧪 Pruebas

### Ejecutar Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=src --cov-report=html --cov-report=term

# Ejecutar archivo de prueba específico
pytest tests/test_domain/test_persona.py

# Ejecutar pruebas con salida verbosa
pytest -v
```

### Estructura de Pruebas

```
tests/
├── unit/                    # Pruebas unitarias
│   ├── test_domain/        # Pruebas de capa de dominio
│   ├── test_application/   # Pruebas de capa de aplicación
│   └── test_infrastructure/ # Pruebas de capa de infraestructura
├── integration/            # Pruebas de integración
├── e2e/                    # Pruebas end-to-end
└── fixtures/               # Datos de prueba fixtures
```

### Objetivos de Cobertura de Pruebas

- **Capa de Dominio**: 95%+ cobertura
- **Capa de Aplicación**: 90%+ cobertura
- **Capa de Infraestructura**: 80%+ cobertura
- **General**: 85%+ cobertura

### Pruebas de Rendimiento

```bash
# Pruebas de carga
pytest tests/performance/ --durations=10

# Perfilado de memoria
python -m memory_profiler main_reflex.py
```

## 🚢 Despliegue

### Despliegue Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["reflex", "run", "--env", "prod"]
```

```bash
# Construir y ejecutar
docker build -t inmobiliaria-velar .
docker run -p 8000:8000 inmobiliaria-velar
```

### Despliegue en la Nube

#### Railway
1. Conectar repositorio GitHub
2. Establecer variables de entorno
3. Desplegar automáticamente

#### Heroku
```yaml
# Procfile
web: reflex run --env prod --port $PORT
```

#### AWS/GCP
- Usar contenedores Docker
- Configurar balanceadores de carga
- Configurar bases de datos administradas
- Implementar CDN para activos estáticos

### Lista de Verificación de Producción

- [ ] Variables de entorno configuradas
- [ ] Respaldos de base de datos programados
- [ ] Certificados SSL instalados
- [ ] Monitoreo y logging configurados
- [ ] Encabezados de seguridad configurados
- [ ] Optimización de rendimiento aplicada

## 🔧 Solución de Problemas

### Problemas Comunes

#### Errores de Conexión a Base de Datos
```bash
# Verificar archivo de base de datos
ls -la DB_Inmo_Velar.db

# Verificar permisos
chmod 644 DB_Inmo_Velar.db

# Verificar integridad de base de datos
python -c "import sqlite3; conn = sqlite3.connect('DB_Inmo_Velar.db'); print('OK')"
```

#### Puerto Ya en Uso
```bash
# Encontrar proceso usando el puerto
netstat -tulpn | grep :8000

# Matar proceso
kill -9 <PID>

# O usar puerto diferente
reflex run --port 3000
```

#### Errores de Importación
```bash
# Reinstalar dependencias
pip uninstall reflex
pip install -r requirements.txt

# Limpiar caché
rm -rf __pycache__/
rm -rf .reflex/
```

#### Problemas de Memoria
```bash
# Aumentar límites del sistema
ulimit -n 4096

# Usar consultas de base de datos más ligeras
# Implementar paginación
# Agregar índices de base de datos
```

### Modo Debug

```bash
# Habilitar logging de debug
export LOG_LEVEL=DEBUG
reflex run

# Verificar logs
tail -f reflex.log
```

### Problemas de Rendimiento

1. **Optimización de Base de Datos**
   - Agregar índices faltantes
   - Optimizar consultas
   - Implementar agrupamiento de conexiones

2. **Optimización de Aplicación**
   - Habilitar caché
   - Usar operaciones asíncronas
   - Implementar carga diferida

3. **Optimización del Sistema**
   - Aumentar RAM
   - Usar almacenamiento SSD
   - Configurar espacio de intercambio

## 💻 Desarrollo

### Calidad del Código

```bash
# Formatear código
black src/ tests/

# Verificación de tipos
mypy src/

# Lint código
flake8 src/

# Ejecutar hooks pre-commit
pre-commit run --all-files
```

### Flujo de Trabajo de Desarrollo

1. **Crear Rama de Característica**
   ```bash
   git checkout -b feature/nueva-caracteristica
   ```

2. **Escribir Pruebas Primero**
   ```bash
   # Crear archivo de prueba
   touch tests/test_caracteristica.py
   ```

3. **Implementar Característica**
   ```bash
   # Seguir principios de Arquitectura Limpia
   # Agregar lógica de dominio primero
   # Luego servicios de aplicación
   # Finalmente componentes de presentación
   ```

4. **Ejecutar Pruebas**
   ```bash
   pytest tests/test_caracteristica.py
   ```

5. **Revisión de Código**
   ```bash
   # Asegurar que el código sigue estándares
   # Agregar documentación
   # Actualizar README si es necesario
   ```

### Mejores Prácticas

#### Estilo de Código
- Seguir directrices PEP 8
- Usar hints de tipo extensivamente
- Escribir nombres de variables descriptivos
- Mantener funciones pequeñas y enfocadas

#### Directrices de Arquitectura
- Respetar límites de capas
- Usar inyección de dependencias
- Implementar manejo de errores apropiado
- Escribir pruebas integrales

#### Seguridad
- Validar todas las entradas
- Usar consultas parametrizadas
- Implementar autenticación apropiada
- Registrar eventos de seguridad

#### Rendimiento
- Optimizar consultas de base de datos
- Usar caché estratégicamente
- Implementar paginación
- Monitorear uso de recursos

## 🤝 Contribución

### Proceso de Contribución

1. **Hacer Fork del Repositorio**
2. **Crear Rama de Característica**
   ```bash
   git checkout -b feature/caracteristica-increible
   ```
3. **Confirmar Cambios**
   ```bash
   git commit -m "Agregar caracteristica increible"
   ```
4. **Enviar a Rama**
   ```bash
   git push origin feature/caracteristica-increible
   ```
5. **Abrir Pull Request**

### Lista de Verificación de Revisión de Código

- [ ] Pruebas pasan
- [ ] Código sigue directrices de estilo
- [ ] Documentación actualizada
- [ ] No hay vulnerabilidades de seguridad
- [ ] Impacto de rendimiento evaluado
- [ ] Migraciones de base de datos incluidas (si aplica)

### Formato de Mensajes de Commit

```
tipo(alcance): descripción

[cuerpo opcional]

[pie de página opcional]
```

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 📄 Licencia

**Software Propietario**

Copyright © 2025 Inmobiliaria Velar SAS. Todos los derechos reservados.

Este software es propietario y confidencial. La copia, modificación, distribución o uso no autorizado de este software está estrictamente prohibido.

Para consultas de licenciamiento, por favor contactar: legal@inmobiliariavelar.com

---

**Construido con ❤️ por el Equipo de Desarrollo de Inmobiliaria Velar**
