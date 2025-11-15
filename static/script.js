/**
 * Sistema de Predicción de Sequía - Script Principal
 * Gestiona la interacción con la API de Open-Meteo
 */

const API_URL = 'http://127.0.0.1:5000/api';

// Elementos del DOM
const form = document.getElementById('analyzeForm');
const municipioSelect = document.getElementById('municipio');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const result = document.getElementById('result');
// Chart.js instances
let lineChart = null;
let scatterChart = null;
let barChart = null;

/**
 * Inicializa los event listeners
 */
function initEventListeners() {
    form.addEventListener('submit', handleFormSubmit);
}

/**
 * Maneja el envío del formulario
 */
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const municipio = municipioSelect.value;
    
    if (!municipio) {
        showError('Por favor selecciona un municipio');
        return;
    }

    await analyzeSequia(municipio);
}

/**
 * Realiza el análisis de sequía consultando la API
 * @param {string} municipio - Nombre del municipio a analizar
 */
async function analyzeSequia(municipio) {
    // Limpiar errores anteriores
    error.classList.remove('show');
    result.classList.remove('show');
    
    // Mostrar loading
    loading.style.display = 'block';

    try {
        console.log(`Analizando: ${municipio}`);
        
        const response = await fetch(`${API_URL}/analizar?municipio=${municipio}`);
        
        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        if (data.success) {
            console.log('Análisis completado');
            displayResult(municipio, data);
        } else {
            showError(data.error || 'Error desconocido');
        }
    } catch (err) {
        console.error('Error:', err);
        showError(`Error al conectar con el servidor: ${err.message}`);
    } finally {
        loading.style.display = 'none';
    }
}

/**
 * Muestra los resultados del análisis en la interfaz
 * @param {string} municipio - Nombre del municipio
 * @param {object} data - Datos del análisis
 */
function displayResult(municipio, data) {
    document.getElementById('municipioName').textContent = municipio;
    document.getElementById('indiceValue').textContent = `${data.indice_sequia}%`;
    
    // Aplicar clase de color según categoría USDM (D0-D4)
    const nivelValue = document.getElementById('nivelValue');
    const categoria = data.categoria || data.nivel_riesgo || 'D0';
    const nombreCategoria = data.nombre_categoria || categoria;
    // Mostrar formato: "D3 - Sequía Extrema"
    nivelValue.textContent = `${categoria} - ${nombreCategoria}`;
    
    const nivelClass = 'nivel-' + categoria.toLowerCase();
    nivelValue.className = 'result-value ' + nivelClass;
    
    // Mostrar datos climáticos
    document.getElementById('precipValue').textContent = 
        data.datos.precipitacion_promedio.toFixed(2) + ' mm';
    document.getElementById('tempValue').textContent = 
        data.datos.temperatura_promedio.toFixed(2) + ' °C';
    document.getElementById('evapValue').textContent = 
        data.datos.evapotranspiracion_promedio.toFixed(2) + ' mm';

    // Mostrar estadísticas de lluvia (días con/sin precipitación)
    if (data.series && data.series.lluvia_mm) {
        const lluviaData = data.series.lluvia_mm;
        const diasConLluvia = lluviaData.filter(x => Number(x) > 0).length;
        const totalDias = lluviaData.length;
        console.log(`Lluvia: ${diasConLluvia}/${totalDias} días con precipitación (${(diasConLluvia/totalDias*100).toFixed(0)}%)`);
    }

    // Mostrar sección de resultados con animación
    result.classList.add('show');
    
    console.log('Resultados mostrados');

    // Dibujar gráficas si vienen las series
    try {
        if (data.series) {
            const fechas = data.series.fechas || [];
            // Aceptar varias claves posibles (compatibilidad hacia atrás)
            const lluviaRaw = data.series.lluvia_mm || data.series.lluvia || data.series.precipitacion || [];
            // temperatura puede venir como 'temperatura_c' o 'temp_c'
            const tempRaw = data.series.temperatura_c || data.series.temp_c || [];

            // Normalizar a arrays numéricos y recortar al mínimo tamaño común
            const N = Math.min(fechas.length, lluviaRaw.length, tempRaw.length);
            const fechasTrim = fechas.slice(0, N);
            const lluvia = lluviaRaw.slice(0, N).map(x => Number(x) || 0);
            const temp = tempRaw.slice(0, N).map(x => Number(x) || 0);

            // Filtrar filas inválidas (por si alguno es NaN)
            const filteredFechas = [];
            const filteredLluvia = [];
            const filteredTemp = [];
            for (let i = 0; i < N; i++) {
                if (!isNaN(lluvia[i]) && !isNaN(temp[i])) {
                    filteredFechas.push(fechasTrim[i]);
                    filteredLluvia.push(lluvia[i]);
                    filteredTemp.push(temp[i]);
                }
            }

            renderLineChart(filteredFechas, filteredLluvia);
            renderScatterChart(filteredLluvia, filteredTemp);
        }

        // Aceptar diferentes nombres para el promedio mensual
        const monthly = data.promedio_mensual || data.monthly_promedio || [];
        if (monthly && monthly.length > 0) {
            const meses = monthly.map(m => m.mes || m.month || '');
            const lluviaMes = monthly.map(m => Number(m.lluvia_mm || m.lluvia || m.precipitacion || 0));
            renderBarChart(meses, lluviaMes);
        }
    } catch (e) {
        console.error('Error al dibujar gráficas:', e);
    }
}

