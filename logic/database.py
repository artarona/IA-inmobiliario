import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

DB_PATH = "dante_properties.db"
LOG_PATH = "conversation_logs.db"



def initialize_databases():
    """Inicializa las bases de datos cargando propiedades desde JSON"""
    try:
        print("🔄 INICIALIZANDO BD CARGANDO DESDE JSON...")
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # ELIMINAR tabla existente para forzar recreación
            cursor.execute("DROP TABLE IF EXISTS properties")
            
            # CREAR tabla con esquema completo
            cursor.execute('''
                CREATE TABLE properties (
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
            
            # ✅ CARGAR PROPIEDADES DESDE ARCHIVO JSON
            propiedades = cargar_propiedades_desde_json()
            
            if not propiedades:
                print("⚠️ No se pudieron cargar propiedades desde JSON, usando datos de ejemplo")
                propiedades = obtener_propiedades_ejemplo()
            
            # Insertar propiedades en la base de datos
            for prop in propiedades:
                try:
                    cursor.execute('''
                        INSERT INTO properties (
                            id_temporal, titulo, barrio, precio, ambientes, metros_cuadrados,
                            descripcion, operacion, tipo, direccion, antiguedad, expensas,
                            cochera, balcon, pileta, acepta_mascotas, aire_acondicionado,
                            moneda_precio, moneda_expensas
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        prop.get('id_temporal', f"prop_{hash(prop.get('titulo', ''))}"),
                        prop['titulo'], prop['barrio'], prop['precio'],
                        prop['ambientes'], prop['metros_cuadrados'], prop.get('descripcion', ''),
                        prop['operacion'], prop['tipo'], prop.get('direccion'),
                        prop.get('antiguedad'), prop.get('expensas'), prop.get('cochera'),
                        prop.get('balcon'), prop.get('pileta'), prop.get('acepta_mascotas'),
                        prop.get('aire_acondicionado'), prop.get('moneda_precio', 'USD'),
                        prop.get('moneda_expensas', 'ARS')
                    ))
                    print(f"✅ Propiedad cargada: {prop['titulo']}")
                except Exception as e:
                    print(f"⚠️ Error cargando propiedad {prop.get('titulo', 'N/A')}: {e}")
            
            conn.commit()
            print(f"✅ Base de datos inicializada con {len(propiedades)} propiedades")
            
    except Exception as e:
        print(f"❌ Error crítico inicializando base de datos: {e}")

def cargar_propiedades_desde_json():
    """Carga propiedades desde el archivo properties.json"""
    try:
        json_path = "properties.json"
        
        # Verificar si el archivo existe
        if not os.path.exists(json_path):
            print(f"❌ Archivo {json_path} no encontrado")
            return None
        
        # Leer y parsear el JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            propiedades_data = json.load(f)
        
        print(f"📁 Archivo {json_path} encontrado, cargando propiedades...")
        
        # El archivo puede tener diferentes estructuras, manejemos ambas
        if isinstance(propiedades_data, list):
            # Caso 1: El JSON es directamente una lista de propiedades
            propiedades = propiedades_data
            print(f"   📊 Estructura: Lista directa ({len(propiedades)} propiedades)")
        elif isinstance(propiedades_data, dict) and 'propiedades' in propiedades_data:
            # Caso 2: El JSON tiene un objeto con clave 'propiedades'
            propiedades = propiedades_data['propiedades']
            print(f"   📊 Estructura: Objeto con clave 'propiedades' ({len(propiedades)} propiedades)")
        else:
            print(f"❌ Estructura JSON no reconocida")
            return None
        
        # Validar propiedades mínimas requeridas
        propiedades_validas = []
        for prop in propiedades:
            if all(key in prop for key in ['titulo', 'barrio', 'precio', 'operacion', 'tipo']):
                propiedades_validas.append(prop)
            else:
                print(f"⚠️ Propiedad incompleta omitida: {prop.get('titulo', 'Sin título')}")
        
        print(f"✅ {len(propiedades_validas)} propiedades válidas cargadas desde JSON")
        return propiedades_validas
        
    except Exception as e:
        print(f"❌ Error cargando propiedades desde JSON: {e}")
        return None

def obtener_propiedades_ejemplo():
    """Propiedades de ejemplo por si falla la carga del JSON"""
    return [
        {
            'id_temporal': 'prop_backup_001',
            'titulo': 'Casa de respaldo en Palermo',
            'barrio': 'Palermo',
            'precio': 1200.0,
            'ambientes': 2,
            'metros_cuadrados': 65.0,
            'descripcion': 'Propiedad de respaldo cargada desde código',
            'operacion': 'alquiler',
            'tipo': 'departamento',
            'moneda_precio': 'USD'
        }
    ]

