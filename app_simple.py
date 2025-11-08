# --- Importación de librerías necesarias ---
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from datetime import date, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry

# --- COMIENZO DEL CÓDIGO DEL PROYECTO ---

# -------------------------------------------------
# 1. DATOS HISTÓRICOS (simulados para Chihuahua)
# -------------------------------------------------
# Precipitación mensual (mm) de enero a diciembre de varios años
# (En un proyecto real, esto vendría de SMN)
precipitacion_historica = [
    15, 10, 5, 20, 25, 30, 40, 35, 20, 10, 5, 0,   # Año 1: sequía severa
    20, 25, 30, 40, 50, 60, 70, 60, 40, 30, 20, 10, # Año 2: normal
    10, 5, 0, 15, 10, 20, 25, 20, 10, 5, 0, 0,      # Año 3: sequía
    # ... (agregar más datos reales en tu versión final)
]

# Etiquetas: 1 = sequía (precip < 20 mm/mes), 0 = normal
etiquetas_historicas = [] # Se crea una lista vacía para las etiquetas.
for p in precipitacion_historica: # Se itera sobre cada valor de precipitación histórica.
    etiquetas_historicas.append(1 if p < 20 else 0)

# -------------------------------------------------
# 2. FUNCIÓN: CÁLCULO DE LA DERIVADA (Cálculo Diferencial)
# -------------------------------------------------
def derivada_tendencia(datos):
    """
    Calcula la derivada aproximada (tasa de cambio) entre meses.
    Si la derivada es muy negativa, hay tendencia a sequía.
    Usa una aproximación simple de la derivada: f'(x) ≈ f(x) - f(x-1).
    """
    derivadas = [] # Lista para guardar las tasas de cambio.
    for i in range(1, len(datos)): # Itera desde el segundo elemento.
        # Derivada ≈ (f(x) - f(x-1)) / (x - (x-1)) = f(x) - f(x-1)
        deriv = datos[i] - datos[i-1] # Calcula la diferencia con el mes anterior.
        derivadas.append(deriv) # Añade la diferencia a la lista.
    
    if len(derivadas) >= 2: # Si hay al menos dos cambios calculados...
        # Devuelve el promedio de los últimos dos cambios para suavizar la tendencia.
        return (derivadas[-1] + derivadas[-2]) / 2
    return 0 # Si no hay suficientes datos, no hay tendencia.

# -------------------------------------------------
# 3. FUNCIÓN: ESTADÍSTICA MANUAL (Estadística)
# -------------------------------------------------
def regresion_lineal_simple(x, y):
    """
    Calcula los coeficientes de una regresión lineal simple (y = β0 + β1*x).
    """
    n = len(x) # Número de puntos de datos.
    sum_x = sum(x) # Suma de todos los valores de x.
    sum_y = sum(y) # Suma de todos los valores de y.
    sum_xy = sum(x[i] * y[i] for i in range(n)) # Suma de los productos de x e y.
    sum_x2 = sum(xi ** 2 for xi in x) # Suma de los cuadrados de x.

    # Fórmula para la pendiente (β1).
    beta1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    # Fórmula para el intercepto (β0).
    beta0 = (sum_y - beta1 * sum_x) / n
    return beta0, beta1 # Devuelve ambos coeficientes.

# "Entrena" un modelo de regresión lineal simple con los datos históricos para usarlo después.
beta0, beta1 = regresion_lineal_simple(precipitacion_historica, etiquetas_historicas)

# -------------------------------------------------
# 4. FUNCIÓN: ÁLGEBRA LINEAL (Mínimos Cuadrados desde cero)
# -------------------------------------------------
def transpuesta_matriz(A):
    """Devuelve la transpuesta de A"""
    # Itera sobre las columnas de A para convertirlas en las filas de la nueva matriz.
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))] 

