#!/usr/bin/env python3
"""
CREA 15 PROPIEDADES DE EJEMPLO para probar el sistema
"""

import pandas as pd
import json
import os
import random
from datetime import datetime

def crear_propiedades_ejemplo():
    print("🏗️ CREANDO 15 PROPIEDADES DE EJEMPLO")
    print("=" * 50)
    
    excel_file = "propiedades.xlsx"
    
    # Datos de ejemplo REALISTAS
    propiedades = [
        {
            "titulo": "Departamento en Palermo SoHo",
            "barrio": "palermo",
            "precio": 280000,
            "ambientes": 2,
            "metros": 68,
            "operacion": "alquiler",
            "tipo": "departamento",
            "descripcion": "Excelente departamento en el corazón de Palermo SoHo",
            "direccion": "Honduras 1450",
            "antiguedad": 3,
            "estado": "excelente",
            "orientacion": "norte",
            "piso": "5",
            "expensas": 8500,
            "amenities": "pileta, gimnasio, sum, seguridad 24hs",
            "cochera": "Sí",
            "balcon": "Sí",
            "pileta": "Sí",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Fotos profesionales disponibles, Tour virtual 360°"
        },
        {
            "titulo": "Casa en Belgrano R",
            "barrio": "belgrano",
            "precio": 650000,
            "ambientes": 4,
            "metros": 180,
            "operacion": "venta",
            "tipo": "casa",
            "descripcion": "Magnífica casa familiar con jardín y pileta",
            "direccion": "Juramento 2345",
            "antiguedad": 8,
            "estado": "excelente",
            "orientacion": "norte",
            "piso": "",
            "expensas": 0,
            "amenities": "pileta, parrilla, jardín, cochera cubierta",
            "cochera": "Sí",
            "balcon": "Sí",
            "pileta": "Sí",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Video tour disponible, Fotos del jardín, Plano de la propiedad"
        },
        {
            "titulo": "PH en Colegiales",
            "barrio": "colegiales",
            "precio": 190000,
            "ambientes": 1,
            "metros": 48,
            "operacion": "alquiler",
            "tipo": "ph",
            "descripcion": "Acogedor PH ideal para una persona, totalmente reciclado",
            "direccion": "Conesa 876",
            "antiguedad": 2,
            "estado": "excelente",
            "orientacion": "este",
            "piso": "planta baja",
            "expensas": 2500,
            "amenities": "patio privado, lavadero independiente",
            "cochera": "No",
            "balcon": "No",
            "pileta": "No",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Fotos del PH reciclado, Plano de distribución"
        },
        {
            "titulo": "Monoambiente en Microcentro",
            "barrio": "microcentro",
            "precio": 120000,
            "ambientes": 1,
            "metros": 35,
            "operacion": "alquiler",
            "tipo": "departamento",
            "descripcion": "Monoambiente funcional en pleno microcentro, excelente ubicación",
            "direccion": "Lavalle 1234",
            "antiguedad": 10,
            "estado": "bueno",
            "orientacion": "sur",
            "piso": "12",
            "expensas": 4500,
            "amenities": "seguridad 24hs, laundry",
            "cochera": "No",
            "balcon": "No",
            "pileta": "No",
            "acepta_mascotas": "No",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Fotos de la unidad, Video del edificio"
        },
        {
            "titulo": "Departamento en Recoleta",
            "barrio": "recoleta",
            "precio": 420000,
            "ambientes": 3,
            "metros": 95,
            "operacion": "venta",
            "tipo": "departamento",
            "descripcion": "Lujoso departamento en torre de Recoleta con vistas panorámicas",
            "direccion": "Ayacucho 1678",
            "antiguedad": 5,
            "estado": "excelente",
            "orientacion": "norte",
            "piso": "15",
            "expensas": 12000,
            "amenities": "pileta, gimnasio, sum, seguridad 24hs, salón de fiestas",
            "cochera": "Sí",
            "balcon": "Sí",
            "pileta": "Sí",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Tour virtual 360°, Fotos profesionales, Video del edificio"
        },
        {
            "titulo": "Casaquinta en San Isidro",
            "barrio": "san isidro",
            "precio": 850000,
            "ambientes": 5,
            "metros": 220,
            "operacion": "venta",
            "tipo": "casaquinta",
            "descripcion": "Exclusiva casaquinta con parque arbolado y pileta olímpica",
            "direccion": "Av. del Libertador 3456",
            "antiguedad": 15,
            "estado": "excelente",
            "orientacion": "norte",
            "piso": "",
            "expensas": 0,
            "amenities": "pileta, parrilla, quincho, jardín, cochera 3 autos",
            "cochera": "Sí",
            "balcon": "Sí",
            "pileta": "Sí",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Drone video, Fotos del parque, Tour de la propiedad"
        },
        {
            "titulo": "Departamento en Almagro",
            "barrio": "almagro",
            "precio": 165000,
            "ambientes": 2,
            "metros": 55,
            "operacion": "alquiler",
            "tipo": "departamento",
            "descripcion": "Departamento luminoso cerca del Parque Centenario",
            "direccion": "Díaz Vélez 2345",
            "antiguedad": 12,
            "estado": "bueno",
            "orientacion": "oeste",
            "piso": "3",
            "expensas": 3800,
            "amenities": "seguridad, lavadero",
            "cochera": "No",
            "balcon": "Sí",
            "pileta": "No",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "No",
            "info_multimedia": "Fotos de la propiedad, Video del barrio"
        },
        {
            "titulo": "PH en Villa Crespo",
            "barrio": "villa crespo",
            "precio": 210000,
            "ambientes": 2,
            "metros": 60,
            "operacion": "venta",
            "tipo": "ph",
            "descripcion": "PH con patio parisino, ideal para jóvenes profesionales",
            "direccion": "Serrano 1456",
            "antiguedad": 4,
            "estado": "excelente",
            "orientacion": "norte",
            "piso": "planta baja",
            "expensas": 2800,
            "amenities": "patio parisino, lavadero",
            "cochera": "No",
            "balcon": "No",
            "pileta": "No",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Fotos del patio, Plano de distribución"
        },
        {
            "titulo": "Departamento en Caballito",
            "barrio": "caballito",
            "precio": 195000,
            "ambientes": 2,
            "metros": 58,
            "operacion": "alquiler",
            "tipo": "departamento",
            "descripcion": "Departamento funcional a metros del Parque Rivadavia",
            "direccion": "Av. Rivadavia 5678",
            "antiguedad": 8,
            "estado": "bueno",
            "orientacion": "este",
            "piso": "4",
            "expensas": 4200,
            "amenities": "seguridad, ascensor",
            "cochera": "No",
            "balcon": "Sí",
            "pileta": "No",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "No",
            "info_multimedia": "Fotos de la propiedad, Mapa de ubicación"
        },
        {
            "titulo": "Casa en Nuñez",
            "barrio": "nuñez",
            "precio": 520000,
            "ambientes": 3,
            "metros": 140,
            "operacion": "venta",
            "tipo": "casa",
            "descripcion": "Casa moderna con diseño contemporáneo y jardín",
            "direccion": "Uruguay 2345",
            "antiguedad": 6,
            "estado": "excelente",
            "orientacion": "norte",
            "piso": "",
            "expensas": 0,
            "amenities": "jardín, cochera, terraza",
            "cochera": "Sí",
            "balcon": "Sí",
            "pileta": "No",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Fotos profesionales, Video tour, Plano de la casa"
        },
        {
            "titulo": "Estudio en Palermo Hollywood",
            "barrio": "palermo",
            "precio": 135000,
            "ambientes": 1,
            "metros": 32,
            "operacion": "alquiler",
            "tipo": "departamento",
            "descripcion": "Estudio moderno en edificio nuevo, perfecto para estudiantes",
            "direccion": "Fitz Roy 1678",
            "antiguedad": 1,
            "estado": "excelente",
            "orientacion": "norte",
            "piso": "7",
            "expensas": 5200,
            "amenities": "gimnasio, sum, seguridad 24hs",
            "cochera": "No",
            "balcon": "Sí",
            "pileta": "Sí",
            "acepta_mascotas": "No",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Fotos del estudio, Video del edificio"
        },
        {
            "titulo": "PH en Boedo",
            "barrio": "boedo",
            "precio": 175000,
            "ambientes": 2,
            "metros": 52,
            "operacion": "alquiler",
            "tipo": "ph",
            "descripcion": "PH tradicional con mucho carácter, en zona de bares tangueros",
            "direccion": "Av. Boedo 2345",
            "antiguedad": 25,
            "estado": "a refaccionar",
            "orientacion": "sur",
            "piso": "planta baja",
            "expensas": 1800,
            "amenities": "patio interno",
            "cochera": "No",
            "balcon": "No",
            "pileta": "No",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "No",
            "info_multimedia": "Fotos del PH, Informe técnico"
        },
        {
            "titulo": "Departamento en Balvanera",
            "barrio": "balvanera",
            "precio": 145000,
            "ambientes": 2,
            "metros": 50,
            "operacion": "alquiler",
            "tipo": "departamento",
            "descripcion": "Departamento económico cerca de Once, ideal para inversión",
            "direccion": "Pueyrredón 1234",
            "antiguedad": 15,
            "estado": "bueno",
            "orientacion": "oeste",
            "piso": "2",
            "expensas": 3200,
            "amenities": "ascensor, seguridad",
            "cochera": "No",
            "balcon": "No",
            "pileta": "No",
            "acepta_mascotas": "No",
            "aire_acondicionado": "No",
            "info_multimedia": "Fotos básicas, Información de rentabilidad"
        },
        {
            "titulo": "Casa en Vicente López",
            "barrio": "vicente lopez",
            "precio": 720000,
            "ambientes": 4,
            "metros": 190,
            "operacion": "venta",
            "tipo": "casa",
            "descripcion": "Casa familiar con piscina y amplio jardín, cerca del río",
            "direccion": "Av. del Libertador 4567",
            "antiguedad": 12,
            "estado": "excelente",
            "orientacion": "norte",
            "piso": "",
            "expensas": 0,
            "amenities": "pileta, quincho, jardín, cochera 2 autos",
            "cochera": "Sí",
            "balcon": "Sí",
            "pileta": "Sí",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Drone footage, Fotos del jardín, Tour virtual"
        },
        {
            "titulo": "Departamento en Puerto Madero",
            "barrio": "puerto madero",
            "precio": 950000,
            "ambientes": 3,
            "metros": 110,
            "operacion": "venta",
            "tipo": "departamento",
            "descripcion": "Exclusivo departamento en torre de Puerto Madero con vista al dique",
            "direccion": "Alicia Moreau de Justo 1234",
            "antiguedad": 4,
            "estado": "excelente",
            "orientacion": "este",
            "piso": "22",
            "expensas": 18500,
            "amenities": "pileta, gimnasio, sum, seguridad 24hs, spa, business center",
            "cochera": "Sí",
            "balcon": "Sí",
            "pileta": "Sí",
            "acepta_mascotas": "Sí",
            "aire_acondicionado": "Sí",
            "info_multimedia": "Tour virtual premium, Fotos con drone, Video del edificio"
        }
    ]
    
    # Crear DataFrame
    df = pd.DataFrame(propiedades)
    
    # Guardar Excel
    df.to_excel(excel_file, index=False)
    print(f"✅ Excel creado: {excel_file}")
    print(f"📊 Total propiedades: {len(propiedades)}")
    
    # Mostrar resumen
    print(f"\n📈 RESUMEN DE PROPIEDADES CREADAS:")
    print("=" * 40)
    
    # Estadísticas
    barrios = {}
    operaciones = {}
    tipos = {}
    
    for prop in propiedades:
        barrio = prop['barrio']
        operacion = prop['operacion']
        tipo = prop['tipo']
        
        barrios[barrio] = barrios.get(barrio, 0) + 1
        operaciones[operacion] = operaciones.get(operacion, 0) + 1
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    print(f"🏢 Por operación: {operaciones}")
    print(f"🏠 Por tipo: {tipos}")
    print(f"📍 Barrios: {barrios}")
    
    # Rango de precios
    precios = [p['precio'] for p in propiedades]
    print(f"💰 Rango de precios: ${min(precios):,} - ${max(precios):,}")
    
    return True