// ---- Funciones de gráficos usando Chart.js ----
function renderLineChart(labels, valores) {
    const ctx = document.getElementById('chartLine').getContext('2d');
    if (lineChart) {
        lineChart.destroy();
    }
    lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Precipitación (mm)',
                data: valores,
                borderColor: 'rgba(102,126,234,1)',
                backgroundColor: 'rgba(102,126,234,0.18)',
                tension: 0.2,
                fill: true,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: 8 },
            plugins: { legend: { display: true } },
            scales: {
                x: { display: true, title: { display: true, text: 'Fecha' } },
                y: { display: true, title: { display: true, text: 'Precipitación (mm)' } }
            }
        }
    });
}

function renderScatterChart(lluvia, temp) {
    const ctx = document.getElementById('chartScatter').getContext('2d');
    if (scatterChart) {
        scatterChart.destroy();
    }
    const puntos = lluvia.map((l, i) => ({ x: l, y: temp[i] }));
    scatterChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Lluvia vs Temperatura',
                data: puntos,
                backgroundColor: 'rgba(118,75,162,0.9)',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: 6 },
            plugins: { legend: { display: true } },
            scales: {
                x: { title: { display: true, text: 'Precipitación (mm)' } },
                y: { title: { display: true, text: 'Temperatura (°C)' } }
            }
        }
    });
}

function renderBarChart(meses, lluviaMes) {
    const ctx = document.getElementById('chartBar').getContext('2d');
    if (barChart) {
        barChart.destroy();
    }
    const threshold = 20; // mm/mes
    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: meses,
            datasets: [
                {
                    label: 'Lluvia mensual (mm)',
                    data: lluviaMes,
                    backgroundColor: 'rgba(102,126,234,0.78)'
                },
                {
                    label: `Umbral ${threshold} mm/mes`,
                    data: meses.map(() => threshold),
                    type: 'line',
                    borderColor: 'rgba(220,53,69,0.95)',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: 6 },
            plugins: { legend: { display: true } },
            scales: {
                x: { title: { display: true, text: 'Mes' } },
                y: { title: { display: true, text: 'Lluvia (mm)' } }
            }
        }
    });
}

/**
 * Muestra un mensaje de error
 * @param {string} message - Mensaje de error a mostrar
 */
function showError(message) {
    error.textContent = message;
    error.classList.add('show');
    console.error('Error:', message);
}

/**
 * Inicialización al cargar la página
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Aplicación de Sequía iniciada');
    initEventListeners();
});
