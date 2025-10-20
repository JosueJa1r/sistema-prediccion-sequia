from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

# Datos históricos simulados
precipitacion_historica = [15, 10, 5, 20, 25, 30, 40, 35, 20, 10, 5, 0, 20, 25, 30, 40, 50, 60, 70, 60, 40, 30, 20, 10, 10, 5, 0, 15, 10, 20, 25, 20, 10, 5, 0, 0]
etiquetas_historicas = [1 if p < 20 else 0 for p in precipitacion_historica]

# Estados disponibles
estados = {
    "Chihuahua": {"lat": 28.64, "lon": -106.09},
    "Sonora": {"lat": 29.09, "lon": -110.95},
    "Coahuila": {"lat": 27.30, "lon": -101.95},
    "Nuevo León": {"lat": 25.67, "lon": -100.31},
    "Tamaulipas": {"lat": 24.27, "lon": -98.84},
    "Durango": {"lat": 24.02, "lon": -104.67},
    "Zacatecas": {"lat": 22.77, "lon": -102.58},
    "San Luis Potosí": {"lat": 22.15, "lon": -100.98},
    "Aguascalientes": {"lat": 21.88, "lon": -102.29},
    "Jalisco": {"lat": 20.66, "lon": -103.35},
    "Guanajuato": {"lat": 21.02, "lon": -101.26},
    "Querétaro": {"lat": 20.59, "lon": -100.39},
    "Hidalgo": {"lat": 20.09, "lon": -98.76},
    "México": {"lat": 19.43, "lon": -99.13},
    "Puebla": {"lat": 19.04, "lon": -98.20},
    "Tlaxcala": {"lat": 19.31, "lon": -98.24},
    "Morelos": {"lat": 18.68, "lon": -99.10},
    "Ciudad de México": {"lat": 19.43, "lon": -99.13},
    "Veracruz": {"lat": 19.17, "lon": -96.13},
    "Tabasco": {"lat": 17.84, "lon": -92.62},
    "Campeche": {"lat": 19.85, "lon": -90.53},
    "Yucatán": {"lat": 20.71, "lon": -89.09},
    "Quintana Roo": {"lat": 19.18, "lon": -88.48},
    "Chiapas": {"lat": 16.75, "lon": -93.11},
    "Oaxaca": {"lat": 17.07, "lon": -96.72},
    "Guerrero": {"lat": 17.44, "lon": -99.88},
    "Michoacán": {"lat": 19.70, "lon": -101.19},
    "Colima": {"lat": 19.24, "lon": -103.72},
    "Nayarit": {"lat": 21.75, "lon": -104.85},
    "Sinaloa": {"lat": 25.17, "lon": -107.49},
    "Baja California": {"lat": 30.84, "lon": -115.28},
    "Baja California Sur": {"lat": 26.04, "lon": -111.66}
}

def derivada_tendencia(datos):
    """Calcula la derivada aproximada entre meses."""
    derivadas = []
    for i in range(1, len(datos)):
        deriv = datos[i] - datos[i-1]
        derivadas.append(deriv)
    
    if len(derivadas) >= 2:
        return (derivadas[-1] + derivadas[-2]) / 2
    return 0

def media(datos):
    """Calcula el promedio de una lista de números."""
    return sum(datos) / len(datos)

def regresion_lineal_simple(x, y):
    """Calcula los coeficientes de una regresión lineal simple."""
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(xi ** 2 for xi in x)

    beta1 = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    beta0 = (sum_y - beta1 * sum_x) / n
    return beta0, beta1

# Entrena el modelo
beta0, beta1 = regresion_lineal_simple(precipitacion_historica, etiquetas_historicas)

def obtener_datos_simulados(estado):
    """Genera datos simulados de precipitación."""
    if estado not in estados:
        raise ValueError(f"Estado '{estado}' no encontrado.")
    
    # Estados del norte (más secos)
    estados_norte = ["Chihuahua", "Sonora", "Coahuila", "Nuevo León", "Tamaulipas", "Durango", "Zacatecas", "San Luis Potosí", "Aguascalientes", "Baja California", "Baja California Sur"]
    
    if estado in estados_norte:
        mes1 = random.uniform(5, 25)
        mes2 = random.uniform(3, 20)
        mes3 = random.uniform(0, 15)
    else:
        mes1 = random.uniform(20, 60)
        mes2 = random.uniform(15, 50)
        mes3 = random.uniform(10, 40)
    
    return [mes1, mes2, mes3]

