from datetime import datetime
from num2words import num2words

def verify_logic():
    print("--- Verifying Num2Words and Date Logic ---")
    
    # 1. Test Num2Words
    try:
        val = 1500000
        text = num2words(val, lang='es').upper()
        print(f"Num2Words Check ({val}): {text}")
        if "UN MILLÓN QUINIENTOS MIL" in text or "UN MILLON QUINIENTOS MIL" in text:
            print("SUCCESS: Num2Words is working.")
        else:
            print("WARNING: Num2Words output unexpected.")
    except Exception as e:
        print(f"ERROR: Num2Words failed: {e}")

    # 2. Test Date Logic
    print("\n--- Testing Date Logic ---")
    fecha_inicio = '2024-01-01'
    fecha_fin = '2025-01-01'
    
    dt_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    dt_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    
    diff_years = dt_fin.year - dt_inicio.year
    diff_months = dt_fin.month - dt_inicio.month
    calculated_months = (diff_years * 12) + diff_months
    
    print(f"Start: {fecha_inicio}, End: {fecha_fin}")
    print(f"Calculated Months: {calculated_months}")
    
    text_months = num2words(calculated_months, lang='es').upper()
    print(f"Months in Text: {text_months}")
    
    if calculated_months == 12 and ("DOCE" in text_months):
        print("SUCCESS: Date logic working.")
    else:
        print("WARNING: Date logic unexpected.")

if __name__ == "__main__":
    verify_logic()
