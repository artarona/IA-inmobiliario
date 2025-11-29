# database_fix.py - EJECUTAR SOLO UNA VEZ
import sqlite3
import json
import os

DB_PATH = "propiedades.db"

def fix_database():
    print("🔧 EJECUTANDO REPARACIÓN DEFINITIVA DE BD...")
    
    # 1. Eliminar BD corrupta
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️  BD corrupta eliminada")
    
    # 2. Crear nueva BD con esquema CORRECTO
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE properties (
            id_temporal TEXT PRIMARY KEY,
            titulo TEXT,
            barrio TEXT,
            precio REAL,
            ambientes INTEGER,
            metros_cuadrados REAL,
            operacion TEXT,
            tipo TEXT,
            descripcion TEXT,
            direccion TEXT,
            antiguedad INTEGER,
            estado TEXT,
            orientacion TEXT,
            expensas REAL,
            amenities TEXT,
            cochera TEXT,
            balcon TEXT,
            pileta TEXT,
            acepta_mascotas TEXT,
            aire_acondicionado TEXT,
            info_multimedia TEXT,
            documentos TEXT,
            videos TEXT,
            fotos TEXT,
            moneda_precio TEXT,
            moneda_expensas TEXT,
            fecha_procesamiento TEXT
        )
    ''')
    print("✅ Tabla creada con esquema correcto")
    
    # 3. Cargar datos desde JSON
    with open("propiedades.json", "r", encoding="utf-8") as f:
        propiedades = json.load(f)
    
    for p in propiedades:
        cur.execute('''
            INSERT INTO properties (
                id_temporal, titulo, barrio, precio, ambientes, metros_cuadrados,
                operacion, tipo, descripcion, direccion, antiguedad, estado,
                orientacion, expensas, amenities, cochera, balcon, pileta,
                acepta_mascotas, aire_acondicionado, info_multimedia,
                documentos, videos, fotos, moneda_precio, moneda_expensas,
                fecha_procesamiento
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            p.get('id_temporal'), p.get('titulo'), p.get('barrio'), p.get('precio'),
            p.get('ambientes'), p.get('metros_cuadrados'), p.get('operacion'),
            p.get('tipo'), p.get('descripcion'), p.get('direccion'), p.get('antiguedad'),
            p.get('estado'), p.get('orientacion'), p.get('expensas'), p.get('amenities'),
            p.get('cochera'), p.get('balcon'), p.get('pileta'), p.get('acepta_mascotas'),
            p.get('aire_acondicionado'), p.get('info_multimedia'),
            json.dumps(p.get('documentos', [])), json.dumps(p.get('videos', [])),
            json.dumps(p.get('fotos', [])), p.get('moneda_precio'),
            p.get('moneda_expensas'), p.get('fecha_procesamiento')
        ))
    
    conn.commit()
    
    # 4. Verificar
    cur.execute("SELECT COUNT(*) FROM properties")
    count = cur.fetchone()[0]
    print(f"✅ {count} propiedades cargadas")
    
    cur.execute("PRAGMA table_info(properties)")
    columnas = [col[1] for col in cur.fetchall()]
    print(f"📋 Columnas: {columnas}")
    
    conn.close()
    print("🎉 REPARACIÓN COMPLETADA")

if __name__ == "__main__":
    fix_database()