def convertir_a_json():
    """Convierte el Excel a JSON automáticamente"""
    print(f"\n🔄 CONVIRTIENDO a JSON...")
    
    try:
        # Leer Excel
        df = pd.read_excel("propiedades.xlsx")
        
        # Convertir a JSON
        propiedades_json = []
        
        for index, row in df.iterrows():
            propiedad = {
                "id": index + 1,
                "title": str(row['titulo']),
                "neighborhood": str(row['barrio']).lower(),
                "price": float(row['precio']),
                "rooms": int(row['ambientes']),
                "sqm": float(row['metros']),
                "description": str(row['descripcion']),
                "operacion": str(row['operacion']).lower(),
                "tipo": str(row['tipo']).lower(),
                "direccion_exacta": str(row.get('direccion', '')),
                "antiguedad": int(row.get('antiguedad', 0)),
                "estado": str(row.get('estado', 'bueno')).lower(),
                "orientacion": str(row.get('orientacion', '')),
                "piso": str(row.get('piso', '')),
                "expensas": float(row.get('expensas', 0)),
                "amenities": str(row.get('amenities', '')),
                "cochera": str(row.get('cochera', 'No')) == 'Sí',
                "balcon": str(row.get('balcon', 'No')) == 'Sí',
                "pileta": str(row.get('pileta', 'No')) == 'Sí',
                "acepta_mascotas": str(row.get('acepta_mascotas', 'No')) == 'Sí',
                "aire_acondicionado": str(row.get('aire_acondicionado', 'No')) == 'Sí',
                "info_multimedia": str(row.get('info_multimedia', ''))
            }
            propiedades_json.append(propiedad)
        
        # Guardar JSON
        with open("properties.json", 'w', encoding='utf-8') as f:
            json.dump(propiedades_json, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON creado: properties.json")
        print(f"📁 {len(propiedades_json)} propiedades convertidas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al convertir: {e}")
        return False

if __name__ == "__main__":
    print("🏠 GENERADOR DE 15 PROPIEDADES DE EJEMPLO")
    print("=" * 50)
    print("Este script creará un Excel con 15 propiedades variadas")
    print("y las convertirá automáticamente a JSON para el sistema.")
    print()
    
    # Crear Excel
    if crear_propiedades_ejemplo():
        # Convertir a JSON
        if convertir_a_json():
            print(f"\n🎉 ¡TODO LISTO!")
            print("=" * 30)
            print("✅ Excel creado: propiedades.xlsx")
            print("✅ JSON creado: properties.json") 
            print("✅ 15 propiedades de ejemplo listas")
            print()
            print("🚀 Ahora puedes:")
            print("   1. Reiniciar el servidor")
            print("   2. Probar el sistema con datos reales")
            print("   3. Usar el Excel como template para tus propiedades")
        else:
            print("❌ Error al crear JSON")
    else:
        print("❌ Error al crear Excel")
    
    input("\nPresiona Enter para salir...")