
import re
from typing import Dict, Any
from logic.filter_data import BARRIOS, OPERACIONES, TIPOS

def detect_filters(text_lower: str) -> Dict[str, Any]:
    """Detecta y extrae filtros del texto del usuario usando listas estáticas."""
    filters = {}
    
    barrios_disponibles = [b.lower() for b in BARRIOS]
    tipos_disponibles = [t.lower() for t in TIPOS]
    operaciones_disponibles = [o.lower() for o in OPERACIONES]
    
    # Detección de barrio
    barrio_detectado = None
    for barrio in barrios_disponibles:
        if barrio in text_lower:
            barrio_detectado = barrio
            break
    
    if not barrio_detectado:
        barrio_patterns = [
            r"en ([a-zA-Záéíóúñ\s]+)",
            r"barrio ([a-zA-Záéíóúñ\s]+)",
            r"zona ([a-zA-Záéíóúñ\s]+)",
            r"de ([a-zA-Záéíóúñ\s]+)$",
        ]
        
        for pattern in barrio_patterns:
            match = re.search(pattern, text_lower)
            if match:
                potential_barrio = match.group(1).strip().lower()
                if potential_barrio in barrios_disponibles:
                    barrio_detectado = potential_barrio
                    break
    
    if barrio_detectado:
        filters["neighborhood"] = barrio_detectado
    
    # Detección de tipo
    for tipo in tipos_disponibles:
        if tipo in text_lower:
            filters["tipo"] = tipo
            break
    
    # Detección de operación
    for operacion in operaciones_disponibles:
        if operacion in text_lower:
            filters["operacion"] = operacion
            break
    
    # Detección de precio
    precio_patterns = [
        r"hasta \$?\s*([0-9\.]+)\s*(usd|dólares|dolares)?",
        r"máximo \$?\s*([0-9\.]+)\s*(usd|dólares|dolares)?",
        r"precio.*?\$?\s*([0-9\.]+)\s*(usd|dólares|dolares)?",
        r"menos de \$?\s*([0-9\.]+)\s*(usd|dólares|dolares)?",
        r"\$?\s*([0-9\.]+)\s*(usd|dólares|dolares|pesos)",
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
    
    # Precio mínimo
    min_price_match = re.search(r"desde \$?\s*([0-9\.]+)", text_lower)
    if min_price_match:
        try:
            min_price = int(min_price_match.group(1).replace('.', ''))
            filters["min_price"] = min_price
        except ValueError:
            pass
    
    # Ambientes
    rooms_match = re.search(r"(\d+)\s*amb", text_lower) or re.search(r"(\d+)\s*ambiente", text_lower)
    if rooms_match:
        filters["min_rooms"] = int(rooms_match.group(1))

    # Metros cuadrados
    sqm_match = re.search(r"(\d+)\s*m2", text_lower) or re.search(r"(\d+)\s*metros", text_lower)
    if sqm_match:
        filters["min_sqm"] = int(sqm_match.group(1))

    return filters
