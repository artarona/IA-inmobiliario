// backend.js
const API_URL = "https://dante-propiedades-backend.onrender.com/chat";

export async function enviarConsultaAlBackend(mensaje, filtros) {
    const requestData = {
        message: mensaje,
        channel: 'web',
        filters: filtros
    };

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
}

export function obtenerRespuestaDemo(mensaje) {
    const datosDemo = { /* mismo bloque de datos demo que tenías */ };
    const msg = mensaje.toLowerCase().trim();
    return datosDemo[msg] || Object.values(datosDemo).find(d => msg.includes(d.key)) || null;
}
