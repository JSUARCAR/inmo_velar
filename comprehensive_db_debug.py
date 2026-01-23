#!/usr/bin/env python3
"""
Elite Debug Script: Comprehensive Database Diagnosis
Runs all debug layers and generates diagnostic report
"""

import sys
sys.path.insert(0, r'c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX')

from src.infraestructura.persistencia.database import db_manager
import re

print("=" * 80)
print("ELITE DEBUG REPORT: SQL Placeholder Syntax Error")
print("=" * 80)

# LAYER 1: Database Configuration
print("\n### LAYER 1: Database Configuration ###")
print(f"Database Type: {getattr(db_manager, 'db_type', 'UNKNOWN')}")
print(f"Database URL: {db_manager.database_url}")

if hasattr(db_manager, 'get_placeholder'):
    placeholder = db_manager.get_placeholder()
    print(f"Placeholder returned by get_placeholder(): '{placeholder}'")
else:
    print("❌ CRITICAL: get_placeholder() method NOT FOUND")
    placeholder = "UNKNOWN"

# LAYER 2: Connection Analysis
print("\n### LAYER 2: Connection Analysis ###")
try:
    with db_manager.obtener_conexion() as conn:
        print(f"Connection Type: {type(conn)}")
        print(f"Connection Module: {conn.__class__.__module__}")
        
        cursor = conn.cursor()
        print(f"Cursor Type: {type(cursor)}")
        
        # Determine actual database
        if 'psycopg' in conn.__class__.__module__:
            actual_db = "PostgreSQL"
            expected_placeholder = "%s"
        elif 'sqlite' in conn.__class__.__module__:
            actual_db = "SQLite"
            expected_placeholder = "?"
        else:
            actual_db = "UNKNOWN"
            expected_placeholder = "UNKNOWN"
            
        print(f"Actual Database: {actual_db}")
        print(f"Expected Placeholder: '{expected_placeholder}'")
        
except Exception as e:
    print(f"❌ ERROR getting connection: {e}")
    actual_db = "ERROR"
    expected_placeholder = "ERROR"

# LAYER 3: Mismatch Detection
print("\n### LAYER 3: Placeholder Mismatch Analysis ###")
if placeholder != "UNKNOWN" and expected_placeholder != "UNKNOWN":
    if placeholder == expected_placeholder:
        print(f"✅ MATCH: get_placeholder() returns '{placeholder}' for {actual_db}")
    else:
        print(f"❌ MISMATCH DETECTED!")
        print(f"   get_placeholder() returns: '{placeholder}'")
        print(f"   {actual_db} expects: '{expected_placeholder}'")
        print(f"   → This is the ROOT CAUSE of the syntax error")

# LAYER 4: Test Query Execution
print("\n### LAYER 4: Test Query with Different Placeholders ###")
try:
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # Test 1: With ?
        print("\nTest 1: Query with '?' placeholder")
        try:
            cursor.execute("SELECT 1 WHERE 1 = ?", (1,))
            print("   Result: SUCCESS (? works)")
        except Exception as e:
            print(f"   Result: FAILED - {str(e)[:100]}")
        
        # Test 2: With %s
        print("\nTest 2: Query with '%s' placeholder")
        try:
            cursor.execute("SELECT 1 WHERE 1 = %s", (1,))
            print("   Result: SUCCESS (%s works)")
        except Exception as e:
            print(f"   Result: FAILED - {str(e)[:100]}")
            
except Exception as e:
    print(f"❌ ERROR during testing: {e}")

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
print("\nNext Steps:")
print("1. If MISMATCH detected: Fix get_placeholder() method in database.py")
print("2. If hardcoded placeholders found: Replace with get_placeholder() calls")
print("3. Re-run application and verify fix")
