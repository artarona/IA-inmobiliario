import pandas as pd
import json
import re
from datetime import datetime

def excel_a_json_avanzado(archivo_excel, archivo_salida='properties.json'):
    """
    Versión mejorada para convertir Excel a JSON con mejor manejo de datos
    """
    
    try:
        # Leer el archivo Excel
        df = pd.read_excel(archivo_excel)
        
        print(f"✅ Excel leído correctamente: {len(df)} registros encontrados")
        
    except Exception as e:
        print(f"❌ Error leyendo el archivo Excel: {e}")
        return None
    
    # Limpiar nombres de columnas
    df.columns = [limpiar_nombre_columna(col) for col in df.columns]
    
    propiedades = []
    
    for index, row in df.iterrows():
        try:
            propiedad = procesar_fila(row)
            if propiedad:  # Solo agregar si se procesó correctamente
                propiedades.append(propiedad)
        except Exception as e:
            print(f"⚠️ Error procesando fila {index}: {e}")
            continue
    
    # Guardar JSON
    try:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(propiedades, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON guardado exitosamente: {archivo_salida}")
        print(f"📊 Total de propiedades procesadas: {len(propiedades)}")
        
    except Exception as e:
        print(f"❌ Error guardando JSON: {e}")
        return None
    
    return propiedades

def limpiar_nombre_columna(nombre):
    """Limpia y estandariza nombres de columnas"""
    if pd.isna(nombre):
        return "columna_desconocida"
    
    nombre_limpio = str(nombre).lower().strip()
    nombre_limpio = re.sub(r'[^\w\s]', '_', nombre_limpio)  # Reemplazar caracteres especiales
    nombre_limpio = re.sub(r'\s+', '_', nombre_limpio)  # Reemplazar espacios múltiples
    return nombre_limpio

def procesar_fila(fila):
    """Procesa una fila individual del DataFrame"""
    propiedad = {}
    
    for columna, valor in fila.items():
        if pd.notna(valor) and valor != '':
            propiedad[columna] = limpiar_valor(valor, columna)
    
    # Enriquecer con datos extraídos
    propiedad = enriquecer_propiedad(propiedad)

    # Manejar campos de listas (fotos, videos, documentos)
    for campo_lista in ['fotos', 'videos', 'documentos']:
        if campo_lista in propiedad and isinstance(propiedad[campo_lista], str):
            propiedad[campo_lista] = [item.strip() for item in propiedad[campo_lista].split(',')]
        elif campo_lista not in propiedad:
            propiedad[campo_lista] = []
    
    return propiedad

def limpiar_valor(valor, nombre_columna):
    """Limpia y convierte valores según el tipo de columna"""
    
    # Columnas que deben ser numéricas
    columnas_numericas = ['precio', 'precio_usd', 'metros', 'metros_cuadrados', 
                         'superficie', 'ambientes', 'habitaciones', 'dormitorios', 
                         'banos', 'antiguedad']
    
    # Columnas que deben ser texto
    columnas_texto = ['descripcion', 'direccion', 'barrio', 'localidad', 
                     'ciudad', 'operacion', 'tipo', 'caracteristicas']
    
    nombre_columna_lower = nombre_columna.lower()
    
    # Si es numérico
    if any(col in nombre_columna_lower for col in columnas_numericas):
        return convertir_a_numero(valor)
    
    # Si es texto
    elif any(col in nombre_columna_lower for col in columnas_texto):
        return str(valor).strip()
    
    # Por defecto, mantener el valor original pero limpiarlo
    else:
        if isinstance(valor, str):
            return valor.strip()
        return valor

def convertir_a_numero(valor):
    """Convierte un valor a número, manejando diferentes formatos"""
    if isinstance(valor, (int, float)):
        return valor
    
    if isinstance(valor, str):
        # Remover símbolos de moneda, espacios, etc.
        valor_limpio = re.sub(r'[^\d.,]', '', valor.strip())
        
        # Reemplazar coma por punto para decimales
        valor_limpio = valor_limpio.replace(',', '.')
        
        try:
            if '.' in valor_limpio:
                return float(valor_limpio)
            else:
                return int(valor_limpio)
        except ValueError:
            return valor  # Devolver original si no se puede convertir
    
    return valor

def enriquecer_propiedad(propiedad):
    """Enriquece la propiedad con datos extraídos y metadatos"""
    
    # Extraer de descripción si existe
    if any(key in propiedad for key in ['descripcion', 'descripción', 'caracteristicas']):
        descripcion = next((propiedad[key] for key in ['descripcion', 'descripción', 'caracteristicas'] 
                           if key in propiedad and isinstance(propiedad[key], str)), "")
        
        if descripcion:
            propiedad['caracteristicas_extraidas'] = extraer_caracteristicas_avanzadas(descripcion)
    
    # Estandarizar campos clave
    propiedad = estandarizar_campos_clave(propiedad)
    
    # Agregar metadatos
    propiedad['fecha_procesamiento'] = datetime.now().isoformat()
    propiedad['id_temporal'] = f"prop_{hash(str(propiedad)) % 10000:04d}"
    
    return propiedad

def extraer_caracteristicas_avanzadas(texto):
    """Extrae características específicas del texto usando expresiones regulares"""
    if not isinstance(texto, str):
        return {}
    
    texto_lower = texto.lower()
    caracteristicas = {}
    
    # Patrones para extraer información
    patrones = {
        'ambientes': r'(\d+)\s*(?:amb|ambiente|ambientes|habitaciones|hab)',
        'banos': r'(\d+)\s*(?:baño|baños|banio|banios)',
        'metros_cuadrados': r'(\d+)\s*m²|\s*(\d+)\s*metros?',
        'antiguedad': r'(\d+)\s*(?:año|años|antigüedad)',
    }
    
    for clave, patron in patrones.items():
        match = re.search(patron, texto_lower)
        if match:
            # Tomar el primer grupo que no sea None
            valor = next((g for g in match.groups() if g is not None), None)
            if valor:
                try:
                    caracteristicas[clave] = int(valor)
                except ValueError:
                    pass
    
    # Características booleanas
    bool_caracteristicas = {
        'pileta': ['pileta', 'piscina'],
        'balcon': ['balcón', 'balcon'],
        'terraza': ['terraza'],
        'cochera': ['cochera', 'garaje', 'garage'],
        'jardin': ['jardín', 'jardin'],
        'amueblado': ['amueblado', 'amueblada'],
        'aire_acondicionado': ['aire acondicionado', 'aire_acondicionado', 'aa'],
        'calefaccion': ['calefacción', 'calefaccion'],
        'seguridad': ['seguridad', 'seguro', 'alarma'],
        'ascensor': ['ascensor', 'elevador']
    }
    
    for clave, palabras in bool_caracteristicas.items():
        if any(palabra in texto_lower for palabra in palabras):
            caracteristicas[clave] = True
    
    return caracteristicas

def estandarizar_campos_clave(propiedad):
    """Estandariza campos clave como operación, tipo, etc."""
    
    # Mapeos para estandarización
    mapeo_operacion = {
        'alquiler': ['alquiler', 'renta', 'arriendo'],
        'venta': ['venta', 'vende', 'comprar', 'venta']
    }
    
    mapeo_tipo = {
        'departamento': ['depto', 'dpto', 'apto', 'apartamento', 'departamento'],
        'casa': ['casa', 'house', 'vivienda'],
        'ph': ['ph', 'propiedad horizontal'],
        'casaquinta': ['casa quinta', 'quinta', 'casaquinta'],
        'terreno': ['terreno', 'lote', 'parcela']
    }
    
    # Estandarizar operación
    if 'operacion' in propiedad:
        propiedad['operacion'] = estandarizar_valor(propiedad['operacion'], mapeo_operacion)
    
    # Estandarizar tipo
    if 'tipo' in propiedad:
        propiedad['tipo'] = estandarizar_valor(propiedad['tipo'], mapeo_tipo)
    
    # Estandarizar ubicación
    for campo_ubicacion in ['barrio', 'localidad', 'ciudad']:
        if campo_ubicacion in propiedad and isinstance(propiedad[campo_ubicacion], str):
            propiedad[campo_ubicacion] = propiedad[campo_ubicacion].title().strip()
    
    return propiedad

def estandarizar_valor(valor, mapeo):
    """Estandariza un valor según un mapeo dado"""
    if not isinstance(valor, str):
        return valor
    
    valor_lower = valor.lower()
    
    for valor_estandar, variantes in mapeo.items():
        if any(variante in valor_lower for variante in variantes):
            return valor_estandar
    
    return valor

# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    print("🏠 CONVERSOR EXCEL A JSON - DANTE PROPIEDADES")
    print("=" * 50)
    
    archivo_excel = 'propiedades.xlsx'  # Cambiar por tu archivo
    
    try:
        # Convertir el archivo
        propiedades = excel_a_json_avanzado(archivo_excel)
        
        if propiedades:
            print(f"\n✅ Conversión exitosa!")
            print(f"📊 Total de propiedades: {len(propiedades)}")
            
            # Mostrar ejemplo
            if propiedades:
                print(f"\n📋 Ejemplo de propiedad convertida:")
                print(json.dumps(propiedades[0], ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ Error en la conversión: {e}")