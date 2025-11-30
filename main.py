"""
Backend para Dante Propiedades - Asistente Inmobiliario con IA
"""
import os
import re
import json
import time
from functools import lru_cache
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.openapi.utils import get_openapi
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

# Importar lógica de negocio
from logic.database import (
    initialize_databases,
    verificar_y_reparar_bd,
    query_properties,
    get_historial_canal,
    get_last_bot_response,
    log_conversation,
    DB_PATH,
    LOG_PATH
)
from logic.filters import detect_filters
from logic.gemini_client import call_gemini_with_rotation, build_prompt
from logic.filter_data import BARRIOS, OPERACIONES, TIPOS

# ✅ INICIALIZACIÓN Y CONFIGURACIÓN
verificar_y_reparar_bd()
CACHE_DURATION = 300  # 5 minutos para cache

class Metrics:
    def __init__(self):
        self.requests_count = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.gemini_calls = 0
        self.search_queries = 0
        self.start_time = time.time()
    
    def increment_requests(self): self.requests_count += 1
    def increment_success(self): self.successful_requests += 1
    def increment_failures(self): self.failed_requests += 1
    def increment_gemini_calls(self): self.gemini_calls += 1
    def increment_searches(self): self.search_queries += 1
    def get_uptime(self): return time.time() - self.start_time

metrics = Metrics()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Iniciando ciclo de vida de la aplicación...")
    initialize_databases()
    yield
    print("✅ Finalizando ciclo de vida de la aplicación.")

# ✅ APP PRINCIPAL
app = FastAPI(
    lifespan=lifespan,
    title="Dante Propiedades API",
    description="Backend para procesamiento de consultas y filtros de propiedades con IA.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CACHE
query_cache = {}

def get_cache_key(filters: Dict[str, Any]) -> str:
    return json.dumps(filters, sort_keys=True)

def cache_query_results(filters: Dict[str, Any], results: List[Dict]):
    cache_key = get_cache_key(filters)
    query_cache[cache_key] = {'results': results, 'timestamp': time.time()}

def get_cached_results(filters: Dict[str, Any]) -> Optional[List[Dict]]:
    cache_key = get_cache_key(filters)
    cached = query_cache.get(cache_key)
    if cached and (time.time() - cached['timestamp']) < CACHE_DURATION:
        return cached['results']
    return None

@lru_cache(maxsize=100)
def query_properties_cached(filters_json: str):
    filters = json.loads(filters_json) if filters_json else {}
    return query_properties(filters)

# ✅ MODELOS DE DATOS
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    channel: str = Field(default="web")
    filters: Optional[Dict[str, Any]] = None
    contexto_anterior: Optional[Dict[str, Any]] = None
    es_seguimiento: Optional[bool] = False

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

# ✅ ENDPOINTS
@app.get("/")
def root():
    return FileResponse("index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    start_time = time.time()
    metrics.increment_requests()
    
    try:
        user_text = request.message.strip()
        if not user_text:
            raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")

        channel = request.channel.strip()
        filters_from_frontend = request.filters or {}
        contexto_anterior = request.contexto_anterior
        es_seguimiento = request.es_seguimiento

        text_lower = user_text.lower()
        filters = filters_from_frontend.copy()
        detected_filters = detect_filters(text_lower)
        filters.update(detected_filters)

        # ✅ AGREGAR DIAGNÓSTICO AQUÍ
        print(f"🎯 CONSULTA USUARIO: '{user_text}'")
        print(f"🔍 FILTROS DETECTADOS: {detected_filters}")
        print(f"🔍 FILTROS FRONTEND: {filters_from_frontend}")
        print(f"🔍 FILTROS COMBINADOS: {filters}")

        results = None
        search_performed = False
        
        if filters:
            search_performed = True
            metrics.increment_searches()
            results = query_properties(filters)
            print(f"📊 RESULTADOS OBTENIDOS: {len(results) if results else 0} propiedades")

        historial = get_historial_canal(channel)
        contexto_historial = "\nHistorial reciente:\n" + "\n".join(f"- {m}" for m in historial) if historial else ""
        
        contexto_dinamico = (
            f"Barrios disponibles: {', '.join(BARRIOS)}.\n"
            f"Tipos de propiedad: {', '.join(TIPOS)}.\n"
            f"Operaciones disponibles: {', '.join(OPERACIONES)}."
        )

        style_hint = "Respondé de forma breve, directa y cálida como si fuera un mensaje de WhatsApp." if channel == "whatsapp" else "Respondé de forma explicativa, profesional y cálida como si fuera una consulta web."
        
        prompt = build_prompt(user_text, results, filters, channel, f"{style_hint}\n{contexto_dinamico}\n{contexto_historial}")
        
        metrics.increment_gemini_calls()
        answer = call_gemini_with_rotation(prompt)
        
        response_time = time.time() - start_time
        log_conversation(user_text, answer, channel, response_time, search_performed, len(results) if results else 0)
        metrics.increment_success()
        
        # ✅ AGREGAR DIAGNÓSTICO DE RESPUESTA AQUÍ
        response_data = ChatResponse(
            response=answer,
            results_count=len(results) if results is not None else None,
            search_performed=search_performed,
            propiedades=results
        )
        
        print(f"📤 ENVIANDO RESPUESTA AL FRONTEND:")
        print(f"   📝 Respuesta: {answer[:100]}...")
        print(f"   📊 Resultados: {len(results) if results else 0} propiedades")
        print(f"   🔍 Búsqueda realizada: {search_performed}")
        if results:
            for i, prop in enumerate(results[:2]):
                print(f"   🏠 Prop {i+1}: {prop['titulo']} - {prop['operacion']}")
        
        return response_data
    
    except Exception as e:
        metrics.increment_failures()
        print(f"❌ ERROR en endpoint /chat: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail="Ocurrió un error procesando tu consulta.")


@app.get("/filters")
def get_all_filters():
    """Endpoint para obtener filtros estáticos desde filter_data."""
    return {
        "operaciones": OPERACIONES,
        "tipos": TIPOS,
        "barrios": BARRIOS
    }

@app.get("/properties", response_model=List[PropertyResponse])
def get_properties_endpoint(
    neighborhood: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None,
    min_rooms: Optional[int] = None, operacion: Optional[str] = None, tipo: Optional[str] = None,
    min_sqm: Optional[float] = None, max_sqm: Optional[float] = None, limit: int = 20
):
    filters = {k: v for k, v in locals().items() if v is not None and k != 'limit'}
    results = query_properties(filters)
    print(f"📊 RESULTADOS OBTENIDOS: {len(results) if results else 0} propiedades")
    return results[:limit]

@app.get("/status")
def status():
    return {
        "status": "activo",
        "uptime_seconds": metrics.get_uptime(),
        "total_requests": metrics.requests_count,
        "gemini_calls": metrics.gemini_calls,
        "search_queries": metrics.search_queries
    }

# ✅ INICIO
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)  # reload=False en producción