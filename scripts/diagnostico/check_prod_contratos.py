import psycopg2

def check_prod_contratos():
    conn = psycopg2.connect(
        host="hopper.proxy.rlwy.net",
        port=12937,
        user="postgres",
        password="tBltIuhaUSMqQFvUMtSqIPFQZdXwpPtU",
        dbname="railway"
    )
    cursor = conn.cursor()
    
    print("=== CONTRATOS_MANDATOS ===")
    cursor.execute("SELECT COUNT(*) FROM CONTRATOS_MANDATOS")
    print("Total Mandatos:", cursor.fetchone()[0])
    
    print("=== CONTRATOS_ARRENDAMIENTOS ===")
    cursor.execute("SELECT COUNT(*) FROM CONTRATOS_ARRENDAMIENTOS")
    print("Total Arrendamientos:", cursor.fetchone()[0])

check_prod_contratos()
