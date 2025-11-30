import { obtenerFiltrosSeleccionados, limpiarFiltros } from './filtros.js';
import { enviarConsultaAlBackend, obtenerRespuestaDemo } from './backend.js';

const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const statusText = document.getElementById('statusText');
const resetChatBtn = document.getElementById('resetChatBtn');

let conversacionActual = [];
let conversacionInicialMostrada = false; // ✅ SOLO UNA VARIABLE

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

// ✅ SOLO UNA FUNCIÓN enviarMensaje - ELIMINAR LA DUPLICADA
export async function enviarMensaje() {
    let msg = userInput.value.trim();
    if (!msg) return alert('Por favor, escribí tu consulta.');

    // ✅ MOSTRAR BIENVENIDA SOLO LA PRIMERA VEZ
    if (!conversacionInicialMostrada) {
        addMessage('¡Hola! 👋 Soy tu asistente de Dante Propiedades. Te ayudo a encontrar la propiedad ideal. Podés usar los filtros o contarme directamente qué necesitás. ¿En qué puedo ayudarte hoy?', 'bot');
        conversacionInicialMostrada = true;
    }

    addMessage(msg, 'user');
    userInput.value = '';
    sendBtn.disabled = true;
    showTypingIndicator();

    const filtros = obtenerFiltrosSeleccionados();
    if (Object.keys(filtros).length === 0) limpiarFiltros();

    try {
        const data = await enviarConsultaAlBackend(msg, filtros);
        
        // ✅ DIAGNÓSTICO
        console.log("🎯 ===== DIAGNÓSTICO PROPIEDADES =====");
        console.log("📦 RESPUESTA COMPLETA:", data);
        console.log("🏠 PROPIEDADES:", data.propiedades);
        console.log("🔢 CANTIDAD PROPIEDADES:", data.propiedades ? data.propiedades.length : 0);
        console.log("✅ BÚSQUEDA REALIZADA:", data.search_performed);
        console.log("📊 CONTADOR RESULTADOS:", data.results_count);

        if (data.propiedades && data.propiedades.length > 0) {
            console.log("✅ HAY PROPIEDADES - DETALLES:");
            data.propiedades.forEach((prop, index) => {
                console.log(`   ${index + 1}. ${prop.titulo} - ${prop.operacion} - $${prop.precio}`);
            });
            
            console.log("🚀 ACTIVANDO VISUALIZACIÓN DE PROPIEDADES");
            mostrarPropiedadesEnInterfaz(data.propiedades);
        } else {
            console.log("❌ NO HAY PROPIEDADES PARA MOSTRAR");
        }
        console.log("🎯 ===== FIN DIAGNÓSTICO =====");
        
        addMessage(data.response || '❌ Respuesta inesperada del servidor');
        statusText.textContent = 'Conectado';
        
    } catch (error) {
        console.error('❌ Error:', error);
        const demo = obtenerRespuestaDemo(msg);
        addMessage(demo ? demo.response + '\n\n---\n**🔧 Modo demo**' : '🔍 Consulta en modo demostración');
        statusText.textContent = 'Modo Demo';
    } finally {
        conversacionActual = [];
        hideTypingIndicator();
        sendBtn.disabled = false;
        userInput.focus();
    }
}

export function resetearChat() {
    if (confirm('¿Querés empezar una nueva conversación?')) {
        chatBox.innerHTML = '';
        conversacionActual = [];
        conversacionInicialMostrada = false; // ✅ Resetear bandera
        limpiarFiltros();
        // NO agregar mensaje de bienvenida aquí
    }
}

// ✅ FUNCIÓN PARA MOSTRAR PROPIEDADES EN LA INTERFAZ

// ✅ FUNCIÓN PARA FORMATEAR PRECIOS
function formatPrecio(precio, moneda) {
    if (!precio || precio === 0) return 'Consultar';
    
    if (moneda === 'USD') {
        return `USD ${precio.toLocaleString('es-AR')}`;
    } else {
        return `$${precio.toLocaleString('es-AR')} ${moneda || 'ARS'}`;
    }
}
// ✅ FUNCIÓN PARA MOSTRAR PROPIEDADES CON IMÁGENES
function mostrarPropiedadesEnInterfaz(propiedades) {
    console.log("🖥️ MOSTRANDO PROPIEDADES EN INTERFAZ CON IMÁGENES");
    
    let propiedadesContainer = document.getElementById('propiedadesContainer');
    
    if (!propiedadesContainer) {
        propiedadesContainer = document.createElement('div');
        propiedadesContainer.id = 'propiedadesContainer';
        propiedadesContainer.className = 'propiedades-container';
        chatBox.appendChild(propiedadesContainer);
    }
    
    propiedadesContainer.innerHTML = '<h3 style="margin-bottom: 15px; color: #333;">🏠 Propiedades Encontradas</h3>';
    
    const propertyEmojis = {
        'casa': '🏠',
        'departamento': '🏢', 
        'ph': '🏡',
        'terreno': '📐',
        'oficina': '💼',
        'casaquinta': '🏘️',
        'local': '🏪',
        'galpon': '🏭'
    };
    
    propiedades.forEach((prop, index) => {
        const emoji = propertyEmojis[prop.tipo?.toLowerCase()] || '🏠';
        
        const propElement = document.createElement('div');
        propElement.className = 'propiedad-card';
        
        // ✅ GENERAR HTML CON IMÁGENES
        propElement.innerHTML = generarHTMLPropiedad(prop, index, emoji);
        
        propiedadesContainer.appendChild(propElement);
    });
    
    console.log(`✅ ${propiedades.length} propiedades mostradas en interfaz`);
}

