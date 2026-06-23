import socket


def is_server_running(host="localhost", port=8000) -> bool:
    """Verifica si el servidor Reflex está corriendo en el puerto indicado."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.connect((host, port))
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False


SERVER_RUNNING = is_server_running()
