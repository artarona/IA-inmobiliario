// chat.js
import { obtenerFiltrosSeleccionados, limpiarFiltros } from './filtros.js';
import { enviarConsultaAlBackend, obtenerRespuestaDemo } from './backend.js';

const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const statusText = document.getElementById('statusText');
const resetChatBtn = document.getElementById('resetChatBtn');

let conversacionActual = [];

export function addMessage(text, from = "bot") {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${from === 'user' ? 'msg-user' : 'msg-bot'}`;
    messageDiv.innerHTML = from === 'bot' ? `<b>ASISTENTE VIRTUAL</b>${text}` : text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    conversacionActual.push({ text, from, timestamp: new Date().toISOString() });
}

function showTypingIndicator() {
    typingIndicator.style.display = 'flex';
    chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

export async function enviarMensaje() {
    let msg = userInput.value.trim();
    if (!msg) return alert('Por favor, escribí tu consulta.');

    addMessage(msg, 'user');
    userInput.value = '';
    sendBtn.disabled = true;
    showTypingIndicator();

    const filtros = obtenerFiltrosSeleccionados();
    if (Object.keys(filtros).length === 0) limpiarFiltros(); // 🔄 Limpieza automática

    try {
        const data = await enviarConsultaAlBackend(msg, filtros);
        addMessage(data.response || '❌ Respuesta inesperada del servidor');
        statusText.textContent = 'Conectado';
    } catch (error) {
        console.error('❌ Error:', error);
        const demo = obtenerRespuestaDemo(msg);
        addMessage(demo ? demo.response + '\n\n---\n**🔧 Modo demo**' : '🔍 Consulta en modo demostración');
        statusText.textContent = 'Modo Demo';
    } finally {
        conversacionActual = []; // 🧼 Reset de contexto
        hideTypingIndicator();
        sendBtn.disabled = false;
        userInput.focus();
    }
}

export function resetearChat() {
    if (confirm('¿Querés empezar una nueva conversación?')) {
        chatBox.innerHTML = '';
        conversacionActual = [];
        limpiarFiltros();
        addMessage('¡Perfecto! Empezamos de nuevo. ¿Qué propiedad estás buscando?', 'bot');
    }
}
