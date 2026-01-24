import os
import re

TARGET_FILES = [
    "verify_schema.py",
    "verify_fix.py",
    "test_simple_trigger.py",
    "list_tables.py",
    "generate_triggers.py",
    "diagnose_codeudor_35.py",
    "debug_sql.py",
    "create_ipc_table.py",
    "create_bonif_table.py",
    "apply_legal_rep_migration_standalone.py",
    "apply_fix_v2.py",
    "apply_fix.py",
    "apply_audit_full.py",
    "apply_audit_final.py",
    "scripts/force_clean_incidentes.py"
]

REPLACEMENT_BLOCK = """# Config from shared_db_config
try:
    from shared_db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
except ImportError:
    import sys
    import os
    # Add root to sys.path if running from subdir
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    try:
        from shared_db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
    except ImportError:
        # Fallback to env vars directly if shared config missing
        from dotenv import load_dotenv
        load_dotenv()
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_NAME = os.getenv("DB_NAME", "db_inmo_velar")
        DB_USER = os.getenv("DB_USER", "inmo_user")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "7323")
"""

REGEX_PATTERN = r'(DB_HOST\s*=\s*["\'].*?["\']\s*DB_PORT\s*=\s*\d+\s*DB_NAME\s*=\s*["\'].*?["\']\s*DB_USER\s*=\s*["\'].*?["\']\s*DB_PASSWORD\s*=\s*["\'].*?["\'])'

def sanitize_file(filepath):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize newlines for regex
    # replacement
    new_content = re.sub(REGEX_PATTERN, REPLACEMENT_BLOCK, content, flags=re.DOTALL)
    
    # Also catch cases where only DB_PASSWORD or password var is hardcoded but not the full block
    # This is tricky with regex, relying on the block pattern for the specific list is safer first.
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Sanitized {filepath}")
    else:
        print(f"No changes made to {filepath} (Pattern not found)")

if __name__ == "__main__":
    base_dir = os.getcwd()
    print(f"Working in {base_dir}")
    for fname in TARGET_FILES:
        full_path = os.path.join(base_dir, fname.replace('/', os.sep))
        sanitize_file(full_path)
