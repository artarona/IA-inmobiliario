import sqlite3
import os
import json
from typing import List, Dict, Any, Optional

DB_PATH = "dante_properties.db"
LOG_PATH = "conversation_logs.db"

def initialize_databases():
    """Inicializa las bases de datos con el esquema CORRECTO"""
    try:
        print("🔄 INICIALIZANDO BD CON ESQUEMA CORREGIDO...")
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            
            # ELIMINAR tabla existente para forzar recreación
            cursor.execute("DROP TABLE IF EXISTS properties")
            
            # CREAR tabla con TODAS las columnas necesarias
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
            
            # Insertar datos de ejemplo COMPLETOS
            propiedades = [
                {
                    'id_temporal': 'prop_001',
                    'titulo': 'Casa en Parque Avellaneda',
                    'barrio': 'Parque Avellaneda', 
                    'precio': 250000.0,
                    'ambientes': 3,
                    'metros_cuadrados': 120.0,
                    'descripcion': 'Hermosa casa con jardín y cochera, ideal para familia',
                    'operacion': 'venta',
                    'tipo': 'casa',
                    'direccion': 'Av. Directorio 4500',
                    'antiguedad': 10,
                    'expensas': 5000.0,
                    'cochera': 'Sí',
                    'balcon': 'Sí',
                    'pileta': 'No',
                    'acepta_mascotas': 'Sí',
                    'aire_acondicionado': 'Sí',
                    'moneda_precio': 'USD',
                    'moneda_expensas': 'ARS'
                },
                {
                    'id_temporal': 'prop_002',
                    'titulo': 'Terreno en Boedo',
                    'barrio': 'Boedo',
                    'precio': 150000.0,
                    'ambientes': 0,
                    'metros_cuadrados': 200.0,
                    'descripcion': 'Terreno ideal para construcción, excelente ubicación',
                    'operacion': 'venta',
                    'tipo': 'terreno', 
                    'direccion': 'Av. La Plata 1200',
                    'moneda_precio': 'USD'
                },
                {
                    'id_temporal': 'prop_003',
                    'titulo': 'Monoambiente microcentro',
                    'barrio': 'Microcentro',
                    'precio': 80000.0,
                    'ambientes': 1,
                    'metros_cuadrados': 35.0,
                    'descripcion': 'Monoambiente totalmente equipado, listo para entrar',
                    'operacion': 'venta',
                    'tipo': 'departamento',
                    'direccion': 'Lavalle 800',
                    'antiguedad': 5,
                    'expensas': 3000.0,
                    'balcon': 'Sí',
                    'aire_acondicionado': 'Sí',
                    'moneda_precio': 'USD',
                    'moneda_expensas': 'ARS'
                },
                {
                    'id_temporal': 'prop_004',
                    'titulo': 'Oficina en Microcentro Superluminoso',
                    'barrio': 'Microcentro',
                    'precio': 120000.0,
                    'ambientes': 2,
                    'metros_cuadrados': 45.0,
                    'descripcion': 'Oficina luminosa con excelentes vistas, totalmente equipada',
                    'operacion': 'venta',
                    'tipo': 'oficina',
                    'direccion': 'Corrientes 1234',
                    'antiguedad': 3,
                    'expensas': 8000.0,
                    'aire_acondicionado': 'Sí',
                    'moneda_precio': 'USD',
                    'moneda_expensas': 'ARS'
                },
                {
                    'id_temporal': 'prop_005', 
                    'titulo': 'PH en Palermo',
                    'barrio': 'Palermo',
                    'precio': 350000.0,
                    'ambientes': 4,
                    'metros_cuadrados': 180.0,
                    'descripcion': 'PH con patio privado, excelente estado, mucha privacidad',
                    'operacion': 'venta',
                    'tipo': 'ph',
                    'direccion': 'Honduras 4500',
                    'antiguedad': 8,
                    'expensas': 7000.0,
                    'cochera': 'Sí',
                    'balcon': 'Sí',
                    'pileta': 'No',
                    'acepta_mascotas': 'Sí',
                    'moneda_precio': 'USD',
                    'moneda_expensas': 'ARS'
                }
            ]
            
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
                        prop['id_temporal'], prop['titulo'], prop['barrio'], prop['precio'],
                        prop['ambientes'], prop['metros_cuadrados'], prop['descripcion'],
                        prop['operacion'], prop['tipo'], prop.get('direccion'),
                        prop.get('antiguedad'), prop.get('expensas'), prop.get('cochera'),
                        prop.get('balcon'), prop.get('pileta'), prop.get('acepta_mascotas'),
                        prop.get('aire_acondicionado'), prop.get('moneda_precio', 'USD'),
                        prop.get('moneda_expensas', 'ARS')
                    ))
                    print(f"✅ Propiedad cargada: {prop['titulo']}")
                except Exception as e:
                    print(f"⚠️ Error cargando propiedad {prop['titulo']}: {e}")
            
            conn.commit()
            print(f"✅ Base de datos inicializada con {len(propiedades)} propiedades")
            
    except Exception as e:
        print(f"❌ Error crítico inicializando base de datos: {e}")

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