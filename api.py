from flask import Flask, jsonify, request  # Núcleo de Flask: crear la aplicación, devolver respuestas JSON y acceder a datos de la petición
from flask_cors import CORS  # Habilita CORS (Cross-Origin Resource Sharing) para que el frontend pueda llamar a la API desde otro origen
from datetime import date, timedelta  # Utilidades de fechas para calcular rangos (inicio/fin) en consultas históricas
import requests  # Cliente HTTP usado para consultar la API de Open-Meteo
import os  # Utilidades del sistema operativo (rutas, variables de entorno) utilizadas por la aplicación
from analisis_sequia import calcular_riesgo_modelo

# Funciones auxiliares para operaciones matemáticas (sin NumPy)
def _min(lista):
    """Retorna el mínimo de una lista."""
    return min(lista) if lista else 0

def _max(lista):
    """Retorna el máximo de una lista."""
    return max(lista) if lista else 0

def _mean(lista):
    """Retorna la media (promedio) de una lista."""
    return sum(lista) / len(lista) if lista else 0

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

MUNICIPIOS = {
    "Ahumada": {"lat": 30.5833, "lon": -106.5167},
    "Aldama": {"lat": 28.8500, "lon": -105.4764},
    "Allende": {"lat": 27.0167, "lon": -105.4167},
    "Aquiles Serdán": {"lat": 28.5333, "lon": -106.0167},
    "Ascensión": {"lat": 31.3340, "lon": -107.4950},
    "Bachíniva": {"lat": 28.7833, "lon": -107.4333},
    "Balleza": {"lat": 26.9667, "lon": -106.3333},
    "Batopilas de Manuel Gómez Morín": {"lat": 27.0333, "lon": -107.5936},
    "Bocoyna": {"lat": 27.7667, "lon": -107.6167},
    "Buenaventura": {"lat": 30.0500, "lon": -107.5667},
    "Camargo": {"lat": 27.6800, "lon": -105.1700},
    "Carichí": {"lat": 27.9167, "lon": -107.2167},
    "Casas Grandes": {"lat": 30.3833, "lon": -107.9500},
    "Chihuahua": {"lat": 28.6300, "lon": -106.0800},
    "Chínipas": {"lat": 27.3500, "lon": -108.6000},
    "Coronado": {"lat": 27.0167, "lon": -105.2833},
    "Coyame del Sotol": {"lat": 29.5333, "lon": -105.0000},
    "Cuauhtémoc": {"lat": 28.4000, "lon": -106.8600},
    "Cusihuiriachi": {"lat": 28.2500, "lon": -106.8833},
    "Delicias": {"lat": 28.1900, "lon": -105.4700},
    "Dr. Belisario Domínguez": {"lat": 28.1167, "lon": -107.3833},
    "Galeana": {"lat": 30.0833, "lon": -107.6333},
    "Gómez Farías": {"lat": 29.3500, "lon": -107.7500},
    "Gran Morelos": {"lat": 28.0833, "lon": -106.4333},
    "Guachochi": {"lat": 27.0500, "lon": -107.1500},
    "Guadalupe y Calvo": {"lat": 26.0667, "lon": -106.9500},
    "Guadalupe D.B.": {"lat": 31.5000, "lon": -106.1167},
    "Guazapares": {"lat": 27.3000, "lon": -108.3000},
    "Guerrero": {"lat": 28.9167, "lon": -107.5500},
    "Hidalgo del Parral": {"lat": 26.9300, "lon": -105.6600},
    "Huejotitán": {"lat": 26.8000, "lon": -106.0667},
    "Ignacio Zaragoza": {"lat": 29.7333, "lon": -107.6333},
    "Janos": {"lat": 30.9000, "lon": -108.2000},
    "Jiménez": {"lat": 27.1833, "lon": -104.9167},
    "Juárez": {"lat": 31.7300, "lon": -106.4800},
    "Julimes": {"lat": 28.4167, "lon": -105.4000},
    "La Cruz": {"lat": 27.8167, "lon": -105.2833},
    "López": {"lat": 27.2667, "lon": -105.1500},
    "Madera": {"lat": 29.2000, "lon": -108.2333},
    "Maguarichi": {"lat": 28.1500, "lon": -108.3167},
    "Manuel Benavides": {"lat": 29.2833, "lon": -103.9667},
    "Matachí": {"lat": 28.7833, "lon": -107.8833},
    "Matamoros": {"lat": 26.8000, "lon": -105.4167},
    "Meoqui": {"lat": 28.2667, "lon": -105.4833},
    "Morelos": {"lat": 27.0833, "lon": -108.1333},
    "Moris": {"lat": 28.2833, "lon": -108.8167},
    "Namiquipa": {"lat": 29.1333, "lon": -107.4167},
    "Nonoava": {"lat": 27.2000, "lon": -106.6667},
    "Nuevo Casas Grandes": {"lat": 30.4333, "lon": -107.9167},
    "Ocampo": {"lat": 28.2000, "lon": -108.2167},
    "Ojinaga": {"lat": 29.5667, "lon": -104.4167},
    "Praxédis G. Guerrero": {"lat": 31.4500, "lon": -106.0167},
    "Riva Palacio": {"lat": 28.6000, "lon": -106.5833},
    "Rosales": {"lat": 28.2000, "lon": -105.5500},
    "Rosario": {"lat": 27.4667, "lon": -106.1833},
    "San Francisco de Borja": {"lat": 27.6000, "lon": -106.2833},
    "San Francisco de Conchos": {"lat": 27.5333, "lon": -105.4500},
    "San Francisco del Oro": {"lat": 26.9000, "lon": -105.9500},
    "Santa Bárbara": {"lat": 26.8333, "lon": -105.8167},
    "Satevó": {"lat": 27.9500, "lon": -106.0000},
    "Saucillo": {"lat": 28.0000, "lon": -105.2833},
    "Santa Isabel": {"lat": 28.3833, "lon": -106.3167},
    "Temosachic": {"lat": 28.6000, "lon": -107.8167},
    "El Tule": {"lat": 27.2333, "lon": -105.9000},
    "Urique": {"lat": 27.0667, "lon": -108.1500},
    "Uruachi": {"lat": 28.1667, "lon": -108.5333},
    "Valle de Zaragoza": {"lat": 27.6500, "lon": -105.7333},
}

