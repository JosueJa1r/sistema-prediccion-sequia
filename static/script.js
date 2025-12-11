/**
 * Tierra que habla - Script Principal
 * Gestiona la interacción con la API de Open-Meteo
 */

const API_URL = 'http://127.0.0.1:5000/api';

const RECOMENDACIONES = {
    "D0": {
        agricultores: "Monitoree la humedad del suelo. Use un medidor de humedad de bajo costo o la prueba del puño (hacer una bola con tierra) para evaluar la necesidad de riego de auxilio inicial.",
        ganaderos: "Asegure el almacenamiento de agua. Revise la impermeabilidad de los bordos y presones. Active el protocolo de limpieza y mantenimiento de tinacos y aljibes."
    },
    "D1": {
        agricultores: "Considere la siembra en curvas de nivel. En áreas de temporal, esto ayuda a maximizar la infiltración del agua de lluvia escasa y reduce la erosión.",
        ganaderos: "Implemente la rotación de potreros intensiva. Esto permite que el pastizal existente se recupere entre usos, maximizando el forraje disponible antes de la sequía severa."
    },
    "D2": {
        agricultores: "Coseche agua de lluvia de techos. Instale canaletas y tanques (cisternas) para almacenar el agua de cualquier lluvia esporádica para uso doméstico o riego de huertos de subsistencia.",
        ganaderos: "Trate la paja y rastrojos. Use urea o melaza para mejorar el valor nutricional de los residuos de cosecha (rastrojos de maíz o trigo), utilizándolos como suplemento del forraje caro."
    },
    "D3": {
        agricultores: "Prepare la tierra para el próximo ciclo. Realice prácticas de conservación de suelos (como subsoleo) para romper capas duras y mejorar la capacidad de captación de agua una vez que regresen las lluvias.",
        ganaderos: "Establezca acuerdos de pastoreo temporal (renta). Busque convenios con productores en regiones menos afectadas (valles centrales o zonas con riego) para mover el ganado y reducir costos de forraje y transporte de agua."
    },
    "D4": {
        agricultores: "Documente pérdidas. Tome fotografías y mantenga un registro de los daños en sus cultivos para facilitar futuras solicitudes de apoyo ante programas como el Seguro Catastrófico o el FONDEN.",
        ganaderos: "Priorice el ganado de reemplazo. Separe y mantenga con vida únicamente a las vaquillas y sementales genéticamente superiores que aseguren la reactivación del hato cuando termine la emergencia."
    }
};

// Elementos del DOM
const form = document.getElementById('analyzeForm');
const municipioSelect = document.getElementById('municipio');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const result = document.getElementById('result');
// Chart.js instances (globales para acceso desde translations.js)
window.lineChart = null;
window.scatterChart = null;
window.barChart = null;
window.regressionChart = null;

/**
 * Inicializa los event listeners
 */