def resolver_sistema_gauss_jordan(A, b):
    """
    Resuelve A*x = b usando eliminación de Gauss-Jordan (sin librerías).
    A: matriz cuadrada, b: vector.
    """
    n = len(A)
    # Crea la matriz aumentada [A | b] para resolver el sistema.
    M = [A[i] + [b[i]] for i in range(n)]

    # Proceso de eliminación Gauss-Jordan.
    for i in range(n): # Itera sobre cada fila (pivote).
        pivote = M[i][i] # El elemento en la diagonal es el pivote.
        if pivote == 0: continue # Si el pivote es 0, no se puede dividir (se salta).
        
        # Normaliza la fila del pivote para que el elemento pivote sea 1.
        for j in range(i, n + 1): # Itera sobre los elementos de la fila.
            M[i][j] /= pivote # Divide cada elemento por el pivote.
            
        # Elimina los otros elementos en la columna del pivote.
        for k in range(n): # Itera sobre todas las filas.
            if k != i: # Excepto la fila del pivote.
                factor = M[k][i] # El valor a eliminar.
                for j in range(i, n + 1): # Resta la fila del pivote (multiplicada por el factor) de la fila actual.
                    M[k][j] -= factor * M[i][j]

    # Extrae la solución (la última columna de la matriz aumentada).
    x = [M[i][n] for i in range(n)] # La solución está en la columna 'b' transformada.
    return x # Devuelve el vector de soluciones 'x'.

def modelo_algebra_lineal(precip_actual):
    """
    Usa álgebra lineal para predecir el riesgo resolviendo la "Ecuación Normal":
    (X^T * X) * β = X^T * y
    """
    # Crea la matriz de diseño X. Cada fila es [precipitación, 1] para el intercepto.
    X = [[p, 1] for p in precipitacion_historica]
    y = etiquetas_historicas  # El vector de resultados (0 o 1).

    # Calcula los componentes de la Ecuación Normal.
    Xt = transpuesta_matriz(X) # Transpuesta de X.
    # Multiplica X transpuesta por X.
    XtX = [[sum(Xt[i][k] * X[k][j] for k in range(len(X))) for j in range(len(X[0]))] for i in range(len(Xt))]
    # Multiplica X transpuesta por y.
    Xty = [sum(Xt[i][k] * y[k] for k in range(len(y))) for i in range(len(Xt))]

    try: # Intenta resolver el sistema.
        # Resuelve el sistema de ecuaciones (XtX) * β = Xty para encontrar los coeficientes β.
        beta = resolver_sistema_gauss_jordan(XtX, Xty)
        # Usa los coeficientes para hacer una predicción: riesgo = β0 * precip_actual + β1.
        prediccion = beta[0] * precip_actual + beta[1]
        # Asegura que el resultado esté entre 0 y 1, ya que es una probabilidad/riesgo.
        return max(0, min(1, prediccion))
    except: # Si hay un error (p.ej., matriz no invertible).
        return 0.5  # Devuelve un valor neutral como fallback.

