/**
 * Sistema de Traducciones
 * Español, Tarahumara y Rarámuri
 */

const translations = {
    es: {
        // Header
        title: "Tierra que habla",
        subtitle: "Sistema de análisis meteorológico en Chihuahua",
        
        // Form
        selectMunicipality: "Selecciona un municipio:",
        chooseMunicipality: "-- Elige un municipio --",
        analyzeButton: "Analizar Sequía",
        loadingMessage: "Consultando datos meteorológicos...",
        
        // Results
        analysisFor: "Análisis para",
        droughtIndex: "Índice de Sequía:",
        category: "Categoría:",
        
        // Climate Data
        climateData: "Datos Climáticos (Promedio últimos 90 días)",
        precipitation: "Precipitación",
        temperature: "Temperatura",
        evapotranspiration: "Evapotranspiración",
        
        // Recommendations
        recommendations: "Recomendaciones",
        forFarmers: "Para Agricultores",
        forRanchers: "Para Ganaderos",
        
        // Charts
        charts: "Gráficas",
        lineChartTitle: "Precipitación Diaria (Últimos 90 Días)",
        scatterChartTitle: "Relación Precipitación vs Temperatura",
        barChartTitle: "Precipitación Mensual Acumulada",
        regressionChart: "Regresión Lineal y Predicción",
        riskEvolutionTitle: "Evolución del Índice de Sequía",
        
        // Drought Categories
        droughtCategory: {
            "D0": "Anormalmente Seco",
            "D1": "Sequía Moderada",
            "D2": "Sequía Severa",
            "D3": "Sequía Extrema",
            "D4": "Sequía Excepcional"
        },
        
        // Recommendations
        recommendations: {
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
        }
    },
    
    tara: {
        // Header (Tarahumara)
        title: "Onorúa Nokála",
        subtitle: "Chihuahua rejói kusírami bewá",
        
        // Form
        selectMunicipality: "Mapú rejói sirámi:",
        chooseMunicipality: "-- Mapú sirámi gasíwa --",
        analyzeButton: "Bewá Kusí Ra'íchari",
        loadingMessage: "Kusírami bewá napáka...",
        
        // Results
        analysisFor: "Bewáchi rejói",
        droughtIndex: "Kusí nimá:",
        category: "Ma'sá:",
        
        // Climate Data
        climateData: "Kusírami Bewá (90 osí rejói)",
        precipitation: "Yubá",
        temperature: "Waséame",
        evapotranspiration: "Yubá Ré'mi",
        
        // Recommendations
        recommendations: "Kusí Mapu Níwara",
        forFarmers: "Teóchi Niwá",
        forRanchers: "Chíbachi Niwá",
        
        // Charts
        charts: "Machí Bewá",
        lineChartTitle: "Yubá Osí Osí (90 Osí Rejói)",
        scatterChartTitle: "Yubá gu Waséame Machí",
        barChartTitle: "Yubá Machí Malá",
        regressionChart: "Yubá Bewá Kusírami",
        riskEvolutionTitle: "Kusí Nimá Rejói Bewá",
        
        // Drought Categories
        droughtCategory: {
            "D0": "Kusí Sipó Osíchi",
            "D1": "Kusí Machí",
            "D2": "Kusí Marí",
            "D3": "Kusí Majá",
            "D4": "Kusí Ko'á Majá"
        },
        
        // Recommendations (Tarahumara)
        recommendations: {
            "D0": {
                agricultores: "Osákami yubá bewá. Teonári machí kusí namá yubá gasí osíchi. Machí kusírami bewá yubá rejói namá.",
                ganaderos: "Yubá chipá gasíwa. Bordos machí yubá gasí osá. Tinacos machí kusí bewá gasíwa rejói."
            },
            "D1": {
                agricultores: "Teó machí kusírami bewá. Kusírami namá yubá sipó gasí machí osá. Yubá rejói bewá gasíwa.",
                ganaderos: "Chíba kusírami machí. Chipá kusí osá machí namá bewá. Kusírami gasí osá rejói."
            },
            "D2": {
                agricultores: "Yubá chipá sipó gasí. Namá kusí yubá bewá chipá osá. Teónari gasíwa yubá namá.",
                ganaderos: "Chipá kusí bewá machí. Teó kusírami namá bewá gasí. Chíba kusí machí rejói osá."
            },
            "D3": {
                agricultores: "Kusírami teó namá gasí. Yubá kusí osá bewá machí. Kusírami gasí rejói namá yubá.",
                ganaderos: "Chíba kusírami gasí bewá. Kusí namá chipá machí osá. Yubá bewá gasí rejói machí."
            },
            "D4": {
                agricultores: "Teó kusí bewá namá. Kusírami machí namá gasí osá. Bewá rejói kusí chipá namá.",
                ganaderos: "Chíba kusí machí namá. Kusírami bewá gasí rejói. Chíba chipá machí kusí gasíwa."
            }
        }
    },
    
    rara: {
        // Header (Rarámuri - variante dialectal)
        title: "Onorúa Chokeamé",
        subtitle: "Chihuahua rejói oné kusírami",
        
        // Form
        selectMunicipality: "Mapú rejói esíwa:",
        chooseMunicipality: "-- Mapú esíwa sikára --",
        analyzeButton: "Oné Ra'íchari Bewá",
        loadingMessage: "Kusírami napáka anérame...",
        
        // Results
        analysisFor: "Bewáchi",
        droughtIndex: "Oné nimá:",
        category: "Rejói:",
        
        // Climate Data
        climateData: "Kusírami (90 osíbara)",
        precipitation: "Yubá Ewá",
        temperature: "Waséame Rejói",
        evapotranspiration: "Yubá Ré'asá",
        
        // Recommendations
        recommendations: "Mapu Kusí Níwara",
        forFarmers: "Teóchi Bewá",
        forRanchers: "Chíba Mapu",
        
        // Charts
        charts: "Machí Rejói",
        lineChartTitle: "Yubá Osí Osí (90 Osí Oné)",
        scatterChartTitle: "Yubá gu Waséame Oné",
        barChartTitle: "Yubá Machí Malá",
        regressionChart: "Yubá Bewá Oné",
        riskEvolutionTitle: "Oné Nimá Rejói Bewá",
        
        // Drought Categories
        droughtCategory: {
            "D0": "Oné Sipó",
            "D1": "Oné Machíwa",
            "D2": "Oné Maríwa",
            "D3": "Oné Ko'á",
            "D4": "Oné Ko'á Majá"
        },
        
        // Recommendations (Rarámuri)
        recommendations: {
            "D0": {
                agricultores: "Yubá bewá osákami. Teónari machí oné namá yubá gasí. Machí kusírami yubá rejói bewá.",
                ganaderos: "Yubá chipá namá gasí. Bordos oné yubá machí gasí. Tinacos kusí bewá machí rejói."
            },
            "D1": {
                agricultores: "Teó oné kusírami bewá. Yubá sipó machí namá gasí osá. Kusírami bewá gasí rejói.",
                ganaderos: "Chíba oné machí kusírami. Chipá bewá machí namá gasí. Oné kusírami rejói gasí."
            },
            "D2": {
                agricultores: "Yubá chipá bewá gasí. Namá oné yubá chipá osá. Teónari gasíwa yubá bewá.",
                ganaderos: "Chipá oné bewá machí. Teó kusírami bewá gasí namá. Chíba oné rejói machí."
            },
            "D3": {
                agricultores: "Oné teó namá kusírami. Yubá bewá machí gasí osá. Kusírami rejói yubá namá.",
                ganaderos: "Chíba oné kusírami bewá. Namá chipá machí gasí. Yubá bewá rejói machí gasí."
            },
            "D4": {
                agricultores: "Teó oné bewá kusírami. Machí namá gasí osá bewá. Rejói kusí chipá namá.",
                ganaderos: "Chíba oné machí kusírami. Bewá gasí rejói namá. Chíba chipá oné gasíwa."
            }
        }
    }
};