function initEventListeners() {
    form.addEventListener('submit', handleFormSubmit);
    
    // Inicializar selector de idioma
    if (typeof initLanguageSelector === 'function') {
        initLanguageSelector();
    }
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
    
    // Obtener idioma actual (usar una sola vez)
    const currentLang = localStorage.getItem('preferredLanguage') || 'es';
    
    // Aplicar clase de color según categoría USDM (D0-D4)
    const nivelValue = document.getElementById('nivelValue');
    const categoria = data.categoria || data.nivel_riesgo || 'D0';
    
    // Traducir categoría según idioma
    let nombreCategoria = data.nombre_categoria || categoria;
    if (translations && translations[currentLang] && translations[currentLang].droughtCategory) {
        nombreCategoria = translations[currentLang].droughtCategory[categoria] || nombreCategoria;
    }
    
    // Mostrar formato: "D3 - Sequía Extrema"
    nivelValue.textContent = `${categoria} - ${nombreCategoria}`;
    nivelValue.dataset.category = categoria; // Guardar para cambios de idioma
    
    const nivelClass = 'nivel-' + categoria.toLowerCase();
    nivelValue.className = 'result-value ' + nivelClass;
    
    // Mostrar datos climáticos
    document.getElementById('precipValue').textContent = 
        data.datos.precipitacion_promedio.toFixed(2) + ' mm';
    document.getElementById('tempValue').textContent = 
        data.datos.temperatura_promedio.toFixed(2) + ' °C';
    document.getElementById('evapValue').textContent = 
        data.datos.evapotranspiracion_promedio.toFixed(2) + ' mm';

    // Mostrar recomendaciones con soporte multiidioma
    let recomendaciones;
    
    if (translations && translations[currentLang] && translations[currentLang].recommendations) {
        recomendaciones = translations[currentLang].recommendations[categoria];
    }
    
    // Fallback a español si no hay traducción
    if (!recomendaciones) {
        recomendaciones = RECOMENDACIONES[categoria] || { 
            agricultores: "No hay recomendaciones disponibles.", 
            ganaderos: "No hay recomendaciones disponibles." 
        };
    }
    
    const recAgricultores = document.getElementById('recAgricultores');
    const recGanaderos = document.getElementById('recGanaderos');
    
    if (recomendaciones) {
        recAgricultores.textContent = recomendaciones.agricultores;
        recGanaderos.textContent = recomendaciones.ganaderos;
        
        // Guardar categoría para cambios de idioma
        recAgricultores.dataset.category = categoria;
        recGanaderos.dataset.category = categoria;
    }

    // Mostrar estadísticas de lluvia (días con/sin precipitación)
    if (data.series && data.series.lluvia_mm) {
        const lluviaData = data.series.lluvia_mm;
        const diasConLluvia = lluviaData.filter(x => Number(x) > 0).length;
        const totalDias = lluviaData.length;
        console.log(`Lluvia: ${diasConLluvia}/${totalDias} días con precipitación (${(diasConLluvia/totalDias*100).toFixed(0)}%)`);
    }

    // Mostrar sección de resultados con animación
    result.classList.add('show');

    // Actualizar y mostrar el enlace a los datos diarios
    const linkDatosDiarios = document.getElementById('linkDatosDiarios');
    if (linkDatosDiarios) {
        // Usamos encodeURIComponent para manejar nombres con espacios o caracteres especiales
        linkDatosDiarios.href = `static/diferencial/diferencial.html?municipio=${encodeURIComponent(municipio)}`;
        linkDatosDiarios.style.display = 'block';
    }
    
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
            renderRegressionChart(filteredFechas, filteredLluvia);
        }

        // Aceptar diferentes nombres para el promedio mensual
        const monthly = data.promedio_mensual || data.monthly_promedio || [];
        if (monthly && monthly.length > 0) {
            const meses = monthly.map(m => m.mes || m.month || '');
            const lluviaMes = monthly.map(m => Number(m.lluvia_mm || m.lluvia || m.precipitacion || 0));
            renderBarChart(meses, lluviaMes);
        }

        dibujarModeloMatematico(data); // Llamamos a la nueva función pasándole los datos de la API
    } catch (e) {
        console.error('Error al dibujar gráficas:', e);
    }
}

// ---- Funciones de gráficos usando Chart.js ----
function renderLineChart(labels, valores) {
    const ctx = document.getElementById('chartLine').getContext('2d');

    if (window.lineChart) {
        window.lineChart.destroy();
    }
    
    // Obtener idioma actual para el título
    const currentLang = localStorage.getItem('preferredLanguage') || 'es';
    const chartTitle = translations && translations[currentLang] && translations[currentLang].lineChartTitle 
        ? translations[currentLang].lineChartTitle 
        : 'Precipitación Diaria (Últimos 90 Días)';
    
    window.lineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Precipitación Diaria (mm)',
                data: valores,
                borderColor: 'rgba(102, 126, 234, 1)',
                backgroundColor: 'rgba(102, 126, 234, 0.18)',
                tension: 0.2,
                fill: true,
                pointRadius: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: 8 },
            plugins: { 
                title: {
                    display: true,
                    text: chartTitle,
                    font: { size: 14, weight: 'bold' }
                },
                legend: { display: true }
            },
            scales: {
                x: { display: true, title: { display: true, text: 'Fecha' } },
                y: { display: true, title: { display: true, text: 'Precipitación (mm)' } }
            }
        }
    });
}

