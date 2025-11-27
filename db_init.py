### `backend/db_init.py`
# Script para inicializar la BD SQLite a partir de properties.json
import sqlite3
import json
import os

HERE = os.path.dirname(__file__)
DB = os.path.join(HERE, 'propiedades.db')
JSON = os.path.join(HERE, 'properties.json')

with open(JSON, 'r', encoding='utf-8') as f:
    props = json.load(f)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute('''
CREATE TABLE IF NOT EXISTS properties (
    id_temporal TEXT PRIMARY KEY,
    titulo TEXT,
    barrio TEXT,
    precio INTEGER,
    ambientes INTEGER,
    metros_cuadrados INTEGER,
    operacion TEXT,
    tipo TEXT,
    descripcion TEXT,
    direccion TEXT,
    antiguedad INTEGER,
    estado TEXT,
    orientacion TEXT,
    expensas INTEGER,
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

cur.execute('DELETE FROM properties')
for p in props:
    cur.execute('INSERT INTO properties (id_temporal, titulo, barrio, precio, ambientes, metros_cuadrados, operacion, tipo, descripcion, direccion, antiguedad, estado, orientacion, expensas, amenities, cochera, balcon, pileta, acepta_mascotas, aire_acondicionado, info_multimedia, documentos, videos, fotos, moneda_precio, moneda_expensas, fecha_procesamiento) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (p.get('id_temporal'), p.get('titulo'), p.get('barrio'), p.get('precio'), p.get('ambientes'), p.get('metros_cuadrados'), p.get('operacion'), p.get('tipo'), p.get('descripcion'), p.get('direccion'), p.get('antiguedad'), p.get('estado'), p.get('orientacion'), p.get('expensas'), p.get('amenities'), p.get('cochera'), p.get('balcon'), p.get('pileta'), p.get('acepta_mascotas'), p.get('aire_acondicionado'), p.get('info_multimedia'), json.dumps(p.get('documentos')), json.dumps(p.get('videos')), json.dumps(p.get('fotos')), p.get('moneda_precio'), p.get('moneda_expensas'), p.get('fecha_procesamiento')))

conn.commit()
conn.close()
print('DB inicializada en', DB)
