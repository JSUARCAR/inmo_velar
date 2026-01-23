"""
Sistema de Colores - Inmobiliaria Velar
Paleta basada en especificaciones UI/UX: Modernidad tecnologica + sobriedad profesional
"""

# ============================================================================
# COLORES PRIMARIOS
# ============================================================================
PRIMARY = "#2563EB"           # Azul corporativo moderno (acciones principales)
SECONDARY = "#64748B"         # Gris pizarra (elementos secundarios)
SURFACE = "#F8FAFC"           # Gris muy claro (fondos de cards)
BACKGROUND = "#FFFFFF"        # Blanco puro (fondo principal)
SURFACE_VARIANT = "#F1F5F9"   # Gris azulado muy claro (contenedores secundarios)

# ============================================================================
# COLORES SEMANTICOS (Estados y Alertas)
# ============================================================================
SUCCESS = "#10B981"           # Verde (exito, ocupado, pagado)
SUCCESS_LIGHT = "#D1FAE5"     # Verde claro (fondos de éxito)
WARNING = "#F59E0B"           # Amarillo/Ambar (advertencia, pendiente)
ERROR = "#EF4444"             # Rojo (error, mora, critico)
ERROR_LIGHT = "#FEE2E2"       # Rojo claro (fondos de error)
INFO = "#3B82F6"              # Azul claro (informativo, IPC)

# ============================================================================
# COLORES DE TEXTO
# ============================================================================
TEXT_PRIMARY = "#1E293B"      # Negro azulado (titulos, texto principal)
TEXT_SECONDARY = "#64748B"    # Gris medio (subtitulos, descripciones)
TEXT_DISABLED = "#CBD5E1"     # Gris claro (texto deshabilitado)
TEXT_ON_PRIMARY = "#FFFFFF"   # Blanco (texto sobre primary)
TEXT_ON_ERROR = "#FFFFFF"     # Blanco (texto sobre error)

# ============================================================================
# COLORES DE BORDE Y SOMBRA
# ============================================================================
BORDER_DEFAULT = "#E2E8F0"    # Gris muy claro (bordes sutiles)
BORDER_FOCUS = PRIMARY        # Azul (borde en foco)
SHADOW_SM = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
SHADOW_MD = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
SHADOW_LG = "0 10px 15px -3px rgba(0, 0, 0, 0.1)"

# ============================================================================
# GRADIENTES (Para elementos especiales)
# ============================================================================
GRADIENT_PRIMARY = f"linear-gradient(135deg, {PRIMARY} 0%, #1E40AF 100%)"
GRADIENT_SUCCESS = f"linear-gradient(135deg, {SUCCESS} 0%, #059669 100%)"
GRADIENT_ERROR = f"linear-gradient(135deg, {ERROR} 0%, #DC2626 100%)"

# ============================================================================
# COLORES ESPECIFICOS POR ROL
# ============================================================================
ADMIN_BADGE = "#7C3AED"       # Violeta (badge de admin)
ASESOR_BADGE = "#0EA5E9"      # Azul cielo (badge de asesor)

# ============================================================================
# OPACIDADES (Alpha channels para overlays)
# ============================================================================
OVERLAY_LIGHT = "rgba(0, 0, 0, 0.5)"
OVERLAY_DARK = "rgba(0, 0, 0, 0.75)"