function renderScatterChart(lluvia, temp) {
    const ctx = document.getElementById('chartScatter').getContext('2d');
    if (window.scatterChart) {
        window.scatterChart.destroy();
    }
    
    // Obtener idioma actual para el título
    const currentLang = localStorage.getItem('preferredLanguage') || 'es';
    const chartTitle = translations && translations[currentLang] && translations[currentLang].scatterChartTitle 
        ? translations[currentLang].scatterChartTitle 
        : 'Relación Precipitación vs Temperatura';
    
    const puntos = lluvia.map((l, i) => ({ x: l, y: temp[i] }));
    window.scatterChart = new Chart(ctx, {
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
            plugins: { 
                title: {
                    display: true,
                    text: chartTitle,
                    font: { size: 14, weight: 'bold' }
                },
                legend: { display: true }
            },
            scales: {
                x: { title: { display: true, text: 'Precipitación (mm)' } },
                y: { title: { display: true, text: 'Temperatura (°C)' } }
            }
        }
    });
}

function renderBarChart(meses, lluviaMes) {
    const ctx = document.getElementById('chartBar').getContext('2d');
    if (window.barChart) {
        window.barChart.destroy();
    }
    
    // Obtener idioma actual para el título
    const currentLang = localStorage.getItem('preferredLanguage') || 'es';
    const chartTitle = translations && translations[currentLang] && translations[currentLang].barChartTitle 
        ? translations[currentLang].barChartTitle 
        : 'Precipitación Mensual Acumulada';
    
    const threshold = 20; // mm/mes (umbral de sequía)

    // --- MEJORA: Colores dinámicos para las barras ---
    const barColors = lluviaMes.map(value => 
        value < threshold ? 'rgba(220, 53, 69, 0.7)' : 'rgba(102, 126, 234, 0.78)' // Rojo si está por debajo, azul si no
    );

    window.barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: meses,
            datasets: [
                {
                    label: 'Lluvia mensual (mm)',
                    data: lluviaMes,
                    backgroundColor: barColors
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
            plugins: { 
                title: {
                    display: true,
                    text: chartTitle,
                    font: { size: 14, weight: 'bold' }
                },
                legend: { display: true }
            },
            scales: {
                x: { title: { display: true, text: 'Mes' } },
                y: { title: { display: true, text: 'Lluvia (mm)' } }
            }
        }
    });
}

/**
 * Calcula la regresión lineal simple
 * @param {Array} x - Valores independientes
 * @param {Array} y - Valores dependientes
 * @returns {Object} - {slope, intercept, r2}
 */
function calcularRegresionLineal(x, y) {
    const n = x.length;
    const sumX = x.reduce((a, b) => a + b, 0);
    const sumY = y.reduce((a, b) => a + b, 0);
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
    const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
    
    // Calcular pendiente (beta1) e intercepto (beta0)
    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;
    
    // Calcular R² (coeficiente de determinación)
    const yMean = sumY / n;
    const ssTotal = y.reduce((sum, yi) => sum + Math.pow(yi - yMean, 2), 0);
    const ssResidual = y.reduce((sum, yi, i) => sum + Math.pow(yi - (slope * x[i] + intercept), 2), 0);
    const r2 = 1 - (ssResidual / ssTotal);
    
    return { slope, intercept, r2 };
}

/**
 * Renderiza la gráfica de regresión lineal con predicción futura
 */
