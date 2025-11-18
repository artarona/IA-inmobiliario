import sqlite3
conn = sqlite3.connect("propiedades.db")
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM properties")
print("Cantidad de propiedades cargadas:", cur.fetchone()[0])
conn.close()