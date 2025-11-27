"""
"""
import os
import re
import json
import sqlite3
import requests
import time
from functools import lru_cache
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from config import API_KEYS, ENDPOINT, WORKING_MODEL as MODEL


# Después de las importaciones, agrega:
print(f"🔍 API Keys cargadas: {API_KEYS}")
print(f"🔍 Endpoint: {ENDPOINT}")

# Al inicio, después de las importaciones
print("🔍 TODAS LAS VARIABLES DE ENTORNO:")
for key, value in os.environ.items():
    if "GEMINI" in key or "API" in key:
        print(f"   {key}: {value}")



# 🔥 AGREGAR ESTO TEMPORALMENTE:
print("🔍 TODAS LAS VARIABLES DE ENTORNO RELACIONADAS:")
for key, value in os.environ.items():
    if "GEMINI" in key.upper() or "API" in key.upper() or "KEY" in key.upper():
        print(f"   {key}: {value[:20]}...")  # Mostrar solo primeros 20 chars

print("🔍 VARIABLE GEMINI_API_KEYS específica:")
print(f"   GEMINI_API_KEYS: {os.getenv('GEMINI_API_KEYS', 'NO DEFINIDA')}")

print("🔍 VARIABLE GEMINI_KEYS específica:")
print(f"   GEMINI_KEYS: {os.getenv('GEMINI_KEYS', 'NO DEFINIDA')}")



def call_gemini_with_rotation(prompt: str) -> str:
    import google.generativeai as genai
    
    print(f"🎯 INICIANDO ROTACIÓN DE CLAVES")
    print(f"🔧 Modelo: {MODEL}")
    print(f"🔑 Claves disponibles: {len(API_KEYS)}")
    
    for i, key in enumerate(API_KEYS):
        if not key.strip():
            continue
            
        print(f"🔄 Probando clave {i+1}/{len(API_KEYS)}...")
        
        try:
            genai.configure(api_key=key.strip())
            model = genai.GenerativeModel(MODEL)
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.8,
                    top_k=40,
                )
            )
            
            if not response.parts:
                raise Exception("Respuesta vacía de Gemini")
            
            answer = response.text.strip()
            print(f"✅ Éxito con clave {i+1}")
            
            return answer

        except Exception as e:
            error_type = type(e).__name__
            
            # 🔥 MENSAJES MÁS LIMPIOS
            if "ResourceExhausted" in error_type or "429" in str(e):
                print(f"❌ Clave {i+1} agotada")
            elif "PermissionDenied" in error_type or "401" in str(e):
                print(f"❌ Clave {i+1} no autorizada") 
            else:
                print(f"❌ Clave {i+1} error: {error_type}")
            
            continue
    
    return "❌ Todas las claves agotadas. Intente más tarde."

