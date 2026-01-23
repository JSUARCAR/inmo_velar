# 📢 Propuesta: Módulo de Notificaciones (WhatsApp + Email)

## 1. Objetivo General
Implementar un sistema de notificaciones multicanal para enriquecer la funcionalidad de alertas actual (`ServicioAlertas`). Este módulo **enviará activamente** información relevante a usuarios externos (Inquilinos, Propietarios, Asesores) y administradores.

## 2. Alcance Funcional Ajustado

### A. Canales de Comunicación

#### 📧 Email (Office 365 Empresarial)
Uso de la infraestructura existente de Microsoft 365 para envíos formales, seguros y con alta entregabilidad.
- **Configuración:** SMTP a través de Office 365 (`smtp.office365.com`).
- **Casos de Uso:** Envío de adjuntos (PDFs), facturas, estados de cuenta y notificaciones legales.

#### 📱 WhatsApp (Desktop Automatizado)
Uso de la aplicación de escritorio **WhatsApp Desktop** instalada en el equipo local.
- **Requisito del Usuario:** Envíos **sin intervención manual** ("sin oprimir botón de enviar").
- **Solución Técnica:** Automatización de Interfaz (RPA) local. El sistema abrirá la aplicación y simulará la tecla `Enter` automáticamente.

---

## 3. Propuesta Técnica y Arquitectura

### Estructura de Carpetas

```text
src/
├── infraestructura/
│   ├── notificaciones/
│   │   ├── cliente_email_office365.py  # Cliente SMTP específico O365
│   │   ├── cliente_whatsapp_desktop.py # Automatización con PyAutoGUI
│   └── templates/
│       ├── email/                      # Plantillas HTML
│       └── whatsapp/                   # Mensajes de texto
├── aplicacion/
│   └── servicios/
│       └── servicio_notificaciones.py  # Orquestador
```

### Tecnologías y Flujos

#### 1. Para Email (Office 365) 📧
Utilizaremos `smtplib` con configuración específica TLS para Microsoft 365.

*   **Requisito de Administrador (Tu rol):**
    *   Debes asegurarte de que la cuenta remitente tenga habilitado **"SMTP Auenticado"** (Authenticated SMTP) en el Centro de Administración de Microsoft 365 (Usuarios > Usuarios activos > Correo > Aplicaciones de correo electrónico).
*   **Flujo:**
    1.  Sistema genera el PDF (ej: recibo).
    2.  Conecta al servidor `smtp.office365.com` (Puerto 587).
    3.  Autentica con credenciales de la cuenta designada.
    4.  Envía el correo con el adjunto.

#### 2. Para WhatsApp (Desktop Automation) 📱
Para lograr el envío "sin clic", utilizaremos una combinación de **Protocol Links** y **Simulación de Teclado**.

*   **Librerías:** `webbrowser` (nativa) + `pyautogui` (para simular el teclado).
*   **Flujo Automatizado:**
    1.  El sistema construye la URL especial: `whatsapp://send?phone=573001234567&text=Hola...`
    2.  Se ejecuta el comando para abrir esta URL.
    3.  El sistema operativo detecta el protocolo y abre la app **WhatsApp Desktop**.
    4.  El script espera unos segundos (configurable, ej: 3s) para dar tiempo a que la app cargue y pegue el texto en la caja de chat.
    5.  El script simula la pulsación de la tecla `ENTER` automáticamente.
    6.  El mensaje se envía.
    *   *(Opcional: El script simula `Alt+F4` o minimiza la ventana para regresar al foco).*

*   **Consideraciones Importantes:**
    *   El PC debe estar desbloqueado.
    *   No se debe mover el mouse ni escribir mientras se ejecuta la macro (dura ~2-3 segundos).
    *   Requiere tener WhatsApp Desktop instalado y logueado.

---

## 4. Plan de Implementación (Fase 17)

### Fase 17.1: Configuración de Entorno
- Instalar librería de automatización: `pip install pyautogui`
- Crear variables de entorno en `.env` para credenciales O365 y tiempos de espera de WhatsApp.

### Fase 17.2: Implementación Cliente Email (Office 365)
- Crear clase `ClienteEmailOffice365`.
- Implementar manejo de errores específicos de Microsoft (ej: bloqueos de seguridad).
- Prueba de envío de correo simple.

### Fase 17.3: Implementación Cliente WhatsApp Desktop
- Crear clase `ClienteWhatsAppDesktop`.
- Implementar función `enviar_mensaje_auto(telefono, texto)`.
- Calibrar los tiempos de espera (`sleep`) para asegurar que el mensaje no se envíe antes de que abra la app.

### Fase 17.4: Integración en UI
- Agregar botón "Notificar" en las vistas clave (Liquidaciones, Recibos).
- Al hacer clic, el sistema ejecuta la acción en segundo plano (Email) o toma control momentáneo (WhatsApp).

---

## 5. Requisitos de Configuración (.env)

```ini
# Configuración Email Office 365
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USER=tu_correo@tudominio.com
SMTP_PASSWORD=tu_contraseña

# Configuración WhatsApp Desktop
WA_AUTOSEND_DELAY=3.5  # Segundos a esperar antes de presionar Enter
```
