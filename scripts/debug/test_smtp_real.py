"""
Test SMTP Real Authentication
"""
import smtplib
from src.infraestructura.configuracion.settings import obtener_configuracion

def test_smtp_auth():
    config = obtener_configuracion()
    
    print("=" * 60)
    print("SMTP AUTHENTICATION TEST")
    print("=" * 60)
    print(f"Server: {config.smtp_server}:{config.smtp_port}")
    print(f"User: {config.smtp_user}")
    print(f"Password Length: {len(config.smtp_password) if config.smtp_password else 0}")
    print()
    
    if not config.smtp_user or not config.smtp_password:
        print("❌ FAILED: Missing credentials in .env")
        return False
    
    try:
        print("Step 1: Connecting to SMTP server...")
        server = smtplib.SMTP(config.smtp_server, config.smtp_port, timeout=10)
        print("✅ Connected")
        
        print("\nStep 2: Starting TLS encryption...")
        server.starttls()
        print("✅ TLS started")
        
        print("\nStep 3: Authenticating...")
        server.login(config.smtp_user, config.smtp_password)
        print("✅ AUTHENTICATION SUCCESSFUL!")
        
        server.quit()
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✅")
        print("=" * 60)
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION FAILED")
        print(f"Error: {e}")
        print("\nPossible causes:")
        print("1. Incorrect App Password (regenerate in Microsoft Account)")
        print("2. Username/email incorrect")
        print("3. Account security settings blocking access")
        return False
        
    except Exception as e:
        print(f"\n❌ CONNECTION FAILED")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_smtp_auth()
