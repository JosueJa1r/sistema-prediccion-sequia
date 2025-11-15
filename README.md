# Sistema de Predicción de Sequía - Chihuahua

Sistema de análisis de sequía para municipios de Chihuahua utilizando datos de Open-Meteo. Implementa modelos matemáticos en **Python puro** (sin NumPy) para clasificar sequía según categorías USDM (D0–D4).

## Instalación

```bash
pip install -r requirements.txt
```

**Dependencias:**
- Flask==2.3.3
- Flask-Cors==4.0.0  
- requests>=2.31.0

## Cómo Ejecutar

### 1. Servidor Web
```powershell
py api.py
```
Accede a: **http://127.0.0.1:5000**

### 2. Módulo CLI
```powershell
py analisis_sequia.py --precip 12 --temp 30 --marg 0.8 --json
```

### 3. Análisis de Municipios
```powershell
py analizar_municipios.py
```

## Endpoints de la API

### `GET /api/municipios`
Lista de todos los municipios de Chihuahua.

### `GET /api/analizar?municipio=Chihuahua`
Análisis de sequía para un municipio.

**Parámetros:**
- `municipio` (required): Nombre del municipio
- `marg` (optional): Índice de marginación (0-1)

**Respuesta:**
```json
{
  "municipio": "Chihuahua",
  "indice_sequia": 78.0,
  "categoria": "D3",
  "nombre_categoria": "Sequía Extrema",
  "datos": {
    "precipitacion_promedio": 2.1,
    "temperatura_promedio": 20.5,
    "evapotranspiracion_promedio": 4.8
  }
}
```

## Modelos Matemáticos

### 1. Índice de Sequía Ponderado

$$I_{sequia} = 0.6 \cdot (1 - P_{norm}) + 0.2 \cdot T_{norm} + 0.2 \cdot E_{norm}$$

**Pesos:**
- 60% Precipitación
- 20% Temperatura
- 20% Evapotranspiración

### 2. Normalización (Min-Max)

```python
normalized = [(x - min_val) / (max_val - min_val + 1e-10) for x in datos]
```

### 3. Clasificación USDM

| Categoría | Umbral      | Descripción       |
|-----------|-------------|-------------------|
| D0        | < 0.35      | Anormalmente Seco |
| D1        | 0.35–0.50   | Sequía Moderada   |
| D2        | 0.50–0.65   | Sequía Severa     |
| D3        | 0.65–0.80   | Sequía Extrema    |
| D4        | ≥ 0.80      | Sequía Excepcional|

### 4. Modelo Predictivo Híbrido

Combina:
- **Tendencia:** $P_t - P_{t-1}$
- **Regresión Lineal:** $y = \beta_0 + \beta_1 x$
- **Álgebra Lineal:** Gauss-Jordan sin librerías

$$Riesgo = \frac{1}{3}(Tendencia + Regresion + AlgebraLineal)$$

## Estructura del Proyecto

```
app/
├── api.py                    # Backend Flask
├── analisis_sequia.py        # Módulo de modelos matemáticos
├── analizar_municipios.py    # Script de análisis masivo
├── requirements.txt          # Dependencias Python
├── README.md                 # Este archivo
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
└── __pycache__/
```

## Fuente de Datos

- **API:** Open-Meteo Archive (https://archive-api.open-meteo.com/)
- **Variables:** precipitation_sum, temperature_2m_mean, et0_fao_evapotranspiration
- **Período:** Últimos 90 días

## Características Clave

✓ API REST en Flask  
✓ Interfaz web interactiva  
✓ 75 municipios de Chihuahua  
✓ Python puro (sin NumPy)  
✓ Modelos matemáticos educativos  
✓ Clasificación USDM (D0–D4)  
✓ Gráficos con Chart.js  

## Notas

- D3 es la categoría más frecuente en Chihuahua (clima árido)
- Los datos tienen 1 día de rezago para evitar incompletos
- Disponible en http://127.0.0.1:5000 durante ejecución

## Licencia

Uso educativo e investigativo.

---

**Última actualización:** 15 de noviembre de 2024
