import os
import google.generativeai as genai
from typing import Optional, Dict, Any, List

# ✅ CONFIGURACIÓN GLOBAL
print("=" * 50)
print("🔍 INICIALIZANDO GEMINI CLIENT")
print("=" * 50)

# Cargar API keys
API_KEYS = []
for i in range(1, 4):
    key_name = f"GEMINI_API_KEY_{i}"
    key_value = os.environ.get(key_name)
    if key_value and key_value.strip():
        API_KEYS.append(key_value.strip())
        print(f"✅ {key_name}: Cargada correctamente")

MODEL = os.environ.get("WORKING_MODEL", "gemini-2.0-flash-001")

print(f"🎯 CONFIGURACIÓN FINAL: Modelo={MODEL}, Claves={len(API_KEYS)}")
print("=" * 50)

def call_gemini_with_rotation(prompt: str) -> str:
    """Función para llamar a Gemini API con rotación de claves"""
    print(f"🎯 INICIANDO ROTACIÓN DE CLAVES")
    print(f"🔧 Modelo: {MODEL}")
    print(f"🔑 Claves disponibles: {len(API_KEYS)}")
    
    if not API_KEYS:
        print("⚠️ No hay API keys configuradas, usando modo básico")
        return get_fallback_response()
    
    for i, key in enumerate(API_KEYS):
        try:
            print(f"🔄 Probando clave {i+1}/{len(API_KEYS)}...")
            
            # ✅ CONFIGURACIÓN EXPLÍCITA
            genai.configure(
                api_key=key,
                transport='rest',  # Forzar transporte REST
            )
            
            model = genai.GenerativeModel(MODEL)
            
            # ✅ LLAMADA MÁS SIMPLE PARA DIAGNÓSTICO
            print(f"   📝 Prompt length: {len(prompt)} caracteres")
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000,
                )
            )
            
            print(f"   ✅ Respuesta recibida, partes: {len(response.parts) if response.parts else 0}")
            
            if not response.parts:
                raise Exception("Respuesta vacía de Gemini")
            
            answer = response.text.strip()
            print(f"✅ Éxito con clave {i+1}")
            print(f"   📄 Respuesta: {answer[:100]}...")
            return answer

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            print(f"❌ ERROR Clave {i+1}:")
            print(f"   🏷️  Tipo: {error_type}")
            print(f"   📄 Mensaje: {error_msg}")
            
            # Detectar tipo de error específico
            if "429" in error_msg:
                print(f"   💡 Clave {i+1} agotada (rate limit)")
            elif "401" in error_msg or "PermissionDenied" in error_type or "API_KEY_INVALID" in error_msg:
                print(f"   💡 Clave {i+1} no autorizada/inválida")
            elif "quota" in error_msg.lower():
                print(f"   💡 Clave {i+1} sin quota")
            elif "503" in error_msg or "500" in error_msg:
                print(f"   💡 Error del servidor Gemini")
            elif "network" in error_msg.lower() or "connection" in error_msg.lower():
                print(f"   💡 Error de conexión")
            
            continue
    
    print("💥 TODAS las claves fallaron - usando modo básico")
    return get_fallback_response()

def get_fallback_response():
    """Respuesta de fallback cuando Gemini no funciona"""
    return "🤖 **Dante Propiedades**\n\n¡Hola! La aplicación está funcionando pero hay un problema temporal con el servicio de IA.\n\n**Sistema disponible:**\n✅ Búsqueda de propiedades\n✅ Filtros por barrio, precio, tipo\n✅ Base de datos cargada\n\n⚠️ **El modo conversacional IA está temporalmente desactivado.**\n\n**Cómo usar:**\n1. Escribí tu búsqueda (ej: \"departamento en palermo\")\n2. La app encontrará propiedades relevantes\n3. Usá los filtros para refinar resultados\n\n🏠 **¡La búsqueda de propiedades funciona perfectamente!**"

