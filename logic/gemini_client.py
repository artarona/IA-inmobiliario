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

    if property_details:
        detalles = f"""
Título: {property_details.get('titulo', 'N/A')}
Barrio: {property_details.get('barrio', 'N/A')}
Precio: {property_details.get('moneda_precio', 'USD')} {property_details.get('precio', 'N/A'):,}
Ambientes: {property_details.get('ambientes', 'N/A')}
Metros cuadrados: {property_details.get('metros_cuadrados', 'N/A')}m²
Operación: {property_details.get('operacion', 'N/A')}
Tipo: {property_details.get('tipo', 'N/A')}
Descripción: {property_details.get('descripcion', 'N/A')}
Dirección: {property_details.get('direccion', 'N/A')}
Antigüedad: {property_details.get('antiguedad', 'N/A')} años
Expensas: {property_details.get('moneda_expensas', 'ARS')} {property_details.get('expensas', 'N/A')}
Amenities: {property_details.get('amenities', 'N/A')}
Cochera: {property_details.get('cochera', 'No')}
Balcón: {property_details.get('balcon', 'No')}
Pileta: {property_details.get('pileta', 'No')}
Aire acondicionado: {property_details.get('aire_acondicionado', 'No')}
Acepta mascotas: {property_details.get('acepta_mascotas', 'No')}
"""
        return (
            style_hint + f"\n\nEl usuario está pidiendo más detalles sobre una propiedad específica:\n"
            + detalles
            + "\n\nRedactá una respuesta cálida y profesional que presente estos detalles de forma clara. "
            "Destacá las características más importantes según el tipo de propiedad."
            + ("\nUsá emojis si el canal es WhatsApp." if whatsapp_tone else "")
        )
    
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
        for i, r in enumerate(results[:6]):
            emoji = property_emojis.get(r.get('tipo', '').lower(), '🏠')
            moneda = r.get('moneda_precio', 'USD')
            precio = f"{moneda} {r['precio']:,}" if r['precio'] > 0 else "Consultar"
            
            property_info = f"{emoji} **{r['titulo']}**\n"
            property_info += f"   • 📍 {r['barrio']}\n"
            property_info += f"   • 💰 {precio}\n"
            property_info += f"   • 🏠 {r['ambientes']} amb | {r['metros_cuadrados']} m²\n"
            property_info += f"   • 📋 {r['operacion'].title()} | {r['tipo'].title()}"
            
            if r.get('descripcion'):
                desc = r['descripcion'][:60] + '...' if len(r.get('descripcion', '')) > 60 else r['descripcion']
                property_info += f"\n   • 📝 {desc}"
            
            properties_list.append(property_info)
        
        properties_formatted = "\n\n".join(properties_list)
        
        return (
            style_hint + f"\n\n👋 ¡Hola! Encontré estas propiedades que podrían interesarte:\n\n"
            + properties_formatted
            + "\n\n💡 **Para refinar la búsqueda, podés:**\n"
            + "- Especificar el tipo de propiedad (casa, depto, terreno, oficina)\n"
            + "- Indicar el rango de precio en USD o pesos\n" 
            + "- Elegir la zona o barrio preferido\n"
            + "- Decir la cantidad de ambientes necesarios\n\n"
            + "¿Te interesa alguna en particular? Podés pedir más detalles."
            + ("\nUsá emojis para hacerlo más amigable." if whatsapp_tone else "")
        )
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