# -------------------------------------------------
# 5. DATOS DE COORDENADAS DE MUNICIPIOS DE CHIHUAHUA
# -------------------------------------------------
municipios = {
    "Ahumada": {"lat": 30.58, "lon": -106.51},
    "Aldama": {"lat": 28.83, "lon": -105.91},
    "Allende": {"lat": 26.93, "lon": -105.41},
    "Aquiles Serdán": {"lat": 28.55, "lon": -105.95},
    "Ascensión": {"lat": 31.18, "lon": -107.98},
    "Bachíniva": {"lat": 28.78, "lon": -107.26},
    "Balleza": {"lat": 26.95, "lon": -106.38},
    "Batopilas": {"lat": 27.02, "lon": -107.73},
    "Bocoyna": {"lat": 27.75, "lon": -107.63},
    "Buenaventura": {"lat": 29.83, "lon": -107.48},
    "Camargo": {"lat": 27.68, "lon": -105.17},
    "Carichí": {"lat": 27.93, "lon": -107.05},
    "Casas Grandes": {"lat": 30.41, "lon": -107.95},
    "Coronado": {"lat": 26.75, "lon": -105.18},
    "Coyame del Sotol": {"lat": 29.68, "lon": -105.10},
    "La Cruz": {"lat": 27.86, "lon": -105.20},
    "Cuauhtémoc": {"lat": 28.40, "lon": -106.86},
    "Cusihuiriachi": {"lat": 28.18, "lon": -106.78},
    "Chihuahua": {"lat": 28.63, "lon": -106.08},
    "Chínipas": {"lat": 27.39, "lon": -108.53},
    "Delicias": {"lat": 28.19, "lon": -105.47},
    "Dr. Belisario Domínguez": {"lat": 28.13, "lon": -106.58},
    "Galeana": {"lat": 30.08, "lon": -107.63},
    "Santa Isabel": {"lat": 28.38, "lon": -106.38},
    "Gómez Farías": {"lat": 29.35, "lon": -107.73},
    "Gran Morelos": {"lat": 28.25, "lon": -106.58},
    "Guachochi": {"lat": 27.15, "lon": -107.28},
    "Guadalupe": {"lat": 31.08, "lon": -105.88},
    "Guadalupe y Calvo": {"lat": 26.09, "lon": -106.96},
    "Guazapares": {"lat": 27.23, "lon": -108.28},
    "Guerrero": {"lat": 28.55, "lon": -107.48},
    "Hidalgo del Parral": {"lat": 26.93, "lon": -105.66},
    "Huejotitán": {"lat": 27.03, "lon": -105.8},
    "Ignacio Zaragoza": {"lat": 29.68, "lon": -107.73},
    "Janos": {"lat": 30.88, "lon": -108.2},
    "Jiménez": {"lat": 27.13, "lon": -104.91},
    "Juárez": {"lat": 31.73, "lon": -106.48},
    "Julimes": {"lat": 28.41, "lon": -105.41},
    "López": {"lat": 26.98, "lon": -105.03},
    "Madera": {"lat": 29.18, "lon": -108.15},
    "Maguarichi": {"lat": 27.86, "lon": -107.93},
    "Manuel Benavides": {"lat": 29.08, "lon": -104.13},
    "Matachí": {"lat": 28.86, "lon": -107.73},
    "Matamoros": {"lat": 26.73, "lon": -105.58},
    "Meoqui": {"lat": 28.26, "lon": -105.48},
    "Morelos": {"lat": 26.58, "lon": -107.7},
    "Moris": {"lat": 28.1, "lon": -108.76},
    "Namiquipa": {"lat": 29.25, "lon": -107.41},
    "Nonoava": {"lat": 27.48, "lon": -106.71},
    "Nuevo Casas Grandes": {"lat": 30.41, "lon": -107.91},
    "Ocampo": {"lat": 28.0, "lon": -108.35},
    "Ojinaga": {"lat": 29.56, "lon": -104.41},
    "Praxedis G. Guerrero": {"lat": 31.36, "lon": -106.01},
    "Riva Palacio": {"lat": 28.53, "lon": -106.63},
    "Rosales": {"lat": 28.18, "lon": -105.56},
    "Rosario": {"lat": 27.33, "lon": -106.33},
    "San Francisco de Borja": {"lat": 27.93, "lon": -106.26},
    "San Francisco de Conchos": {"lat": 27.58, "lon": -105.38},
    "San Francisco del Oro": {"lat": 26.93, "lon": -105.85},
    "Santa Bárbara": {"lat": 26.78, "lon": -105.81},
    "Satevó": {"lat": 27.75, "lon": -106.25},
    "Saucillo": {"lat": 28.0, "lon": -105.28},
    "Temósachic": {"lat": 28.98, "lon": -108.03},
    "El Tule": {"lat": 27.08, "lon": -105.98},
    "Urique": {"lat": 27.21, "lon": -107.91},
    "Uruachi": {"lat": 27.86, "lon": -108.21},
    "Valle de Zaragoza": {"lat": 27.46, "lon": -105.81}
}

