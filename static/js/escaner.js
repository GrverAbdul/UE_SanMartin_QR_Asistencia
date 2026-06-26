// static/js/escaner.js
// Integración con html5-qrcode y envío POST con CSRF.
// Depende de que la plantilla defina la variable global `registrarQrUrl`.

/**
 * Obtiene el valor de una cookie por su nombre.
 * Necesario para leer el token CSRF de Django.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

/**
 * Envía el identificador QR al backend para registrar la asistencia.
 * @param {string} qrId - El texto decodificado del código QR.
 */
function postQr(qrId) {
    fetch(registrarQrUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ qr_id: qrId })
    })
    .then(response => response.json().then(data => ({ status: response.status, body: data })))
    .then(({ status, body }) => {
        const resultado = document.getElementById('resultado');
        if (status === 200 && body.success) {
            // Crear toast flotante grande
            const toast = document.createElement('div');
            toast.className = 'position-fixed top-50 start-50 translate-middle p-5 bg-success text-white rounded shadow-lg';
            toast.style.zIndex = '9999';
            toast.innerHTML = `<h1>✅ Asistencia registrada</h1><p class="fs-4">${body.nombre} - ${body.estado}</p>`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        } else {
            // mensaje de error (puede ser también flotante)
            const toast = document.createElement('div');
            toast.className = 'position-fixed top-50 start-50 translate-middle p-5 bg-danger text-white rounded shadow-lg';
            toast.style.zIndex = '9999';
            toast.innerHTML = `<h2>❌ ${body.error}</h2>`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }
    })
    .catch(err => {
        const resultado = document.getElementById('resultado');
        resultado.innerHTML = `<div class="alert alert-danger">Error de conexión</div>`;
        console.error(err);
    });
}

// Inicializar el lector QR cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const html5QrCode = new Html5Qrcode("reader");
    const qrConfig = { fps: 10, qrbox: 250 };

    function onScanSuccess(decodedText, decodedResult) {
        // Pausar momentáneamente para evitar múltiples lecturas del mismo código
        html5QrCode.pause();
        postQr(decodedText);
        // Reanudar después de 1.2 segundos
        setTimeout(() => html5QrCode.resume(), 1200);
    }

    function onScanFailure(error) {
        // Ignorar los errores continuos de escaneo (ocurre en cada frame sin QR)
    }

    Html5Qrcode.getCameras().then(cameras => {
        if (cameras && cameras.length) {
            html5QrCode.start(
                { facingMode: "environment" }, // Usar cámara trasera si está disponible
                qrConfig,
                onScanSuccess,
                onScanFailure
            ).catch(err => {
                console.error("No se pudo iniciar la cámara", err);
                document.getElementById('resultado').innerHTML = `<div class="alert alert-warning">No se pudo acceder a la cámara.</div>`;
            });
        } else {
            document.getElementById('resultado').innerHTML = `<div class="alert alert-warning">No se detectaron cámaras.</div>`;
        }
    }).catch(err => {
        console.error("Error al obtener las cámaras", err);
        document.getElementById('resultado').innerHTML = `<div class="alert alert-warning">Error al buscar cámaras.</div>`;
    });
});