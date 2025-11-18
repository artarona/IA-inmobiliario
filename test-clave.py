import google.generativeai as genai

# Configuración básica
genai.configure(api_key="AIzaSyAoC9RD4HPE7l5wY8RcnMHS7F1BeXj7ea8")
model = genai.GenerativeModel('gemini-2.5-flash')

# 1. 📝 TRADUCCIÓN
def traducir_texto(texto, idioma_destino):
    prompt = f"Traduce este texto al {idioma_destino}: '{texto}'"
    response = model.generate_content(prompt)
    return response.text

# 2. 💻 PROGRAMACIÓN
def explicar_codigo(codigo):
    prompt = f"Explica este código:\n{codigo}"
    response = model.generate_content(prompt)
    return response.text

# 3. 📚 RESUMEN
def resumir_texto(texto):
    prompt = f"Resume el siguiente texto en 3 puntos clave:\n{texto}"
    response = model.generate_content(prompt)
    return response.text

# 4. 🎯 ANÁLISIS
def analizar_problema(problema):
    prompt = f"Analiza este problema y sugiere soluciones: {problema}"
    response = model.generate_content(prompt)
    return response.text