# -------------------------------------------------
# 6. FUNCIÓN SIMPLIFICADA PARA OBTENER DATOS (SIN API EXTERNA)
# -------------------------------------------------
def obtener_pronostico_precipitacion(municipio="Chihuahua"):
    """Obtiene los datos históricos de precipitación de los últimos 90 días desde Open-Meteo."""
    if municipio not in municipios:
        raise ValueError(f"Municipio '{municipio}' no encontrado en la base de datos.")
    
    coords = municipios[municipio]
    
    sesion_cache = requests_cache.CachedSession('.cache', expire_after=3600)
    sesion_reintentos = retry(sesion_cache, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=sesion_reintentos)

    url = "https://archive-api.open-meteo.com/v1/archive"
    
    fecha_final = date.today() - timedelta(days=1)
    fecha_inicio = fecha_final - timedelta(days=89)

    parametros = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "start_date": fecha_inicio.strftime('%Y-%m-%d'),
        "end_date": fecha_final.strftime('%Y-%m-%d'),
        "daily": "precipitation_sum",
    }
    respuestas = openmeteo.weather_api(url, params=parametros)
    respuesta = respuestas[0]

    datos_diarios = respuesta.Daily()
    precipitacion_diaria = datos_diarios.Variables(0).ValuesAsNumpy()

    mes1 = sum(precipitacion_diaria[0:30])
    mes2 = sum(precipitacion_diaria[30:60])
    mes3 = sum(precipitacion_diaria[60:90])
    
    return [mes1, mes2, mes3]

# -------------------------------------------------
# 7. FUNCIÓN PRINCIPAL: HERRAMIENTA DIGITAL
# -------------------------------------------------
def analizar_riesgo(municipio):
    """Orquesta el análisis y devuelve los resultados como un diccionario."""
    try:
        precip_reciente = obtener_pronostico_precipitacion(municipio)
        p3 = precip_reciente[-1]
    except Exception as e:
        # Si falla, devuelve un diccionario de error.
        return {"error": True, "message": str(e)}

    tendencia = derivada_tendencia(precip_reciente)
    prediccion_estadistica = beta0 + beta1 * p3
    prediccion_algebra = modelo_algebra_lineal(p3)

    # Convertimos la tendencia en un componente de riesgo entre 0 y 1.
    riesgo_tendencia = max(0, min(1, -tendencia / 10))

    # Promedio ponderado (dando más peso a la tendencia)
    riesgo = (0.4 * riesgo_tendencia + 0.3 * prediccion_estadistica + 0.3 * prediccion_algebra)

    if riesgo < 0.2:
        nivel = "Anormalmente Seco (D0)"
        accion = "Condición de sequedad. Puede ocasionar retraso en la siembra, limitado crecimiento de cultivos y riesgo de incendios."
        className = "risk-d0"
    elif riesgo < 0.4:
        nivel = "Sequía Moderada (D1)"
        accion = "Daños en cultivos/pastos, alto riesgo de incendios y bajos niveles en ríos. Se sugiere restricción voluntaria en el uso del agua."
        className = "risk-d1"
    elif riesgo < 0.6:
        nivel = "Sequía Severa (D2)"
        accion = "Pérdidas probables en cultivos/pastos, escasez de agua común. Se deben imponer restricciones en el uso del agua."
        className = "risk-d2"
    elif riesgo < 0.8:
        nivel = "Sequía Extrema (D3)"
        accion = "Pérdidas mayores en cultivos/pastos, riesgo extremo de incendios. Se generalizan las restricciones en el uso del agua."
        className = "risk-d3"
    else:
        nivel = "Sequía Excepcional (D4)"
        accion = "Pérdidas excepcionales y generalizadas, escasez total de agua. Probable situación de emergencia."
        className = "risk-d4"

    # Mapeo de clases para colores de progreso
    if riesgo < 0.2: progress_class = "progress-d0"
    elif riesgo < 0.4: progress_class = "progress-d1"
    elif riesgo < 0.6: progress_class = "progress-d2"
    elif riesgo < 0.8: progress_class = "progress-d3"
    else: progress_class = "progress-d4"

    # Devuelve un diccionario con todos los resultados, listo para ser convertido a JSON.
    return {
        "municipio": municipio,
        "nivel": nivel,
        "accion": accion,
        "className": className,
        "progressClass": progress_class, # Para la barra de progreso
        "riesgo": float(riesgo),
        "riesgoTendencia": float(riesgo_tendencia),
        "prediccionEstadistica": float(prediccion_estadistica),
        "prediccionAlgebra": float(prediccion_algebra)
    }