def verificar_y_reparar_bd():
    """Verifica y repara la base de datos si es necesario"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # Verificar si la tabla existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='properties'")
            if not cursor.fetchone():
                print("🚨 Tabla 'properties' no existe - recreando BD...")
                initialize_databases()
                return
            
            # Verificar si tiene columnas esenciales
            cursor.execute("PRAGMA table_info(properties)")
            columnas = [col[1] for col in cursor.fetchall()]
            
            columnas_esenciales = ['id_temporal', 'precio', 'barrio', 'ambientes', 'metros_cuadrados', 'operacion', 'tipo']
            faltantes = [col for col in columnas_esenciales if col not in columnas]
            
            if faltantes:
                print(f"🚨 Columnas faltantes: {faltantes} - recreando BD...")
                initialize_databases()
            else:
                print("✅ Base de datos verificada correctamente")
                
    except Exception as e:
        print(f"🚨 Error verificando BD: {e} - recreando...")
        initialize_databases()

def query_properties(filters: Dict[str, Any]) -> List[Dict]:
    """Consulta propiedades con filtros"""
    try:
        # Asegurar que la BD esté en buen estado
        verificar_y_reparar_bd()
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM properties WHERE 1=1"
            params = []
            
            # Aplicar filtros
            if 'neighborhood' in filters and filters['neighborhood']:
                query += " AND barrio LIKE ?"
                params.append(f"%{filters['neighborhood']}%")
            if 'barrio' in filters and filters['barrio']:
                query += " AND barrio LIKE ?" 
                params.append(f"%{filters['barrio']}%")
            if 'min_price' in filters and filters['min_price']:
                query += " AND precio >= ?"
                params.append(filters['min_price'])
            if 'max_price' in filters and filters['max_price']:
                query += " AND precio <= ?"
                params.append(filters['max_price'])
            if 'min_rooms' in filters and filters['min_rooms']:
                query += " AND ambientes >= ?"
                params.append(filters['min_rooms'])
            if 'operacion' in filters and filters['operacion']:
                query += " AND operacion = ?"
                params.append(filters['operacion'])
            if 'tipo' in filters and filters['tipo']:
                query += " AND tipo = ?"
                params.append(filters['tipo'])
            if 'min_sqm' in filters and filters['min_sqm']:
                query += " AND metros_cuadrados >= ?"
                params.append(filters['min_sqm'])
            if 'max_sqm' in filters and filters['max_sqm']:
                query += " AND metros_cuadrados <= ?"
                params.append(filters['max_sqm'])
                
            query += " ORDER BY precio ASC"
                
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            print(f"🔍 Búsqueda encontrada: {len(results)} propiedades")
            return results
            
    except Exception as e:
        print(f"❌ Error en query_properties: {e}")
        return []

def get_historial_canal(canal: str, limit: int = 5) -> List[str]:
    """Obtiene historial de conversación por canal"""
    try:
        with sqlite3.connect(LOG_PATH) as conn:
            cursor = conn.cursor()
            
            # Crear tabla de logs si no existe
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
            
            cursor.execute('''
                SELECT user_message, bot_response FROM logs 
                WHERE channel = ? ORDER BY id DESC LIMIT ?
            ''', (canal, limit))
            
            historial = []
            for row in cursor.fetchall():
                historial.append(f"Usuario: {row[0]}")
                historial.append(f"Bot: {row[1]}")
                
            return historial
            
    except Exception as e:
        print(f"❌ Error obteniendo historial: {e}")
        return []

def get_last_bot_response(canal: str) -> Optional[str]:
    """Obtiene última respuesta del bot para un canal"""
    try:
        with sqlite3.connect(LOG_PATH) as conn:
            cursor = conn.cursor()
            
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
            
            cursor.execute('''
                SELECT bot_response FROM logs 
                WHERE channel = ? ORDER BY id DESC LIMIT 1
            ''', (canal,))
            
            result = cursor.fetchone()
            return result[0] if result else None
            
    except Exception as e:
        print(f"❌ Error obteniendo última respuesta: {e}")
        return None

def log_conversation(user_message: str, bot_response: str, channel: str, 
                    response_time: float, search_performed: bool, results_count: int):
    """Registra conversación en logs"""
    try:
        with sqlite3.connect(LOG_PATH) as conn:
            cursor = conn.cursor()
            
            # Crear tabla si no existe
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
            
            cursor.execute('''
                INSERT INTO logs (timestamp, channel, user_message, bot_response, 
                                response_time, search_performed, results_count)
                VALUES (datetime('now'), ?, ?, ?, ?, ?, ?)
            ''', (channel, user_message, bot_response, response_time, 
                  search_performed, results_count))
            
            conn.commit()
            print(f"📝 Log registrado - Canal: {channel}, Tiempo: {response_time:.2f}s")
            
    except Exception as e:
        print(f"❌ Error registrando log: {e}")

# Inicializar bases de datos al importar el módulo
verificar_y_reparar_bd()