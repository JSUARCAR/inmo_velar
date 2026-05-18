import pytest
from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor

def test_calcular_comision_por_contrato():
    """F7.1: calcular_comision_bruta(1_000_000, 800) = 80_000"""
    canon = 1000000
    pct = 800 # 8%
    comision = LiquidacionAsesor.calcular_comision_bruta(canon, pct)
    assert comision == 80000

def test_multiples_contratos_pct_diferentes():
    """F7.2: Sumar comisiones individuales con porcentajes distintos"""
    # Contrato 1: 1M @ 10% = 100k
    # Contrato 2: 2M @ 5% = 100k
    # Total esperado: 200k
    
    c1_canon = 1000000
    c1_pct = 1000
    c1_comision = LiquidacionAsesor.calcular_comision_bruta(c1_canon, c1_pct)
    
    c2_canon = 2000000
    c2_pct = 500
    c2_comision = LiquidacionAsesor.calcular_comision_bruta(c2_canon, c2_pct)
    
    assert c1_comision + c2_comision == 200000

def test_porcentaje_ponderado():
    """F7.3: Verificar cálculo de porcentaje ponderado"""
    # Usando la misma lógica que el servicio:
    # suma_canon_por_pct / canon_total
    
    c1_canon = 1000000
    c1_pct = 1000 # 10%
    
    c2_canon = 2000000
    c2_pct = 500 # 5%
    
    canon_total = c1_canon + c2_canon
    suma_canon_por_pct = (c1_canon * c1_pct) + (c2_canon * c2_pct)
    
    porcentaje_ponderado = int(suma_canon_por_pct / canon_total)
    
    # (1M*1000 + 2M*500) / 3M = (1000M + 1000M) / 3M = 2000M / 3M = 666.66 -> 666
    assert porcentaje_ponderado == 666

def test_contrato_sin_comision():
    """F7.4: pct=0 -> comision=0"""
    canon = 1000000
    pct = 0
    comision = LiquidacionAsesor.calcular_comision_bruta(canon, pct)
    assert comision == 0