function renderRegressionChart(fechas, lluvia) {
    const ctx = document.getElementById('chartRegression').getContext('2d');
    if (window.regressionChart) {
        window.regressionChart.destroy();
    }
    
    // Obtener idioma actual para el título
    const currentLang = localStorage.getItem('preferredLanguage') || 'es';
    const chartTitle = translations && translations[currentLang] && translations[currentLang].regressionChart 
        ? translations[currentLang].regressionChart 
        : 'Regresión Lineal y Predicción de Precipitación';
    
    // Preparar datos: usar índices numéricos como x
    const n = fechas.length;
    const x = Array.from({length: n}, (_, i) => i);
    
    // Calcular regresión lineal
    const {slope, intercept, r2} = calcularRegresionLineal(x, lluvia);
    
    // Generar línea de regresión para datos históricos
    const lineaRegresion = x.map(xi => slope * xi + intercept);
    
    // Predicción futura (próximos 30 días)
    const diasFuturos = 30;
    const xFuturo = Array.from({length: diasFuturos}, (_, i) => n + i);
    const prediccionFutura = xFuturo.map(xi => Math.max(0, slope * xi + intercept));
    
    // Fechas futuras (aproximadas)
    const ultimaFecha = new Date(fechas[fechas.length - 1]);
    const fechasFuturas = xFuturo.map(i => {
        const fecha = new Date(ultimaFecha);
        fecha.setDate(fecha.getDate() + i - n + 1);
        return fecha.toISOString().split('T')[0];
    });
    
    // Combinar todas las etiquetas
    const todasLasFechas = [...fechas, ...fechasFuturas];
    
    window.regressionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: todasLasFechas,
            datasets: [
                {
                    label: 'Precipitación Real',
                    data: [...lluvia, ...Array(diasFuturos).fill(null)],
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderWidth: 2,
                    pointRadius: 1,
                    fill: true
                },
                {
                    label: 'Línea de Regresión',
                    data: [...lineaRegresion, ...Array(diasFuturos).fill(null)],
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    fill: false
                },
                {
                    label: `Predicción (30 días) - R²=${r2.toFixed(3)}`,
                    data: [...Array(n).fill(null), ...prediccionFutura],
                    borderColor: 'rgba(255, 206, 86, 1)',
                    backgroundColor: 'rgba(255, 206, 86, 0.2)',
                    borderWidth: 3,
                    borderDash: [10, 5],
                    pointRadius: 2,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: 8 },
            plugins: {
                title: {
                    display: true,
                    text: chartTitle,
                    font: { size: 14, weight: 'bold' }
                },
                legend: { display: true, position: 'top' },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) {
                                label += context.parsed.y.toFixed(2) + ' mm';
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: { 
                    title: { display: true, text: 'Fecha' },
                    ticks: { maxTicksLimit: 15 }
                },
                y: { 
                    title: { display: true, text: 'Precipitación (mm)' },
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Dibuja la gráfica del modelo matemático estacional R(t)
 * y resalta el mes actual.
 * @param {object} apiData - Los datos completos recibidos de la API.
 */
function dibujarModeloMatematico(apiData) {
    const canvas = document.getElementById('modeloGrafica');
    if (!canvas) return;
    
    // Configuración del canvas
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height); // Limpiar canvas previo

    // Funciones de escala
    function tToX(t) { return (t / 13) * width; } // <-- ESTA FUNCIÓN FALTABA
    function rToY(r) { return height - ((r + 0.5) / 1.5) * height; }

    // --- MEJORA: Dibujar cuadrícula y marcas numéricas ---
    ctx.strokeStyle = '#e0e0e0'; // Color claro para la cuadrícula
    ctx.fillStyle = '#666';      // Color para el texto de las marcas
    ctx.font = '10px Arial';
    ctx.lineWidth = 1;

    // Marcas y cuadrícula del Eje Y (Riesgo)
    const yMarkers = [0.0, 0.5, 1.0];
    ctx.textAlign = 'right';
    yMarkers.forEach(val => {
        const yPos = rToY(val); // Usamos la función de escala para la posición Y
        ctx.fillText(val.toFixed(1), tToX(0) - 8, yPos + 3);
        ctx.beginPath();
        ctx.moveTo(tToX(0), yPos);
        ctx.lineTo(tToX(13), yPos); // Línea de cuadrícula horizontal
        ctx.stroke();
    });

    // Marcas del Eje X (Meses)
    const xMarkers = [{t: 3, label: 'Mar'}, {t: 6, label: 'Jun'}, {t: 9, label: 'Sep'}, {t: 12, label: 'Dic'}];
    ctx.textAlign = 'center';
    xMarkers.forEach(marker => {
        const xPos = tToX(marker.t);
        ctx.fillText(marker.label, xPos, rToY(0) + 15);
    });

    // Dibujar ejes
    ctx.strokeStyle = '#ccc';
    ctx.beginPath();
    ctx.moveTo(tToX(0), rToY(0));
    ctx.lineTo(tToX(13), rToY(0));
    ctx.stroke();

    // --- INTERACCIÓN CON LA API ---
    // Obtener el mes actual (1-12) y marcarlo en la gráfica
    const mesActual = new Date().getMonth() + 1;


    // --- MEJORA: Dibujar la curva del Riesgo Real ---
    if (apiData.series && apiData.series.riesgo_diario && apiData.series.riesgo_diario.length > 0) {
        const riesgoDiario = apiData.series.riesgo_diario;
        
        // --- CORRECCIÓN: Lógica para dibujar la curva de los últimos 90 días ---
        const mesesACubrir = 3; // 90 días son aprox. 3 meses
        
        // 1. Dibujar el área sombreada
        ctx.beginPath();
        const firstPoint = { t: (mesActual - mesesACubrir), x: tToX(mesActual - mesesACubrir), y: rToY(riesgoDiario[0]/100) };
        ctx.moveTo(firstPoint.x, firstPoint.y);
        riesgoDiario.forEach((riesgo, i) => {
            const t = (mesActual - mesesACubrir) + (i / riesgoDiario.length) * mesesACubrir;
            const xPos = tToX(t);
            const yPos = rToY(riesgo / 100); // Convertir de % a 0-1
            ctx.lineTo(xPos, yPos);
        });
        // Cerrar el área por abajo
        const lastPointX = tToX(mesActual);
        ctx.lineTo(lastPointX, rToY(0)); // Bajar hasta el eje X
        ctx.lineTo(firstPoint.x, rToY(0)); // Ir al inicio por el eje X
        ctx.closePath();
        const gradient = ctx.createLinearGradient(0, 0, 0, height);
        gradient.addColorStop(0, 'rgba(220, 53, 69, 0.5)');
        gradient.addColorStop(1, 'rgba(220, 53, 69, 0.05)');
        ctx.fillStyle = gradient;
        ctx.fill();

        // 2. Dibujar la línea de la curva encima del área
        ctx.strokeStyle = 'rgba(220, 53, 69, 1)'; // Rojo más sólido
        ctx.lineWidth = 2;
        ctx.beginPath();
        riesgoDiario.forEach((riesgo, i) => {
            const t = (mesActual - mesesACubrir) + (i / riesgoDiario.length) * mesesACubrir;
            const xPos = tToX(t);
            const yPos = rToY(riesgo / 100);
            if (i === 0) ctx.moveTo(xPos, yPos); else ctx.lineTo(xPos, yPos);
        });
        ctx.stroke();
    }

    // Etiquetas
    ctx.fillStyle = '#000'; ctx.font = '12px Arial';
    ctx.textAlign = 'center';

    // Etiqueta Eje X
    ctx.fillText('Mes del Año', width / 2, height - 5);

    // Etiqueta Eje Y (rotada)
    ctx.save();
    ctx.translate(15, height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Índice de Riesgo', 0, 0);
    ctx.restore();
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
