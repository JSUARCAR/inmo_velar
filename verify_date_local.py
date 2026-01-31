
from src.infraestructura.servicios.pdf_elite.templates.contrato_template_local import ContratoArrendamientoElite

def test_date_formatting():
    # Instantiate the class (mocking output_dir or just passing None if allowed for helper test)
    # The __init__ calls super which might need args, let's see. 
    # BaseDocumentTemplate usually takes output_dir=None by default or optional.
    
    try:
        contrato = ContratoArrendamientoElite(output_dir=None)
        
        test_dates = [
            ("2026-01-31", "31 de enero de 2026"),
            ("2025-12-25", "25 de diciembre de 2025"),
            ("2024-02-29", "29 de febrero de 2024"),
            ("invalid-date", "invalid-date"),
            ("", "")
        ]
        
        print("Starting verification of _format_date_spanish in ContratoArrendamientoElite (Local)...")
        all_passed = True
        
        for input_date, expected in test_dates:
            result = contrato._format_date_spanish(input_date)
            if result == expected:
                print(f"✅ Input: '{input_date}' -> Output: '{result}'")
            else:
                print(f"❌ Input: '{input_date}' -> Expected: '{expected}', Got: '{result}'")
                all_passed = False
                
        if all_passed:
            print("\n🎉 All date formatting tests passed for Local Contract!")
        else:
            print("\n⚠️ Some tests failed.")
            
    except Exception as e:
        print(f"❌ Error initializing or testing class: {e}")

if __name__ == "__main__":
    test_date_formatting()