// ✅ FUNCIÓN PARA GENERAR HTML DE PROPIEDAD CON IMÁGENES
function generarHTMLPropiedad(prop, index, emoji) {
    const tieneImagenes = prop.fotos && prop.fotos.length > 0;
    const primeraImagen = tieneImagenes ? prop.fotos[0] : null;
    const totalImagenes = tieneImagenes ? prop.fotos.length : 0;
    
    return `
        <div class="propiedad-header">
            <h4><span class="numero-propiedad">${index + 1}.</span> ${emoji} ${prop.titulo}</h4>
            <span class="precio">${formatPrecio(prop.precio, prop.moneda_precio)}</span>
        </div>
        
        ${tieneImagenes ? `
        <div class="propiedad-imagenes">
            <div class="imagen-principal">
                <img src="${primeraImagen}" alt="${prop.titulo}" 
                     onerror="this.style.display='none'" 
                     onload="this.style.opacity='1'">
                ${totalImagenes > 1 ? `
                <div class="contador-imagenes">+${totalImagenes - 1} más</div>
                ` : ''}
            </div>
            ${totalImagenes > 1 ? `
            <div class="galeria-miniaturas">
                ${prop.fotos.slice(0, 4).map((foto, i) => `
                    <img src="${foto}" alt="Imagen ${i + 1}" 
                         onerror="this.style.display='none'"
                         onclick="cambiarImagenPrincipal('${foto}', this)">
                `).join('')}
            </div>
            ` : ''}
        </div>
        ` : `
        <div class="sin-imagen">
            <span>📷 Imágenes no disponibles</span>
        </div>
        `}
        
        <div class="propiedad-info">
            <span>📍 ${prop.barrio}</span>
            <span>🏠 ${prop.ambientes} amb</span>
            <span>📏 ${prop.metros_cuadrados} m²</span>
            <span>📋 ${prop.operacion}</span>
        </div>
        
        ${prop.descripcion ? `<p class="descripcion">${prop.descripcion}</p>` : ''}
        
        <div class="propiedad-acciones">
            <button class="btn-ver-mas" onclick="verMasDetalles('${prop.id_temporal}')">
                📋 Ver más detalles
            </button>
            ${tieneImagenes ? `
            <button class="btn-galeria" onclick="abrirGaleriaCompleta('${prop.id_temporal}')">
                🖼️ Ver galería completa (${totalImagenes})
            </button>
            ` : ''}
        </div>
    `;
}
// ✅ FUNCIONES PARA MANEJO DE IMÁGENES
function cambiarImagenPrincipal(nuevaImagen, elementoClickeado) {
    const contenedorPadre = elementoClickeado.closest('.propiedad-imagenes');
    const imagenPrincipal = contenedorPadre.querySelector('.imagen-principal img');
    
    if (imagenPrincipal) {
        imagenPrincipal.style.opacity = '0';
        setTimeout(() => {
            imagenPrincipal.src = nuevaImagen;
            imagenPrincipal.style.opacity = '1';
        }, 300);
    }
    
    // Resaltar miniatura activa
    const todasMiniaturas = contenedorPadre.querySelectorAll('.galeria-miniaturas img');
    todasMiniaturas.forEach(img => img.classList.remove('activa'));
    elementoClickeado.classList.add('activa');
}

function abrirGaleriaCompleta(idPropiedad) {
    console.log(`🖼️ Abriendo galería completa para propiedad: ${idPropiedad}`);
    alert(`📸 Galería completa de la propiedad ${idPropiedad}\n\nEsta funcionalidad se puede expandir para mostrar un modal con todas las imágenes.`);
}

function verMasDetalles(idPropiedad) {
    console.log(`📋 Viendo más detalles para: ${idPropiedad}`);
    // Aquí puedes implementar la lógica para mostrar detalles completos
    alert(`🔍 Mostrando detalles completos de la propiedad ${idPropiedad}`);
}