# -------------------------------------------------
# 8. APLICACIÓN FLASK
# -------------------------------------------------
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analizar', methods=['GET'])
def analizar_api():
    municipio = request.args.get('municipio', 'Chihuahua')
    resultados = analizar_riesgo(municipio)
    return jsonify(resultados)

@app.route('/api/dashboard/<municipio>', methods=['GET'])
def obtener_datos_dashboard(municipio):
    """Obtiene datos reales para el dashboard."""
    try:
        if municipio not in municipios:
            return jsonify({"error": True, "message": f"Municipio '{municipio}' no encontrado"})
        
        coords = municipios[municipio]
        
        sesion_cache = requests_cache.CachedSession('.cache', expire_after=3600)
        sesion_reintentos = retry(sesion_cache, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=sesion_reintentos)

        url = "https://archive-api.open-meteo.com/v1/archive"
        
        fecha_final = date.today() - timedelta(days=1)
        fecha_inicio = fecha_final - timedelta(days=89)

        parametros = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "start_date": fecha_inicio.strftime('%Y-%m-%d'),
            "end_date": fecha_final.strftime('%Y-%m-%d'),
            "daily": "precipitation_sum,temperature_2m_mean",
        }
        
        respuestas = openmeteo.weather_api(url, params=parametros)
        respuesta = respuestas[0]

        datos_diarios_api = respuesta.Daily()
        precipitacion_diaria = datos_diarios_api.Variables(0).ValuesAsNumpy()
        temperatura_diaria = datos_diarios_api.Variables(1).ValuesAsNumpy()
        
        fechas = [(fecha_inicio + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(90)]

        # Datos para el gráfico de dispersión
        datos_dispersion = [{"x": float(temp), "y": float(precip)} for temp, precip in zip(temperatura_diaria, precipitacion_diaria)]

        # Datos para el gráfico de líneas
        datos_lineas = [{"fecha": f, "precipitacion": float(p)} for f, p in zip(fechas, precipitacion_diaria)]

        # Datos para el gráfico de barras mensual
        precipitacion_mensual = [
            sum(precipitacion_diaria[0:30]),
            sum(precipitacion_diaria[30:60]),
            sum(precipitacion_diaria[60:90])
        ]
        meses_labels = [
            (fecha_inicio + timedelta(days=15)).strftime('%B'),
            (fecha_inicio + timedelta(days=45)).strftime('%B'),
            (fecha_inicio + timedelta(days=75)).strftime('%B')
        ]

        return jsonify({
            "datos_dispersion": datos_dispersion,
            "datos_lineas": datos_lineas,
            "datos_barras_mensual": {"labels": meses_labels, "data": precipitacion_mensual}
        })
        
    except Exception as e:
        return jsonify({"error": True, "message": str(e)})

if __name__ == "__main__":
    print("Iniciando aplicación Flask...")
    app.run(debug=True, port=5001)
