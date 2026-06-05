# Arquitectura y Configuración del MCP de Railway

## 1. Descripción General
El **Model Context Protocol (MCP)** de Railway permite a los asistentes y agentes de inteligencia artificial (como Cursor, Claude Code y OpenCode) interactuar directamente con la infraestructura de Railway del proyecto **Inmobiliaria Velar**.

## 2. Componentes de Arquitectura
- **Cliente:** Herramienta de IA local (Cursor, Claude Code, Codex, OpenCode).
- **Servidor Local (stdio):** El proceso ejecutado a través del comando `railway mcp`. Este proceso hereda las credenciales y el estado del entorno configurado por el CLI de Railway.
- **Canal:** `stdio` (entrada y salida estándar) utilizado para el envío de instrucciones JSON-RPC entre el agente y Railway.
- **Acceso:** Consultas a variables de entorno, metadatos de proyectos y logs, limitados a los permisos del token de Railway autenticado.

## 3. Procedimiento de Instalación Base
Se ejecutó el comando estándar de inyección:
```bash
railway mcp install
```
### Rutas Modificadas
La configuración fue aprovisionada satisfactoriamente en las siguientes ubicaciones detectadas en el sistema:
- **Claude Code**: `C:\Users\PC\.claude.json`
- **Cursor**: `C:\Users\PC\.cursor\mcp.json`
- **OpenAI Codex**: `C:\Users\PC\.codex\config.toml`
- **OpenCode**: `C:\Users\PC\.config\opencode\opencode.json`

## 4. Políticas de Seguridad (Hardening)
### 4.1. RBAC y Sesión
- El MCP local de Railway opera bajo el contexto del usuario autenticado en la terminal (`railway whoami`).
- **PROHIBIDO** el uso de tokens con permisos globales en entornos de desarrollo local; se debe emplear el login interactivo o un `RAILWAY_TOKEN` estrictamente acotado al proyecto actual.
- Las variables críticas o de producción nunca deben ser consultadas en logs no depurados si se comparte pantalla o se graba el entorno.

### 4.2. Aislamiento
El comando inyectado en los IDEs es `railway mcp`. Esto garantiza que los agentes no puedan ejecutar comandos mutativos que no estén explícitamente soportados por la especificación del protocolo. 

## 5. Mantenimiento y Extensibilidad

### Actualización del Cliente MCP
Dado que el MCP se actualiza junto con el CLI de Railway, el mantenimiento solo requiere:
```cmd
npm i -g @railway/cli
```

### Configuración Remota (Alternativa)
Si en el futuro se requiere desacoplar el servidor de la máquina de desarrollo, se puede re-ejecutar la instalación utilizando el flag `--remote`:
```cmd
railway mcp install --remote
```
Esto cambiará el transporte de `stdio` a `http`, apuntando a `https://mcp.railway.com`.

## 6. Resolución de Problemas (Troubleshooting)

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| El IDE reporta "Railway no autenticado" | La sesión local expiró o no existe | Abrir terminal local y ejecutar `railway login`. |
| El agente no detecta herramientas Railway | El IDE no fue reiniciado tras la instalación | Cerrar completamente y volver a abrir Cursor/VS Code. |
| Permisos insuficientes | El token expuso sólo entorno de desarrollo | Ejecutar `railway environment` para cambiar el scope. |

---
**Nota:** Este documento es mantenido como parte del conjunto de especificaciones técnicas del proyecto según `GEMINI.md`.
