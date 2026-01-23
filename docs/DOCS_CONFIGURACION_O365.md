# 📧 Guía de Configuración: Envío de Correos con Office 365

Para que el sistema **InmoVelar** pueda enviar correos automáticamente usando tu cuenta de Office 365 Empresarial, necesitamos habilitar un permiso específico llamado **"SMTP Autenticado"**.

Como eres el administrador, tienes acceso total para hacer esto. Sigue estos pasos exactos:

---

## 🛑 PASO 1: Habilitar SMTP Autenticado (Desde el Admin Center)

Este paso le dice a Microsoft: *"Permite que un programa externo envíe correos en nombre de este usuario"*.

1.  Inicia sesión en el **[Centro de Administración de Microsoft 365](https://admin.microsoft.com/)** con tu cuenta de administrador.
2.  En el menú de la izquierda, haz clic en **Usuarios** y luego en **Usuarios activos**.
3.  Busca y haz clic en el **Usuario** que usaremos para enviar los correos (ej: tu propia cuenta o una cuenta tipo `info@...`).
4.  Se abrirá un panel lateral a la derecha. Haz clic en la pestaña **Correo**.
5.  Busca la sección que dice "Aplicaciones de correo electrónico" y haz clic en el enlace azul **Administrar aplicaciones de correo electrónico**.
6.  Asegúrate de que la casilla **SMTP autenticado** esté **MARCADA (✅)**.
    *   *Si estaba desmarcada, márcala.*
    *   *Si ya estaba marcada, déjala así.*
7.  Haz clic en **Guardar cambios**.

> ⏳ **Nota:** Este cambio puede tardar entre **5 a 15 minutos** en propagarse por los servidores de Microsoft.

---

## ⚠️ PASO 1.5: Habilitar "Contraseñas de Aplicación" (SOLUCIÓN A TU PROBLEMA)

**Si no te aparece la opción "Contraseña de aplicación", es porque tu organización la tiene desactivada. Como eres Admin, vamos a activarla:**

1.  En el mismo **[Centro de Administración](https://admin.microsoft.com/)**, ve a la sección de usuarios (Usuarios activos).
2.  En la barra superior (encima de la lista de usuarios), busca un botón que dice **"Autenticación multifactor"**. (Puede estar dentro de tres puntos `...` si no se ve).
    *   *Esto abrirá una nueva pestaña con un diseño antiguo/clásico.*
3.  En esa nueva pestaña, mira arriba y haz clic en **"Configuración del servicio"** (Service settings).
4.  Busca la sección **Contraseñas de aplicación**.
5.  **MARCA (✅)** la casilla: **"Permitir que los usuarios creen contraseñas de aplicación para iniciar sesión en aplicaciones que no son de explorador"**.
6.  Haz clic en **Guardar** (botón azul abajo).

> 🔄 **Ahora sí:** Vuelve a la página de "Información de Seguridad" (donde tomaste la captura), recarga la página (`F5`), dale a `+ Agregar método` y **ya debería aparecer la opción**.

---

## 🔑 PASO 2: Obtener la Contraseña de Aplicación

Ahora que ya habilitaste la opción:

1.  Ve a la página de **[Información de Seguridad (My Sign-Ins)](https://mysignins.microsoft.com/security-info)**.
2.  Haz clic en el botón `+ Agregar método de inicio de sesión`.
3.  Elige la opción **Contraseña de aplicación**.
4.  Ponle un nombre para identificarla, por ejemplo: `InmoVelarApp`.
5.  El sistema te mostrará una **contraseña larga y aleatoria** (ej: `xxyy-zzzz-aabb-ccdd`).
6.  **CÓPIALA y GUÁRDALA.** Esta será la contraseña que pondremos en el archivo `.env` del sistema.

---

## 🛠️ Resumen para el Sistema (Qué necesito de ti)

Una vez completados los pasos, necesitaré que tengas a la mano estos dos datos para configurarlos en el siguiente paso:

1.  **Email del Remitente:** (El que configuraste en el Paso 1).
2.  **Contraseña:** (La "Contraseña de Aplicación" del Paso 2, o tu clave normal si no usas MFA).

---
**¿Listo?** Una vez tengas esto, confírmame para proceder a configurar las variables de entorno.
