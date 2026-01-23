import sys
import os
import smtplib
from src.infraestructura.configuracion.settings import obtener_configuracion

def verificar_configuracion():
    print("=== Verificación de Configuración SMTP ===")
    
    try:
        config = obtener_configuracion()
        user = config.smtp_user
        password = config.smtp_password
        
        print(f"\n1. Analizando Variables Cargadas:")
        print(f"   SMTP_USER:     '{user}' (Longitud: {len(user) if user else 0})")
        
        if password:
            masked = "*" * (len(password) - 4) + password[-4:] if len(password) > 4 else "****"
            print(f"   SMTP_PASSWORD: '{masked}' (Longitud: {len(password)})")
            
            if " " in password:
                print("   ❌ ERROR DETECTADO: La contraseña contiene espacios.")
            if "'" in password or '"' in password:
                print("   ⚠️ ADVERTENCIA: La contraseña contiene comillas.")
        else:
            print("   SMTP_PASSWORD: [VACÍO/NONE]")
            
        print("\n2. Probando Conexión SMTP:")
        print(f"   Servidor: {config.smtp_server}:{config.smtp_port}")
        
        if not user or not password:
            print("   ❌ ABORTANDO: Faltan credenciales.")
            return

        try:
            server = smtplib.SMTP(config.smtp_server, config.smtp_port)
            server.set_debuglevel(1)
            server.starttls()
            print("   ✅ Conexión TLS establecida.")
            
            server.login(user, password)
            print("   ✅ Autenticación EXITOSA.")
            server.quit()
            
        except smtplib.SMTPAuthenticationError as e:
            print(f"   ❌ ERROR DE AUTENTICACIÓN: {e}")
            print("      Sugerencia: Verifique que está usando la 'Contraseña de Aplicación' y no su contraseña normal.")
        except Exception as e:
            print(f"   ❌ ERROR DE CONEXIÓN: {e}")

    except Exception as e:
        print(f"\n❌ Error General: {e}")

if __name__ == "__main__":
    verificar_configuracion()
