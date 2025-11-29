
import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List

# ✅ CONFIGURACIONES
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "propiedades.db")
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "conversaciones.db")

# ✅ FUNCIONES DE BASE DE DATOS
def cargar_propiedades_json(filename):
    try:
        with open(filename, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Archivo {filename} no encontrado")
        return []
    except json.JSONDecodeError as e:
        print(f"⚠️ Error decodificando JSON en {filename}: {e}")
        return []
    except Exception as e:
        print(f"⚠️ Error al cargar {filename}: {e}")
        return []

def cargar_propiedades_a_db():
    """Carga las propiedades del JSON a la base de datos SQLite"""
    try:
        propiedades = cargar_propiedades_json("properties.json")
        if not propiedades:
            print("❌ No hay propiedades para cargar")
            return
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        propiedades_cargadas = 0
        for p in propiedades:
            try:
                cur.execute('''
                    INSERT OR REPLACE INTO properties (
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
                propiedades_cargadas += 1
                
            except Exception as e:
                print(f"⚠️ Error cargando propiedad {p.get('titulo', 'N/A')}: {e}")
                continue
        
        conn.commit()
        conn.close()
        print(f"✅ {propiedades_cargadas}/{len(propiedades)} propiedades cargadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error cargando propiedades a DB: {e}")

# En logic/database.py - actualiza la función initialize_databases()

def initialize_databases():
    """Inicializa las bases de datos con el esquema correcto"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Tabla de logs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    response_time REAL,
                    search_performed INTEGER DEFAULT 0,
                    results_count INTEGER DEFAULT 0
                )
            ''')
            
            # Tabla de propiedades con todas las columnas necesarias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS properties (
                    id_temporal TEXT PRIMARY KEY,
                    titulo TEXT NOT NULL,
                    barrio TEXT NOT NULL,
                    precio REAL NOT NULL,
                    ambientes INTEGER NOT NULL,
                    metros_cuadrados REAL NOT NULL,
                    descripcion TEXT,
                    operacion TEXT NOT NULL,
                    tipo TEXT NOT NULL,
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
                    moneda_precio TEXT DEFAULT 'USD',
                    moneda_expensas TEXT DEFAULT 'ARS',
                    fecha_procesamiento TEXT
                )
            ''')
            
            conn.commit()
            print("✅ Tablas creadas/verificadas con esquema actualizado")
            
    except Exception as e:
        print(f"❌ Error inicializando bases de datos: {e}")
        
def verificar_y_reparar_bd():
    """Verifica y repara la base de datos en cada inicio"""
    try:
        print("🔍 Verificando estado de la base de datos...")
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Verificar si la tabla existe
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='properties'")
        if not cur.fetchone():
            print("🚨 Tabla 'properties' no existe - recreando...")
            conn.close()
            initialize_databases()
            return
        
        # Verificar columnas críticas
        cur.execute("PRAGMA table_info(properties)")
        columnas = [col[1] for col in cur.fetchall()]
        
        columnas_requeridas = ['barrio', 'precio', 'operacion', 'tipo']
        
        for col in columnas_requeridas:
            if col not in columnas:
                print(f"🚨 Columna '{col}' faltante - recreando BD...")
                conn.close()
                initialize_databases()
                return
        
        # Verificar si hay datos
        cur.execute("SELECT COUNT(*) FROM properties")
        count = cur.fetchone()[0]
        
        if count == 0:
            print("🔄 BD vacía - cargando propiedades...")
            conn.close()
            cargar_propiedades_a_db()
            return
        
        conn.close()
        print("✅ BD verificada correctamente")
        
    except Exception as e:
        print(f"❌ Error verificando BD: {e}")
        # Forzar recreación
        initialize_databases()

def get_historial_canal(canal="web", limite=3):
    try:
        conn = sqlite3.connect(LOG_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT user_message FROM logs WHERE channel = ? ORDER BY id DESC LIMIT ?",
            (canal, limite)
        )
        rows = cur.fetchall()
        conn.close()
        return [r["user_message"] for r in reversed(rows)]
    except Exception as e:
        print(f"❌ Error obteniendo historial: {e}")
        return []

def get_last_bot_response(channel="web"):
    try:
        conn = sqlite3.connect(LOG_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT bot_response FROM logs WHERE channel = ? ORDER BY id DESC LIMIT 1",
            (channel,)
        )
        row = cur.fetchone()
        conn.close()
        return row["bot_response"] if row else None
    except Exception as e:
        print(f"❌ Error obteniendo la última respuesta del bot: {e}")
        return None

def query_properties(filters=None, cache_duration=300):
    query_cache = {}

    def get_cache_key(filters: Dict[str, Any]) -> str:
        """Genera una clave única para el cache basada en los filtros"""
        return json.dumps(filters, sort_keys=True)

    def cache_query_results(filters: Dict[str, Any], results: List[Dict]):
        """Almacena resultados en cache"""
        cache_key = get_cache_key(filters)
        query_cache[cache_key] = {
            'results': results,
            'timestamp': time.time()
        }

    def get_cached_results(filters: Dict[str, Any]) -> Optional[List[Dict]]:
        """Obtiene resultados del cache si están disponibles y no han expirado"""
        cache_key = get_cache_key(filters)
        cached = query_cache.get(cache_key)
        
        if cached and (time.time() - cached['timestamp']) < cache_duration:
            return cached['results']
        return None
        
    try:
        if filters:
            cached_results = get_cached_results(filters)
            if cached_results is not None:
                print("🔍 Usando resultados cacheados")
                return cached_results
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        q = "SELECT * FROM properties"
        params = []
        
        if filters:
            where_clauses = []
            
            if filters.get("neighborhood"):
                where_clauses.append("LOWER(barrio) LIKE LOWER(?)")
                params.append(f"%{filters['neighborhood']}%")
                
            if filters.get("min_price") is not None:
                where_clauses.append("precio >= ?")
                params.append(filters["min_price"])
                
            if filters.get("max_price") is not None:
                where_clauses.append("precio <= ?")
                params.append(filters["max_price"])
                
            if filters.get("operacion"):
                where_clauses.append("LOWER(operacion) LIKE LOWER(?)")
                params.append(f"%{filters['operacion']}%")
            
            if filters.get("min_rooms") is not None:
                where_clauses.append("ambientes >= ?")
                params.append(filters["min_rooms"])
                
            if filters.get("tipo"):
                where_clauses.append("LOWER(tipo) LIKE LOWER(?)")
                params.append(f"%{filters['tipo']}%")
                
            if filters.get("min_sqm") is not None:
                where_clauses.append("metros_cuadrados >= ?")
                params.append(filters["min_sqm"])
                
            if filters.get("max_sqm") is not None:
                where_clauses.append("metros_cuadrados <= ?")
                params.append(filters["max_sqm"])
                
            if where_clauses:
                q += " WHERE " + " AND ".join(where_clauses)
        
        q += " ORDER BY precio ASC LIMIT 50"
        
        cur.execute(q, params)
        rows = cur.fetchall()
        conn.close()
        
        results = [dict(r) for r in rows]
        
        if filters and results:
            cache_query_results(filters, results)
        
        return results
    except Exception as e:
        print(f"❌ Error en query_properties: {e}")
        return []



def log_conversation(user_text, response_text, channel="web", response_time=0.0, search_performed=False, results_count=0):
    try:
        conn = sqlite3.connect(LOG_PATH)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO logs (timestamp, channel, user_message, bot_response, response_time, search_performed, results_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), channel, user_text, response_text, response_time, search_performed, results_count))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ Error en log: {e}")