def analizar_riesgo(estado):
    """Analiza el riesgo de sequía para un estado."""
    try:
        precip_reciente = obtener_datos_simulados(estado)
        p3 = precip_reciente[-1]
    except Exception as e:
        return {"error": True, "message": str(e)}

    tendencia = derivada_tendencia(precip_reciente)
    prediccion_estadistica = beta0 + beta1 * p3
    prediccion_algebra = 0.5  # Valor simplificado

    riesgo_tendencia = max(0, min(1, -tendencia / 10))
    riesgo = (0.4 * riesgo_tendencia + 0.3 * prediccion_estadistica + 0.3 * prediccion_algebra)

    if riesgo < 0.3:
        nivel = "BAJO"
        accion = "Monitoree el pronóstico semanal."
        className = "risk-low"
    elif riesgo < 0.7:
        nivel = "MEDIO"
        accion = "Retrase la siembra 15 días o use cultivos resistentes a sequía."
        className = "risk-medium"
    else:
        nivel = "ALTO"
        accion = "¡ALERTA! Active plan de contingencia: almacene agua y forraje."
        className = "risk-high"

    return {
        "estado": estado,
        "nivel": nivel,
        "accion": accion,
        "className": className,
        "riesgo": float(riesgo),
        "riesgoTendencia": float(riesgo_tendencia),
        "prediccionEstadistica": float(prediccion_estadistica),
        "prediccionAlgebra": float(prediccion_algebra)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analizar', methods=['GET'])
def analizar_api():
    estado = request.args.get('estado', 'Chihuahua')
    resultados = analizar_riesgo(estado)
    return jsonify(resultados)

@app.route('/api/dashboard/<estado>', methods=['GET'])
def obtener_datos_dashboard(estado):
    """Genera datos simulados para el dashboard."""
    try:
        if estado not in estados:
            return jsonify({"error": True, "message": f"Estado '{estado}' no encontrado"})
        
        # Genera datos simulados para 90 días
        datos_diarios = []
        datos_semanales = []
        
        for i in range(90):
            fecha = f"2024-{(i//30)+1:02d}-{(i%30)+1:02d}"
            precip = random.uniform(0, 5)
            datos_diarios.append({
                "fecha": fecha,
                "precipitacion": round(precip, 1)
            })
        
        # Genera datos semanales
        for i in range(0, 90, 7):
            semana_precip = sum(datos_diarios[j]["precipitacion"] for j in range(i, min(i+7, 90)))
            semana_fecha = datos_diarios[i]["fecha"]
            datos_semanales.append({
                "fecha": semana_fecha,
                "precipitacion": round(semana_precip, 1)
            })
        
        # Calcula estadísticas
        precipitacion_total = sum(item["precipitacion"] for item in datos_diarios)
        precipitacion_promedio = precipitacion_total / 90
        precipitacion_maxima = max(item["precipitacion"] for item in datos_diarios)
        dias_sin_lluvia = sum(1 for item in datos_diarios if item["precipitacion"] == 0)
        
        return jsonify({
            "estado": estado,
            "datos_diarios": datos_diarios,
            "datos_semanales": datos_semanales,
            "estadisticas": {
                "precipitacion_total": round(precipitacion_total, 1),
                "precipitacion_promedio": round(precipitacion_promedio, 1),
                "precipitacion_maxima": round(precipitacion_maxima, 1),
                "dias_sin_lluvia": dias_sin_lluvia,
                "periodo": "2024-01-01 a 2024-03-31"
            }
        })
        
    except Exception as e:
        return jsonify({"error": True, "message": str(e)})

# Para Vercel
def handler(request):
    return app(request.environ, lambda *args: None)