def diagnosticar_problemas():
    """Función de diagnóstico"""
    print("🔍 INICIANDO DIAGNÓSTICO...")
    
    # 1. Verificar archivos
    print("1. 📁 Verificando archivos...")
    archivos = os.listdir('.')
    print(f"   Archivos en directorio actual: {archivos}")
    
    # 2. Verificar properties.json
    if os.path.exists("properties.json"):
        try:
            with open("properties.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"   ✅ properties.json: {len(data)} propiedades encontradas")
        except Exception as e:
            print(f"   ❌ Error leyendo properties.json: {e}")
    else:
        print("   ❌ properties.json NO EXISTE")
    
    # 3. Verificar config
    try:
        from config import API_KEYS, ENDPOINT
        print(f"   ✅ Config: {len(API_KEYS)} API keys cargadas")
        print(f"   ✅ Endpoint: {ENDPOINT}")
    except Exception as e:
        print(f"   ❌ Error cargando config: {e}")
    
    # 4. Verificar gemini client
    try:
        from gemini.client import call_gemini_with_rotation
        print("   ✅ Gemini client importado correctamente")
    except Exception as e:
        print(f"   ❌ Error importando gemini client: {e}")

# Ejecutar diagnóstico inmediatamente
diagnosticar_problemas()



# ✅ MODELOS DE DATOS PYDANTIC
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Mensaje del usuario")
    channel: str = Field(default="web", description="Canal de comunicación (web, whatsapp, etc.)")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Filtros aplicados desde el frontend")
    contexto_anterior: Optional[Dict[str, Any]] = Field(default=None, description="Contexto de la conversación anterior")
    es_seguimiento: Optional[bool] = Field(default=False, description="Indica si es un mensaje de seguimiento")

class ChatResponse(BaseModel):
    response: str
    results_count: Optional[int] = None
    search_performed: bool
    propiedades: Optional[List[dict]] = None

class PropertyResponse(BaseModel):
    id_temporal: str
    titulo: str
    barrio: str
    precio: float
    ambientes: int
    metros_cuadrados: float
    descripcion: str
    operacion: str
    tipo: str
    direccion: Optional[str] = None
    antiguedad: Optional[int] = None
    estado: Optional[str] = None
    orientacion: Optional[str] = None
    expensas: Optional[float] = None
    amenities: Optional[str] = None
    cochera: Optional[str] = None
    balcon: Optional[str] = None
    pileta: Optional[str] = None
    acepta_mascotas: Optional[str] = None
    aire_acondicionado: Optional[str] = None
    info_multimedia: Optional[str] = None
    documentos: Optional[List[str]] = None
    videos: Optional[List[str]] = None
    fotos: Optional[List[str]] = None
    moneda_precio: Optional[str] = None
    moneda_expensas: Optional[str] = None
    fecha_procesamiento: Optional[str] = None


# ✅ MÉTRICAS Y ESTADÍSTICAS
class Metrics:
    def __init__(self):
        self.requests_count = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.gemini_calls = 0
        self.search_queries = 0
        self.start_time = time.time()
    
    def increment_requests(self):
        self.requests_count += 1
    
    def increment_success(self):
        self.successful_requests += 1
    
    def increment_failures(self):
        self.failed_requests += 1
    
    def increment_gemini_calls(self):
        self.gemini_calls += 1
    
    def increment_searches(self):
        self.search_queries += 1
    
    def get_uptime(self):
        return time.time() - self.start_time

# ✅ INICIALIZACIÓN
metrics = Metrics()

@asynccontextmanager
async def lifespan(app):
    print("🔄 Iniciando ciclo de vida...")
    # Inicialización de bases de datos y recursos
    initialize_databases()
    yield
    print("✅ Finalizando ciclo de vida...")

# ✅ APP PRINCIPAL
app = FastAPI(
    lifespan=lifespan,
    title="Dante Propiedades API",
    description="Backend para procesamiento de consultas y filtros de propiedades",
    version="1.0.0"
)

# ✅ CONFIGURACIONES
DB_PATH = os.path.join(os.path.dirname(__file__), "propiedades.db")
LOG_PATH = os.path.join(os.path.dirname(__file__), "conversaciones.db")
CACHE_DURATION = 300  # 5 minutos para cache

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CACHE PARA CONSULTAS FRECUENTES
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
    
    if cached and (time.time() - cached['timestamp']) < CACHE_DURATION:
        return cached['results']
    return None



# ✅ FUNCIONES MEJORADAS
def cargar_propiedades_a_db():
    """Carga las propiedades del JSON a la base de datos SQLite con mapeo correcto de campos y tipos"""
    try:
        propiedades = cargar_propiedades_json("properties.json")
        if not propiedades:
            print("❌ No hay propiedades para cargar")
            return
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        # Limpiar tabla existente
        cur.execute("DELETE FROM properties")
        
        propiedades_cargadas = 0
        for p in propiedades:
            try:
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
                    json.dumps(p.get('documentos')), json.dumps(p.get('videos')),
                    json.dumps(p.get('fotos')), p.get('moneda_precio'),
                    p.get('moneda_expensas'), p.get('fecha_procesamiento')
                ))
                propiedades_cargadas += 1
                
            except Exception as e:
                print(f"⚠️ Error cargando propiedad {p.get('titulo', 'N/A')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        conn.commit()
        conn.close()
        print(f"✅ {propiedades_cargadas}/{len(propiedades)} propiedades cargadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error cargando propiedades a DB: {e}")
        import traceback
        traceback.print_exc()


def initialize_databases():
    """Inicializa las bases de datos si no existen"""
    try:
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
            print("🗑️ Base de datos propiedades eliminada forzadamente")
        if os.path.exists(LOG_PATH):
            os.remove(LOG_PATH)
            print("🗑️ Base de datos logs eliminada forzadamente")
        
        # Base de datos de logs
        conn = sqlite3.connect(LOG_PATH)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                channel TEXT,
                user_message TEXT,
                bot_response TEXT,
                response_time REAL,
                search_performed BOOLEAN DEFAULT 0,
                results_count INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ Tabla 'logs' creada/verificada")
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS properties (
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
                fecha_procesamiento TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute("PRAGMA table_info(properties)")
        schema = cur.fetchall()
        print("🔍 Esquema de la tabla 'properties':")
        for col in schema:
            print(f"   {col[1]} : {col[2]}")
        
        conn.commit()
        conn.close()
        print("✅ Tabla 'properties' creada/verificada")

        cargar_propiedades_a_db()
        
        print("✅ Bases de datos inicializadas correctamente con nuevo esquema")
        
    except Exception as e:
        print(f"❌ Error inicializando bases de datos: {e}")
        import traceback
        traceback.print_exc()

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

def extraer_barrios(propiedades):
    return sorted(set(p.get("barrio", "").lower() for p in propiedades if p.get("barrio")))

def extraer_tipos(propiedades):
    return sorted(set(p.get("tipo", "").lower() for p in propiedades if p.get("tipo")))

def extraer_operaciones(propiedades):
    return sorted(set(p.get("operacion", "").lower() for p in propiedades if p.get("operacion")))

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

@lru_cache(maxsize=100)
def query_properties_cached(filters_json: str):
    """Versión cacheada de query_properties"""
    filters = json.loads(filters_json) if filters_json else {}
    return query_properties(filters)



def query_properties(filters=None):
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
        
        print(f"🔍 Query ejecutada: {q}")
        print(f"🔍 Parámetros: {params}")
        
        cur.execute(q, params)
        rows = cur.fetchall()
        conn.close()
        
        results = [dict(r) for r in rows]
        
        if results:
            print(f"✅ {len(results)} propiedades encontradas:")
        else:
            print("❌ No se encontraron propiedades con los filtros aplicados")
        
        if filters and results:
            cache_query_results(filters, results)
        
        return results
    except Exception as e:
        print(f"❌ Error en query_properties: {e}")
        return []
    
    

def build_prompt(user_text, results=None, filters=None, channel="web", style_hint="", property_details=None):
    whatsapp_tone = channel == "whatsapp"

    if property_details:
        details = "\n".join([f"- {key.replace('_', ' ').capitalize()}: {value}" for key, value in property_details.items()])
        return (
            style_hint + f"\n\nEl usuario está pidiendo más detalles sobre la propiedad '{property_details['titulo']}'. Aquí están todos los detalles de la propiedad:\n"
            + details
            + "\n\nRedactá una respuesta cálida y profesional que presente estos detalles de forma clara y atractiva. "
            "Ofrecé ayuda personalizada y sugerí continuar la conversación por WhatsApp. "
            "Cerrá con un agradecimiento y tono amable."
            + ("\nUsá emojis si el canal es WhatsApp." if whatsapp_tone else "")
        )
    
    if results is not None and results:
        bullets = [
            f"{r['titulo']} — {r['barrio']} — ${r['precio']:,.0f} — {r['ambientes']} amb — {r['metros_cuadrados']} m2"
            for r in results[:8]
        ]
        return (
            style_hint + f"\n\nEl usuario está buscando propiedades con los siguientes filtros: {filters}. Aquí hay resultados relevantes:\n"
            + "\n".join(bullets)
            + "\n\nRedactá una respuesta cálida y profesional que resuma los resultados, "
            "ofrezca ayuda personalizada y sugiera continuar la conversación por WhatsApp. "
            "Cerrá con un agradecimiento y tono amable."
            + ("\nUsá emojis si el canal es WhatsApp." if whatsapp_tone else "")
        )
    elif results is not None:
        return (
            f"{style_hint}\n\nEl usuario busca propiedades con estos filtros: {filters} pero no hay resultados. "
            "Redactá una respuesta amable que sugiera alternativas cercanas, pida más detalles "
            "y ofrezca continuar la conversación por WhatsApp. Cerrá con un agradecimiento."
            + ("\nUsá emojis si el canal es WhatsApp." if whatsapp_tone else "")
        )
    else:
        return (
            f"{style_hint}\n\nActuá como asistente inmobiliario para Dante Propiedades. "
            "Respondé la siguiente consulta de forma cálida, profesional y breve. "
            "Si es posible, ofrecé continuar por WhatsApp y agradecé el contacto."
            + ("\nUsá emojis si el canal es WhatsApp." if whatsapp_tone else "")
            + "\nConsulta: " + user_text
        )

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

def detect_filters(text_lower: str) -> Dict[str, Any]:
    """Detecta y extrae filtros del texto del usuario - VERSIÓN MEJORADA Y GENÉRICA"""
    import re
    filters = {}
    
    barrio_keywords = [
        'palermo', 'recoleta', 'belgrano', 'almagro', 'caballito',
        'microcentro', 'balvanera', 'villa crespo', 'san telmo', 'boca',
        'nuñez', 'monserrat', 'constitución', 'flores', 'parque chas',
        'villa urquiza', 'boedo', 'villa luro', 'villa devoto', 'villa soldati',
        'villa ramos mejía', 'liniers', 'mataderos', 'velez sarsfield', 'versalles',
        'paternal', 'chacarita', 'agronomia', 'villa pueyrredón', 'saavedra',
        'coghlan', 'belgrano r', 'belgrano c', 'nuñez', 'olivos', 'san isidro',
        'vicente lopez', 'puerto madero', 'colegiales', 'soho', 'barrio norte'
    ]
    
    operacion_keywords = {
        'alquiler': 'alquiler',
        'alquilar': 'alquiler', 
        'renta': 'alquiler',
        'venta': 'venta',
        'comprar': 'venta',
        'compra': 'venta',
        'vender': 'venta'
    }
    
    tipo_keywords = {
        'departamento': 'departamento',
        'depto': 'departamento',
        'casa': 'casa',
        'ph': 'ph',
        'casaquinta': 'casaquinta',
        'terreno': 'terreno',
        'terrenos': 'terreno',
        'lote': 'terreno',
        'lotes': 'terreno'
    }
    
    barrio_detectado = None
    
    for barrio in barrio_keywords:
        if barrio in text_lower:
            barrio_detectado = barrio
            break
    
    if not barrio_detectado:
        barrio_patterns = [
            r"en ([a-zA-Záéíóúñ\s]+)",
            r"barrio ([a-zA-Záéíóúñ\s]+)",
            r"zona ([a-zA-Záéíóúñ\s]+)",
            r"de ([a-zA-Záéíóúñ\s]+)$",
            r"el de ([a-zA-Záéíóúñ\s]+)",
            r"la de ([a-zA-Záéíóúñ\s]+)",
        ]
        
        for pattern in barrio_patterns:
            match = re.search(pattern, text_lower)
            if match:
                potential_barrio = match.group(1).strip().lower()
                if (
                    potential_barrio in barrio_keywords and 
                    potential_barrio not in operacion_keywords and
                    potential_barrio not in tipo_keywords
                ):
                    barrio_detectado = potential_barrio
                    break
    
    if barrio_detectado:
        filters["neighborhood"] = barrio_detectado
    
    for keyword, tipo in tipo_keywords.items():
        if keyword in text_lower:
            filters["tipo"] = tipo
            break
    
    for keyword, operacion in operacion_keywords.items():
        if keyword in text_lower:
            filters["operacion"] = operacion
            break
    
    precio_patterns = [
        r"hasta \$?\s*([0-9\.]+)",
        r"máximo \$?\s*([0-9\.]+)",
        r"precio.*?\$?\s*([0-9\.]+)",
        r"menos de \$?\s*([0-9\.]+)",
        r"\$?\s*([0-9\.]+)\s*pesos",
        r"de \$?\s*([0-9\.]+)",
        r"valor.*?\$?\s*([0-9\.]+)",
    ]
    
    for pattern in precio_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                precio = int(match.group(1).replace('.', ''))
                filters["max_price"] = precio
                break
            except ValueError:
                continue
    
    min_price_match = re.search(r"desde \$?\s*([0-9\.]+)", text_lower)
    if min_price_match:
        try:
            min_price = int(min_price_match.group(1).replace('.', ''))
            filters["min_price"] = min_price
        except ValueError:
            pass
    
    rooms_match = re.search(r"(\d+)\s*amb", text_lower)
    if rooms_match:
        filters["min_rooms"] = int(rooms_match.group(1))

    sqm_match = re.search(r"(\d+)\s*m2", text_lower) or re.search(r"(\d+)\s*metros", text_lower)
    if sqm_match:
        filters["min_sqm"] = int(sqm_match.group(1))

    return filters



# ✅ ENDPOINTS MEJORADOS
@app.get("/status")
def status():
    """Endpoint de estado del servicio"""
    test_prompt = "Respondé solo con OK"
    try:
        response = call_gemini_with_rotation(test_prompt)
        gemini_status = "OK" if "OK" in response else "ERROR"
    except Exception as e:
        gemini_status = f"ERROR: {str(e)}"
    
    return {
        "status": "activo",
        "gemini_api": gemini_status,
        "uptime_seconds": metrics.get_uptime(),
        "total_requests": metrics.requests_count,
        "successful_requests": metrics.successful_requests,
        "failed_requests": metrics.failed_requests,
        "gemini_calls": metrics.gemini_calls,
        "search_queries": metrics.search_queries
    }

@app.get("/")
def root():
    return {
        "status": "Backend activo",
        "endpoint": "/chat",
        "método": "POST",
        "uso": "Enviar mensaje como JSON: { message: '...', channel: 'web', filters: {...} }",
        "documentación": "/docs"
    }

@app.get("/logs")
def get_logs(limit: int = 10, channel: Optional[str] = None):
    """Obtiene logs de conversaciones con filtros opcionales"""
    try:
        conn = sqlite3.connect(LOG_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        if channel:
            cur.execute(
                "SELECT timestamp, channel, user_message, bot_response, response_time, search_performed, results_count FROM logs WHERE channel = ? ORDER BY id DESC LIMIT ?",
                (channel, limit)
            )
        else:
            cur.execute(
                "SELECT timestamp, channel, user_message, bot_response, response_time, search_performed, results_count FROM logs ORDER BY id DESC LIMIT ?",
                (limit,)
            )
        
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo logs: {str(e)}")

@app.get("/properties", response_model=List[PropertyResponse])
def get_properties(
    neighborhood: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rooms: Optional[int] = None,
    operacion: Optional[str] = None,
    tipo: Optional[str] = None,
    min_sqm: Optional[float] = None,
    max_sqm: Optional[float] = None,
    limit: int = 20
):
    """Endpoint directo para buscar propiedades con filtros"""
    filters = {}
    if neighborhood:
        filters["neighborhood"] = neighborhood
    if min_price is not None:
        filters["min_price"] = min_price
    if max_price is not None:
        filters["max_price"] = max_price
    if min_rooms is not None:
        filters["min_rooms"] = min_rooms
    if operacion:
        filters["operacion"] = operacion
    if tipo:
        filters["tipo"] = tipo
    if min_sqm is not None:
        filters["min_sqm"] = min_sqm
    if max_sqm is not None:
        filters["max_sqm"] = max_sqm
    
    results = query_properties(filters)
    return results[:limit]

@app.get("/debug")
def debug_info():
    """Endpoint de diagnóstico para producción"""
    info = {
        "directorio_actual": os.getcwd(),
        "archivos": os.listdir('.'),
        "existe_properties_json": os.path.exists("properties.json"),
        "existe_config_py": os.path.exists("config.py"),
        "variables_entorno": {
            "GEMINI_API_KEYS": "SET" if os.environ.get("GEMINI_API_KEYS") else "MISSING",
            "PORT": os.environ.get("PORT", "8000")
        },
        "base_datos": {
            "existe_db": os.path.exists(DB_PATH),
            "existe_logs": os.path.exists(LOG_PATH)
        }
    }
    
    if os.path.exists("properties.json"):
        try:
            with open("properties.json", "r", encoding="utf-8") as f:
                props = json.load(f)
                info["properties_json"] = f"{len(props)} propiedades"
        except Exception as e:
            info["properties_json"] = f"Error: {e}"
    
    return info




@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint principal para chat con el asistente inmobiliario"""
    start_time = time.time()
    metrics.increment_requests()
    
    try:
        user_text = request.message.strip()
        channel = request.channel.strip()
        filters_from_frontend = request.filters if request.filters else {}

        contexto_anterior = request.contexto_anterior if hasattr(request, 'contexto_anterior') else None
        es_seguimiento = request.es_seguimiento if hasattr(request, 'es_seguimiento') else False

        if not user_text:
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

        propiedades_json = cargar_propiedades_json("properties.json")
        barrios_disponibles = extraer_barrios(propiedades_json)
        tipos_disponibles = extraer_tipos(propiedades_json)
        operaciones_disponibles = extraer_operaciones(propiedades_json)
        
        historial = get_historial_canal(channel)
        contexto_historial = "\nHistorial reciente:\n" + "\n".join(f"- {m}" for m in historial) if historial else ""

        contexto_dinamico = (
            f"Barrios disponibles: {', '.join(barrios_disponibles)}.\n"
            f"Tipos de propiedad: {', '.join(tipos_disponibles)}.\n"
            f"Operaciones disponibles: {', '.join(operaciones_disponibles)}."
        )

        text_lower = user_text.lower()
        filters, results = {}, None
        search_performed = False
        property_details = None

        palabras_seguimiento_backend = [
            'más', 'mas', 'detalles', 'brindar', 'brindame', 'dime', 'cuéntame', 
            'cuentame', 'información', 'informacion', 'características', 'caracteristicas',
            'este', 'esta', 'ese', 'esa', 'primero', 'primera', 'segundo', 'segunda',
            'propiedad', 'departamento', 'casa', 'ph', 'casaquinta', 'terreno', 'terrenos'
        ]

        es_seguimiento_backend = any(palabra in text_lower for palabra in palabras_seguimiento_backend)
        es_seguimiento_final = es_seguimiento or es_seguimiento_backend

        if es_seguimiento_final and contexto_anterior and contexto_anterior.get('resultados'):
            propiedades_contexto = contexto_anterior['resultados']
            if propiedades_contexto:
                propiedad_especifica = None
                
                import re
                precio_pattern = r'(?:\$? \s*)?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\s*(?:mil|mil|k|K)?'
                match_precio = re.search(precio_pattern, user_text)
                
                if match_precio:
                    precio_texto = match_precio.group(1)
                    precio_limpio = precio_texto.replace('.', '').replace(',', '')
                    
                    try:
                        precio_buscado = int(precio_limpio)
                        for prop in propiedades_contexto:
                            if prop.get('precio') == precio_buscado:
                                propiedad_especifica = prop
                                break
                    except ValueError:
                        pass
                
                if not propiedad_especifica:
                    barrios = ["colegiales", "palermo", "boedo", "belgrano", "recoleta", "soho","almagro", "villa crespo", "san isidro", "vicente lopez"]
                    for barrio in barrios:
                        if barrio in user_text.lower():
                            for prop in propiedades_contexto:
                               if (barrio in prop.get('barrio', '').lower() or 
                                    barrio in prop.get('titulo', '').lower()):
                                    propiedad_especifica = prop
                                    break
                            if propiedad_especifica:
                                break

                if not propiedad_especifica:
                    tipos = ["departamento", "casa", "ph", "terreno"]
                    for tipo in tipos:
                        if tipo in user_text.lower():
                            for prop in propiedades_contexto:
                                if tipo in prop.get('tipo', '').lower():
                                    propiedad_especifica = prop
                                    break
                            if propiedad_especifica:
                                break

                if not propiedad_especifica:
                    if any(word in user_text.lower() for word in ['primero', 'primera', '1']):
                        propiedad_especifica = propiedades_contexto[0]
                    elif any(word in user_text.lower() for word in ['segundo', 'segunda', '2']) and len(propiedades_contexto) > 1:
                        propiedad_especifica = propiedades_contexto[1]
                    elif any(word in user_text.lower() for word in ['tercero', 'tercera', '3']) and len(propiedades_contexto) > 2:
                        propiedad_especifica = propiedades_contexto[2]

                if not propiedad_especifica and propiedades_contexto:
                    propiedad_especifica = propiedades_contexto[0]
                
                property_details = propiedad_especifica
              
        elif any(keyword in text_lower for keyword in [
            "más información", "mas informacion", "más detalles", "mas detalles", 
            "brindar", "dime más", "cuéntame más", "información del", "detalles del",
            "primero", "primera", "este", "esta", "ese", "esa", "el de", "la de"
        ]):
            if contexto_anterior and contexto_anterior.get('resultados'):
                propiedades_contexto = contexto_anterior['resultados']              
                if propiedades_contexto:
                    propiedad_especifica = None
                    import re
                    
                    precio_pattern = r'(?:\$? \s*)?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?)\s*(?:mil|mil|k|K)?'
                    match_precio = re.search(precio_pattern, user_text)
                    
                    if match_precio:
                        precio_texto = match_precio.group(1)
                        precio_limpio = precio_texto.replace('.', '').replace(',', '')
                        
                        try:
                            precio_buscado = int(precio_limpio)
                            for prop in propiedades_contexto:
                                if prop.get('precio') == precio_buscado:
                                    propiedad_especifica = prop
                                    break
                        except ValueError:
                            pass
                   
                    if not propiedad_especifica:
                        barrios = ["colegiales", "palermo", "soho","boedo", "belgrano", "recoleta", "almagro", "villa crespo", "san isidro", "vicente lopez"]
                        for barrio in barrios:
                            if barrio in user_text.lower():
                                for prop in propiedades_contexto:
                                    if (barrio in prop.get('barrio', '').lower() or 
                                        barrio in prop.get('titulo', '').lower()):
                                        propiedad_especifica = prop
                                        break
                                if propiedad_especifica:
                                    break

                    elif not propiedad_especifica:
                        tipos = ["departamento", "casa", "ph", "terreno"]
                        for tipo in tipos:
                            if tipo in user_text.lower():
                                for prop in propiedades_contexto:
                                    if tipo in prop.get('tipo', '').lower():
                                        propiedad_especifica = prop
                                        break
                                if propiedad_especifica:
                                    break

                    if not propiedad_especifica:
                        if any(word in user_text.lower() for word in ['primero', 'primera', '1']):
                            propiedad_especifica = propiedades_contexto[0]
                        elif any(word in user_text.lower() for word in ['segundo', 'segunda', '2']) and len(propiedades_contexto) > 1:
                            propiedad_especifica = propiedades_contexto[1]
                        elif any(word in user_text.lower() for word in ['tercero', 'tercera', '3']) and len(propiedades_contexto) > 2:
                            propiedad_especifica = propiedades_contexto[2]

                    if not propiedad_especifica and propiedades_contexto:
                        propiedad_especifica = propiedades_contexto[0]
                    
                    property_details = propiedad_especifica
            else:
                if historial:
                    last_bot_response = get_last_bot_response(channel)
                    if last_bot_response:
                        match = re.search(r"\* \*\*(.*?):\*\*", last_bot_response)
                        if match:
                            property_title = match.group(1)
                            conn = sqlite3.connect(DB_PATH)
                            conn.row_factory = sqlite3.Row
                            cur = conn.cursor()
                            cur.execute("SELECT * FROM properties WHERE titulo = ?", (property_title,))
                            row = cur.fetchone()
                            if row:
                                property_details = dict(row)
                            conn.close()

        if filters_from_frontend:
            filters.update(filters_from_frontend)
        
        detected_filters = detect_filters(text_lower)
        if detected_filters:
            filters.update(detected_filters)

        if filters and not property_details and not (es_seguimiento_final and contexto_anterior):
            search_performed = True
            metrics.increment_searches()
            results = query_properties(filters)
        else:
            if contexto_anterior and contexto_anterior.get('resultados'):
                results = contexto_anterior['resultados']
                search_performed = True
        
        if channel == "whatsapp":
            style_hint = "Respondé de forma breve, directa y cálida como si fuera un mensaje de WhatsApp."
        else:
            style_hint = "Respondé de forma explicativa, profesional y cálida como si fuera una consulta web."

        if es_seguimiento_final and (contexto_anterior or property_details):
            if property_details:
                detalles_propiedad = f"""
        PROPIEDAD ESPECÍFICA:
        - Título: {property_details.get('titulo', 'N/A')}
        - Precio: ${property_details.get('precio', 'N/A')}
        - Barrio: {property_details.get('barrio', 'N/A')}
        - Ambientes: {property_details.get('ambientes', 'N/A')}
        - Metros: {property_details.get('metros_cuadrados', 'N/A')}m²
        - Operación: {property_details.get('operacion', 'N/A')}
        - Tipo: {property_details.get('tipo', 'N/A')}
        - Descripción: {property_details.get('descripcion', 'N/A')}
        - Dirección: {property_details.get('direccion', 'N/A')}
        - Antigüedad: {property_details.get('antiguedad', 'N/A')}
        - Amenities: {property_details.get('amenities', 'N/A')}
        - Cochera: {property_details.get('cochera', 'N/A')}
        - Balcón: {property_details.get('balcon', 'N/A')}
        - Aire acondicionado: {property_details.get('aire_acondicionado', 'N/A')}
        - Expensas: {property_details.get('expensas', 'N/A')}
        - Estado: {property_details.get('estado', 'N/A')}
        """
                
                prompt = f"""
        ERES UN ASISTENTE INMOBILIARIO. El usuario está preguntando específicamente sobre ESTA propiedad:

        {detalles_propiedad}

        PREGUNTA DEL USUARIO: "{user_text}"

        INSTRUCCIONES ESTRICTAS:
        1. Responde EXCLUSIVAMENTE sobre esta propiedad específica
        2. Proporciona TODOS los detalles disponibles listados arriba
        3. NO menciones otras propiedades
        4. NO hagas preguntas adicionales al usuario
        5. Si faltan datos, menciona "No disponible" para ese campo
        6. {style_hint}

        RESPONDE DIRECTAMENTE CON TODOS LOS DETALLES DE ESTA PROPIEDAD:
        """
            
            else:
                prompt = build_prompt(user_text, results, filters, channel, style_hint + "\n" + contexto_dinamico + "\n" + contexto_historial, property_details)

        else:
            prompt = build_prompt(user_text, results, filters, channel, style_hint + "\n" + contexto_dinamico + "\n" + contexto_historial, property_details)
            
        metrics.increment_gemini_calls()
        answer = call_gemini_with_rotation(prompt)
        
        response_time = time.time() - start_time
        log_conversation(user_text, answer, channel, response_time, search_performed, len(results) if results else 0)
        metrics.increment_success()
        
        return ChatResponse(
            response=answer,
            results_count=len(results) if results else None,
            search_performed=search_performed,
            propiedades=results if results else (contexto_anterior.get('resultados') if contexto_anterior else None)
        )
    
    except HTTPException:
        metrics.increment_failures()
        raise
    except Exception as e:
        metrics.increment_failures()
        error_type = type(e).__name__
        print(f"❌ ERROR en endpoint /chat: {error_type}: {str(e)}")
        
        error_message = "⚠️ Ocurrió un error procesando tu consulta. Por favor, intentá nuevamente en unos momentos."
        
        return ChatResponse(
            response=error_message,
            search_performed=False,
            propiedades=None
        )
        
        
@app.get("/metrics")
def get_metrics():
    """Endpoint para obtener métricas del servicio"""
    return {
        "uptime_seconds": metrics.get_uptime(),
        "requests_per_second": metrics.requests_count / max(metrics.get_uptime(), 1),
        "success_rate": metrics.successful_requests / max(metrics.requests_count, 1),
        "total_requests": metrics.requests_count,
        "successful_requests": metrics.successful_requests,
        "failed_requests": metrics.failed_requests,
        "gemini_calls": metrics.gemini_calls,
        "search_queries": metrics.search_queries,
        "cache_size": len(query_cache)
    }

@app.delete("/cache")
def clear_cache():
    """Limpia el cache de consultas"""
    query_cache.clear()
    query_properties_cached.cache_clear()
    return {"message": "Cache limpiado correctamente"}

# ✅ DOCUMENTACIÓN PERSONALIZADA
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Dante Propiedades API",
        version="1.0.0",
        description="Backend para procesamiento de consultas y filtros de propiedades con IA",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# ✅ INICIO
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 INICIANDO EN MODO PRODUCCIÓN/RENDER")
    print(f"🔍 Directorio: {os.getcwd()}")
    print(f"🔍 Archivos: {os.listdir('.')}")
    
    # Diagnóstico completo
    diagnosticar_problemas()
    
    port = int(os.environ.get("PORT", 8000))
    print(f"🎯 Servidor iniciando en puerto: {port}")
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=False,
        access_log=True
    )