def obtener_datos_meteo(municipio, dias=90):
    if municipio not in MUNICIPIOS:
        raise ValueError(f"Municipio '{municipio}' no encontrado")
    coords = MUNICIPIOS[municipio]
    fecha_fin = date.today() - timedelta(days=1)
    fecha_inicio = fecha_fin - timedelta(days=dias)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "start_date": fecha_inicio.strftime('%Y-%m-%d'),
        "end_date": fecha_fin.strftime('%Y-%m-%d'),
        "daily": ["precipitation_sum", "temperature_2m_mean", "et0_fao_evapotranspiration"],
        "timezone": "auto"
    }
    print(f"[API] Consultando Open-Meteo para {municipio}...")
    respuesta = requests.get(url, params=params)
    respuesta.raise_for_status()
    datos = respuesta.json()
    datos_diarios = datos["daily"]
    return {
        "precipitacion": [float(x) for x in datos_diarios["precipitation_sum"]],
        "temperatura": [float(x) for x in datos_diarios["temperature_2m_mean"]],
        "evapotranspiracion": [float(x) for x in datos_diarios["et0_fao_evapotranspiration"]],
        "fechas": datos_diarios["time"]
    }

def calcular_indice_sequia(precipitacion, temperatura, evapotranspiracion):
    """
    Calcula índice de sequía usando normalización min-max sin NumPy.
    
    Fórmula: I = 0.6 * (1 - P_norm) + 0.2 * T_norm + 0.2 * E_norm
    """
    # Obtener mínimos y máximos
    min_precip = _min(precipitacion)
    max_precip = _max(precipitacion)
    min_temp = _min(temperatura)
    max_temp = _max(temperatura)
    min_evap = _min(evapotranspiracion)
    max_evap = _max(evapotranspiracion)
    
    # Normalizar cada serie usando min-max (rango 0-1)
    precip_normalizada = [
        (x - min_precip) / (max_precip - min_precip + 1e-10) 
        for x in precipitacion
    ]
    temp_normalizada = [
        (x - min_temp) / (max_temp - min_temp + 1e-10) 
        for x in temperatura
    ]
    evap_normalizada = [
        (x - min_evap) / (max_evap - min_evap + 1e-10) 
        for x in evapotranspiracion
    ]
    
    # Aplicar fórmula ponderada: 60% precip, 20% temp, 20% evap
    indice_valores = [
        0.6 * (1 - precip_normalizada[i]) + 0.2 * temp_normalizada[i] + 0.2 * evap_normalizada[i]
        for i in range(len(precipitacion))
    ]
    
    # Retornar el promedio
    return _mean(indice_valores)

@app.route('/')
def index():
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({"mensaje": "API de Sequía - Endpoints disponibles", "endpoints": ["GET / - Interfaz web", "GET /api/municipios - Lista de municipios", "GET /api/analizar?municipio=Chihuahua - Análisis de sequía"]})

@app.route('/api/municipios')
def listar_municipios():
    return jsonify({"municipios": list(MUNICIPIOS.keys())})


@app.route('/api/analizar_detalle')
def analizar_detalle():
    """Devuelve las series crudas (para depuración)"""
    municipio = request.args.get('municipio', 'Chihuahua')
    if municipio not in MUNICIPIOS:
        return jsonify({"error": f"Municipio '{municipio}' no encontrado"}), 400
    datos = obtener_datos_meteo(municipio)
    return jsonify({
        "fechas": datos["fechas"],
        "precipitacion": [float(x) for x in datos["precipitacion"]],
        "temperatura": [float(x) for x in datos["temperatura"]],
        "evapotranspiracion": [float(x) for x in datos["evapotranspiracion"]]
    })

