import React from 'react';
import ReactDOM from 'react-dom/client';

// ====================
// 🔥 CÓDIGO PARA MANTENER BACKEND ACTIVO (SOLO UNA VEZ)
// ====================

// Función para mantener el backend despierto
function keepBackendAlive() {
  fetch('https://ia-inmobiliario.onrender.com/status')
    .then(() => console.log('✅ Backend pinged - manteniendo activo'))
    .catch(error => console.log('❌ Error ping backend:', error));
}

// Ejecutar inmediatamente y cada 10 minutos
keepBackendAlive();
setInterval(keepBackendAlive, 10 * 60 * 1000);

console.log('🔄 Servicio de keep-alive iniciado');

// ====================
// EL RESTO DE TU CÓDIGO EXISTENTE
// ====================

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);