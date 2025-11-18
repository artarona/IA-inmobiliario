import requests
import json

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    print("🧪 INICIANDO PRUEBAS DE LA API...\n")
    
    # 1. Test health endpoints
    print("1. 🔍 Probando endpoints de salud...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   ✅ / : {response.status_code} - {response.json()}")
        
        response = requests.get(f"{BASE_URL}/status")
        print(f"   ✅ /status : {response.status_code}")
        
        response = requests.get(f"{BASE_URL}/debug")
        print(f"   ✅ /debug : {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 2. Test propiedades
    print("\n2. 🏠 Probando búsqueda de propiedades...")
    try:
        response = requests.get(f"{BASE_URL}/properties?neighborhood=Palermo&limit=3")
        data = response.json()
        print(f"   ✅ /properties : {data['count']} propiedades encontradas")
        for prop in data['properties'][:2]:
            print(f"      📍 {prop['title']} - ${prop['price']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. Test chat
    print("\n3. 💬 Probando chat con Gemini...")
    test_messages = [
        "Hola, ¿cómo estás?",
        "Busco departamento en Palermo para alquilar",
        "Quiero una casa con 3 ambientes"
    ]
    
    for message in test_messages:
        try:
            payload = {
                "message": message,
                "channel": "web"
            }
            response = requests.post(f"{BASE_URL}/chat", json=payload)
            data = response.json()
            
            if "response" in data:
                print(f"   ✅ '{message[:30]}...'")
                print(f"      🤖 {data['response'][:80]}...")
            else:
                print(f"   ❌ Error en respuesta: {data}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_all_endpoints()