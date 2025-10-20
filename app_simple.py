# --- Importación de librerías necesarias ---
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import random
from datetime import date, timedelta

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
def media(datos):
    """Calcula el promedio de una lista de números."""
    return sum(datos) / len(datos) # Suma de los elementos dividida por la cantidad de elementos.

def desviacion_estandar(datos):
    """Calcula la desviación estándar de una lista de números."""
    m = media(datos) # Primero calcula la media.
    varianza = sum((x - m) ** 2 for x in datos) / len(datos) # Calcula la varianza.
    return varianza ** 0.5 # La desviación estándar es la raíz cuadrada de la varianza.

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
# 5. DATOS DE COORDENADAS DE ESTADOS MEXICANOS
# -------------------------------------------------
coordenadas_estados = {
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

# -------------------------------------------------
# 6. FUNCIÓN SIMPLIFICADA PARA OBTENER DATOS (SIN API EXTERNA)
# -------------------------------------------------
def obtener_pronostico_precipitacion(estado="Chihuahua"):
    """Genera datos simulados de precipitación para evitar problemas de conectividad."""
    if estado not in coordenadas_estados:
        raise ValueError(f"Estado '{estado}' no encontrado en la base de datos.")
    
    print(f"Generando datos simulados de precipitación para {estado}...")
    
    # Genera datos simulados basados en el estado
    # Estados del norte (más secos)
    estados_norte = ["Chihuahua", "Sonora", "Coahuila", "Nuevo León", "Tamaulipas", "Durango", "Zacatecas", "San Luis Potosí", "Aguascalientes", "Baja California", "Baja California Sur"]
    
    if estado in estados_norte:
        # Estados del norte: menos precipitación
        mes1 = random.uniform(5, 25)
        mes2 = random.uniform(3, 20)
        mes3 = random.uniform(0, 15)
    else:
        # Estados del sur: más precipitación
        mes1 = random.uniform(20, 60)
        mes2 = random.uniform(15, 50)
        mes3 = random.uniform(10, 40)
    
    print(f"Precipitación simulada para {estado} (mm): Mes 1={mes1:.1f}, Mes 2={mes2:.1f}, Mes 3={mes3:.1f}")
    return [mes1, mes2, mes3]

# -------------------------------------------------
# 7. FUNCIÓN PRINCIPAL: HERRAMIENTA DIGITAL
# -------------------------------------------------
def main(estado="Chihuahua"):
    """Orquesta el análisis y devuelve los resultados como un diccionario."""
    try:
        precip_reciente = obtener_pronostico_precipitacion(estado)
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

    # Devuelve un diccionario con todos los resultados, listo para ser convertido a JSON.
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
    estado = request.args.get('estado', 'Chihuahua')
    resultados = main(estado)
    return jsonify(resultados)

@app.route('/api/dashboard/<estado>', methods=['GET'])
def obtener_datos_dashboard(estado):
    """Genera datos simulados para el dashboard."""
    try:
        if estado not in coordenadas_estados:
            return jsonify({"error": True, "message": f"Estado '{estado}' no encontrado"})
        
        # Genera datos simulados para 90 días
        datos_diarios = []
        datos_semanales = []
        
        # Genera datos diarios simulados
        for i in range(90):
            fecha = (date.today() - timedelta(days=89-i)).strftime('%Y-%m-%d')
            # Simula variación en la precipitación
            if i < 30:
                precip = random.uniform(0, 5)  # Mes 1: menos lluvia
            elif i < 60:
                precip = random.uniform(0, 8)  # Mes 2: lluvia moderada
            else:
                precip = random.uniform(0, 3)  # Mes 3: poca lluvia
            
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
                "periodo": f"{(date.today() - timedelta(days=89)).strftime('%Y-%m-%d')} a {(date.today() - timedelta(days=1)).strftime('%Y-%m-%d')}"
            }
        })
        
    except Exception as e:
        return jsonify({"error": True, "message": str(e)})

@app.route('/api/analizar-manual', methods=['POST'])
def analizar_manual_api():
    try:
        datos = request.get_json()
        precipitacion_manual = datos.get('precipitacion', [])
        
        if len(precipitacion_manual) != 3:
            return jsonify({"error": True, "message": "Se requieren exactamente 3 valores de precipitación"})
        
        # Usar los datos manuales para el análisis
        p3 = precipitacion_manual[-1]  # Último mes
        
        tendencia = derivada_tendencia(precipitacion_manual)
        prediccion_estadistica = beta0 + beta1 * p3
        prediccion_algebra = modelo_algebra_lineal(p3)
        
        # Convertimos la tendencia en un componente de riesgo entre 0 y 1.
        riesgo_tendencia = max(0, min(1, -tendencia / 10))
        
        # Promedio ponderado (dando más peso a la tendencia)
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
        
        return jsonify({
            "nivel": nivel,
            "accion": accion,
            "className": className,
            "riesgo": float(riesgo),
            "riesgoTendencia": float(riesgo_tendencia),
            "prediccionEstadistica": float(prediccion_estadistica),
            "prediccionAlgebra": float(prediccion_algebra),
            "datos_usados": precipitacion_manual
        })
        
    except Exception as e:
        return jsonify({"error": True, "message": str(e)})

if __name__ == "__main__":
    print("Iniciando aplicación Flask...")
    print("La aplicación usará datos simulados para evitar problemas de conectividad.")
    app.run(debug=True, port=5001)