// Función para cambiar el idioma
function changeLanguage(lang) {
    const elements = document.querySelectorAll('[data-i18n]');
    
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });
    
    // Guardar preferencia de idioma
    localStorage.setItem('preferredLanguage', lang);
    
    // Actualizar categorías de sequía si están visibles
    const nivelValue = document.getElementById('nivelValue');
    if (nivelValue && nivelValue.dataset.category) {
        const category = nivelValue.dataset.category;
        if (translations[lang].droughtCategory[category]) {
            nivelValue.textContent = `${category} - ${translations[lang].droughtCategory[category]}`;
        }
    }
    
    // Actualizar recomendaciones si están visibles
    const recAgricultores = document.getElementById('recAgricultores');
    const recGanaderos = document.getElementById('recGanaderos');
    
    if (recAgricultores && recAgricultores.dataset.category) {
        const category = recAgricultores.dataset.category;
        if (translations[lang].recommendations && translations[lang].recommendations[category]) {
            recAgricultores.textContent = translations[lang].recommendations[category].agricultores;
            recGanaderos.textContent = translations[lang].recommendations[category].ganaderos;
        }
    }
    
    // Actualizar títulos de las gráficas si están visibles
    if (window.lineChart && translations[lang].lineChartTitle) {
        window.lineChart.options.plugins.title.text = translations[lang].lineChartTitle;
        window.lineChart.update();
    }
    
    if (window.scatterChart && translations[lang].scatterChartTitle) {
        window.scatterChart.options.plugins.title.text = translations[lang].scatterChartTitle;
        window.scatterChart.update();
    }
    
    if (window.barChart && translations[lang].barChartTitle) {
        window.barChart.options.plugins.title.text = translations[lang].barChartTitle;
        window.barChart.update();
    }
    
    if (window.regressionChart && translations[lang].regressionChart) {
        window.regressionChart.options.plugins.title.text = translations[lang].regressionChart;
        window.regressionChart.update();
    }
}

// Inicializar selector de idioma
function initLanguageSelector() {
    const languageSelect = document.getElementById('languageSelect');
    
    // Cargar idioma guardado
    const savedLanguage = localStorage.getItem('preferredLanguage') || 'es';
    languageSelect.value = savedLanguage;
    changeLanguage(savedLanguage);
    
    // Event listener para cambio de idioma
    languageSelect.addEventListener('change', (e) => {
        changeLanguage(e.target.value);
    });
}

// Exportar funciones
window.translations = translations;
window.changeLanguage = changeLanguage;
window.initLanguageSelector = initLanguageSelector;