@app.route('/api/analizar')
def analizar_sequia():
    try:
        municipio = request.args.get('municipio', 'Chihuahua')
        if municipio not in MUNICIPIOS:
            return jsonify({"error": f"Municipio '{municipio}' no encontrado"}), 400
        print(f"[API] Analizando: {municipio}")
        datos = obtener_datos_meteo(municipio)
        indice = calcular_indice_sequia(datos["precipitacion"], datos["temperatura"], datos["evapotranspiracion"])
        # Llamada al modelo adicional del archivo adjunto (opcional)
        marg_param = request.args.get('marg')
        try:
            marg_val = float(marg_param) if marg_param is not None else None
        except Exception:
            marg_val = None
        try:
            mean_precip = _mean(datos["precipitacion"])
            mean_temp = _mean(datos["temperatura"])
            historia = {
                'precipitacion': datos['precipitacion'],
                'temperatura': datos['temperatura']
            }
            modelo_res = calcular_riesgo_modelo(mean_precip, mean_temp, marg=marg_val, historia=historia)
        except Exception as _e:
            modelo_res = None
        
        # Mapear índice numérico a categoría USDM (D0-D4)
        # Umbrales ajustados para climatología árida
        # Rango típico en Chihuahua: 0.5 - 0.8
        if indice < 0.35:
            nivel_riesgo = "D0"
            nombre_nivel = "Anormalmente Seco"
        elif indice < 0.50:
            nivel_riesgo = "D1"
            nombre_nivel = "Sequía Moderada"
        elif indice < 0.65:
            nivel_riesgo = "D2"
            nombre_nivel = "Sequía Severa"
        elif indice < 0.80:
            nivel_riesgo = "D3"
            nombre_nivel = "Sequía Extrema"
        else:
            nivel_riesgo = "D4"
            nombre_nivel = "Sequía Excepcional"
        
        # Preparar series diarias para las gráficas (ya son listas)
        fechas = datos["fechas"]
        lluvia_lista = datos["precipitacion"]
        temperatura_lista = datos["temperatura"]
        evapotranspiracion_lista = datos["evapotranspiracion"]

        # Calcular promedio mensual de lluvia (suma por mes)
        from collections import defaultdict
        import datetime

        mensual = defaultdict(float)
        dias_por_mes = defaultdict(int)
        for f, l in zip(fechas, lluvia_lista):
            try:
                dt = datetime.datetime.strptime(f, "%Y-%m-%d")
            except Exception:
                # si el formato es distinto, intentar parseo flexible
                dt = datetime.date.fromisoformat(f)
            key = dt.strftime("%Y-%m")
            mensual[key] += l
            dias_por_mes[key] += 1

        # Construir lista ordenada de meses
        meses_ordenados = sorted(mensual.keys())
        promedio_mensual = []
        for m in meses_ordenados:
            # Usamos la suma total de lluvia del mes (mm)
            promedio_mensual.append({"mes": m, "lluvia_mm": round(mensual[m], 2)})

        print(f"[API] Resultado: índice={indice:.2f}, categoría={nivel_riesgo} ({nombre_nivel})")
        return jsonify({
            "success": True,
            "municipio": municipio,
            "indice_sequia": round(indice * 100, 1),
            "categoria": nivel_riesgo,
            "nombre_categoria": nombre_nivel,
            "modelo": {
                "riesgo_modelo": round(modelo_res['riesgo'] * 100, 1) if modelo_res else None,
                "categoria_modelo": modelo_res['categoria'] if modelo_res else None,
                "nombre_categoria_modelo": modelo_res['nombre_categoria'] if modelo_res else None
            },
            "datos": {
                "precipitacion_promedio": _mean(datos["precipitacion"]),
                "temperatura_promedio": _mean(datos["temperatura"]),
                "evapotranspiracion_promedio": _mean(datos["evapotranspiracion"])
            },
            "series": {
                "fechas": fechas,
                "lluvia_mm": lluvia_lista,
                "temperatura_c": temperatura_lista,
                "evapotranspiracion_mm": evapotranspiracion_lista
            },
            "promedio_mensual": promedio_mensual
        })
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("API DE SEQUÍA - OPEN-METEO")
    print("=" * 60)
    print("\nMunicipios disponibles:", len(MUNICIPIOS))
    print("\nIniciando servidor en http://127.0.0.1:5000")
    print("\nPrueba los endpoints:")
    print("  - GET /api/municipios")
    print("  - GET /api/analizar?municipio=Chihuahua")
    print("\n" + "=" * 60 + "\n")
    app.run(debug=False, port=5000, host='0.0.0.0', use_reloader=False)