# ... (el resto de build_prompt permanece igual)
def build_prompt(user_text, results=None, filters=None, channel="web", style_hint="", property_details=None):
    whatsapp_tone = channel == "whatsapp"

    # ✅ FORZAR QUE LA IA LISTE LAS PROPIEDADES EN SU RESPUESTA
    if results is not None and results:
        property_emojis = {
            'casa': '🏠',
            'departamento': '🏢', 
            'ph': '🏡',
            'terreno': '📐',
            'oficina': '🏢',
            'casaquinta': '🏘️'
        }
        
        properties_list = []
        for i, r in enumerate(results[:6]):  # Mostrar máximo 6 propiedades
            emoji = property_emojis.get(r.get('tipo', '').lower(), '🏠')
            moneda = r.get('moneda_precio', 'USD')
            precio = f"{moneda} {r['precio']:,}" if r['precio'] > 0 else "Consultar"
            
            property_info = f"{emoji} **{r['titulo']}**\n"
            property_info += f"📍 {r['barrio']} | 💰 {precio}\n"
            property_info += f"🏠 {r['ambientes']} amb | 📏 {r['metros_cuadrados']} m²\n"
            property_info += f"📋 {r['operacion'].title()} | {r['tipo'].title()}"
            
            if r.get('descripcion'):
                desc = r['descripcion'][:80] + '...' if len(r.get('descripcion', '')) > 80 else r['descripcion']
                property_info += f"\n📝 {desc}"
            
            properties_list.append(property_info)
        
        properties_formatted = "\n\n".join(properties_list)
        
        # ✅ PROMPT MEJORADO - La IA DEBE incluir las propiedades en su respuesta
        return (
            f"El usuario busca: '{user_text}'\n\n"
            f"ENCONTRÉ {len(results)} PROPIEDADES que coinciden. "
            f"**DEBES MOSTRAR ESTAS PROPIEDADES EN TU RESPUESTA:**\n\n"
            f"{properties_formatted}\n\n"
            f"Instrucciones para tu respuesta:\n"
            f"1. Comienza saludando cálidamente\n"
            f"2. MENCIONA que encontraste {len(results)} propiedades\n"  
            f"3. LISTA todas las propiedades mostradas arriba\n"
            f"4. Ofrece ayuda para más detalles\n"
            f"5. Mantén un tono {'cercano con emojis' if whatsapp_tone else 'profesional'}\n\n"
            f"¡NO omitas la lista de propiedades en tu respuesta!"
        )
    
    # ... (el resto del código para otros casos permanece igual)
    
    elif results is not None:
        return (
            f"{style_hint}\n\n👋 ¡Hola! Gracias por contactarnos.\n\n"
            f"🔍 No encontré propiedades que coincidan exactamente con tu búsqueda, pero podemos ajustar los filtros.\n\n"
            f"💡 **Sugerencias para mejorar la búsqueda:**\n"
            f"- Probá con un rango de precio más amplio\n"
            f"- Considerá barrios cercanos\n"
            f"- Revisá otros tipos de propiedad\n\n"
            f"¿Querés que ajuste algún parámetro en particular?"
            + ("\n😊 Usá emojis para hacerlo más cercano." if whatsapp_tone else "")
        )
    
    # Prompt para consultas generales
    return (
        f"{style_hint}\n\n"
        f"El usuario pregunta: \"{user_text}\"\n\n"
        f"Contexto inmobiliario:\n"
        f"- Barrios disponibles: {', '.join(['Palermo', 'Recoleta', 'Belgrano', 'Caballito', 'Almagro', 'Villa Crespo', 'Colegiales', 'Nuñez'])}\n"
        f"- Tipos: casa, departamento, PH, terreno, oficina\n"
        f"- Operaciones: venta, alquiler\n"
        f"- Precios en USD y ARS\n\n"
        f"Respondé de forma útil y profesional, ofreciendo ayuda con búsquedas de propiedades."
        + ("\nUsá un tono cercano con emojis apropiados." if whatsapp_tone else "")
    )