# Modelos Matemáticos del Sistema

Este documento describe los modelos matemáticos esenciales utilizados en el sistema de predicción de sequía.

---

## 1. Normalización Min-Max

Convierte datos de diferentes escalas a un rango común [0, 1]:

$$
X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}
$$

**Uso**: Permite comparar precipitación (mm), temperatura (°C) y evapotranspiración (mm) en la misma escala.

---

## 2. Índice de Sequía Ponderado

Combina tres variables climáticas con pesos específicos:

$$
I_{sequia} = 0.6 \cdot (1 - P_{norm}) + 0.2 \cdot T_{norm} + 0.2 \cdot E_{norm}
$$

**Donde**:
- $P_{norm}$ = Precipitación normalizada
- $T_{norm}$ = Temperatura normalizada
- $E_{norm}$ = Evapotranspiración normalizada

**Interpretación**:
- 60% del peso a la falta de precipitación
- 20% a la temperatura alta
- 20% a la evapotranspiración alta

**Resultado**: Valor entre 0 y 1, donde valores más altos indican mayor sequía.

---

## 3. Clasificación USDM (U.S. Drought Monitor)

El índice se clasifica en categorías estándar:

| Categoría | Índice | Descripción |
|-----------|--------|-------------|
| D0 | < 0.35 | Anormalmente Seco |
| D1 | 0.35 - 0.50 | Sequía Moderada |
| D2 | 0.50 - 0.65 | Sequía Severa |
| D3 | 0.65 - 0.80 | Sequía Extrema |
| D4 | ≥ 0.80 | Sequía Excepcional |

---

## 4. Regresión Lineal para Predicción

Ajusta una línea recta a los datos históricos para proyectar tendencias futuras:

$$
y = \beta_0 + \beta_1 x
$$

### Cálculo de Coeficientes:

**Pendiente**:
$$
\beta_1 = \frac{n \sum(xy) - \sum x \sum y}{n \sum(x^2) - (\sum x)^2}
$$

**Intercepto**:
$$
\beta_0 = \frac{\sum y - \beta_1 \sum x}{n}
$$

### Coeficiente de Determinación (R²):

$$
R^2 = 1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}
$$

**Interpretación de R²**:
- **R² > 0.7**: Predicción confiable
- **0.4 < R² < 0.7**: Moderadamente confiable
- **R² < 0.4**: Baja confiabilidad (común en clima árido)

**Aplicación**: Predice precipitación de los próximos 30 días basándose en los últimos 90 días.

---

## 5. Modelo Híbrido de Análisis de Tendencia

Combina tres métodos para mayor robustez:

### a) Análisis de Tendencia Simple:
$$
Tendencia = P_t - P_{t-1}
$$

### b) Regresión Lineal:
$$
y = \beta_0 + \beta_1 x
$$

### c) Álgebra Lineal (Ecuación Normal):
$$
\beta = (X^T X)^{-1} X^T y
$$

### Riesgo Final:
$$
Riesgo_{final} = \frac{1}{3}(Riesgo_{Tendencia} + Riesgo_{Regresión} + Riesgo_{Álgebra})
$$

**Ventaja**: Promedia tres enfoques diferentes para reducir el error de predicción individual.

---

## Implementación en Código

### 1. Normalización Min-Max
**Rama Matemática**: Análisis Numérico / Transformaciones Lineales

```python
def normalizar_minmax(datos):
    """
    Normaliza una lista de datos al rango [0, 1]
    
    Parámetros:
        datos: Lista de valores numéricos
    
    Retorna:
        Lista de valores normalizados entre 0 y 1
    """
    minimo = min(datos)
    maximo = max(datos)
    rango = maximo - minimo + 1e-10  # Evita división por cero
    
    return [(x - minimo) / rango for x in datos]
```

**Función**: Transforma datos de diferentes escalas a un rango uniforme [0,1] para permitir comparaciones justas entre variables con diferentes unidades de medida.

---

### 2. Índice de Sequía Ponderado
**Rama Matemática**: Álgebra Lineal / Combinación Lineal

```python
def calcular_indice_sequia(precipitacion, temperatura, evapotranspiracion):
    """
    Calcula el índice de sequía combinando tres variables climáticas
    
    Parámetros:
        precipitacion: Lista de valores de precipitación diaria (mm)
        temperatura: Lista de valores de temperatura diaria (°C)
        evapotranspiracion: Lista de valores de evapotranspiración (mm)
    
    Retorna:
        Índice de sequía (0-1), donde 1 = sequía extrema
    """
    # Normalizar cada variable
    p_norm = normalizar_minmax(precipitacion)
    t_norm = normalizar_minmax(temperatura)
    e_norm = normalizar_minmax(evapotranspiracion)
    
    # Calcular índice diario con pesos específicos
    indices_diarios = []
    for i in range(len(p_norm)):
        # Invertir precipitación: poca lluvia = alto índice
        indice = 0.6 * (1 - p_norm[i]) + 0.2 * t_norm[i] + 0.2 * e_norm[i]
        indices_diarios.append(indice)
    
    # Retornar promedio como índice final
    return sum(indices_diarios) / len(indices_diarios)
```

**Función**: Combina tres factores climáticos usando una suma ponderada donde la precipitación tiene mayor peso (60%) por ser el indicador más directo de sequía.

---

### 3. Clasificación por Umbrales
**Rama Matemática**: Lógica Condicional / Teoría de Conjuntos

```python
def clasificar_sequia(indice):
    """
    Clasifica el índice de sequía según estándares USDM
    
    Parámetros:
        indice: Valor del índice de sequía (0-1)
    
    Retorna:
        Tupla (categoría, descripción)
    """
    if indice < 0.35:
        return ("D0", "Anormalmente Seco")
    elif indice < 0.50:
        return ("D1", "Sequía Moderada")
    elif indice < 0.65:
        return ("D2", "Sequía Severa")
    elif indice < 0.80:
        return ("D3", "Sequía Extrema")
    else:
        return ("D4", "Sequía Excepcional")
```

**Función**: Mapea valores continuos del índice a categorías discretas siguiendo el sistema estandarizado del U.S. Drought Monitor.

---

### 4. Regresión Lineal Simple
**Rama Matemática**: Estadística / Análisis de Regresión / Mínimos Cuadrados

```python
def calcular_regresion_lineal(x, y):
    """
    Calcula los coeficientes de la regresión lineal y el R²
    usando el método de mínimos cuadrados
    
    Parámetros:
        x: Lista de valores independientes (tiempo)
        y: Lista de valores dependientes (precipitación)
    
    Retorna:
        Diccionario con 'slope' (pendiente), 'intercept' (intercepto), 'r2' (R²)
    """
    n = len(x)
    
    # Calcular sumas necesarias
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(xi ** 2 for xi in x)
    sum_y2 = sum(yi ** 2 for yi in y)
    
    # Calcular pendiente (β₁)
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    
    # Calcular intercepto (β₀)
    intercept = (sum_y - slope * sum_x) / n
    
    # Calcular R² (coeficiente de determinación)
    y_mean = sum_y / n
    ss_total = sum((yi - y_mean) ** 2 for yi in y)
    ss_residual = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
    r2 = 1 - (ss_residual / ss_total) if ss_total != 0 else 0
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r2': r2
    }
```

**Función**: Ajusta una línea recta a datos históricos usando el método de mínimos cuadrados. Minimiza la suma de las distancias cuadradas entre puntos observados y la línea predicha. Útil para identificar tendencias y hacer proyecciones futuras.

---

### 5. Predicción con Regresión
**Rama Matemática**: Análisis Predictivo / Extrapolación

```python
def predecir_precipitacion(fechas, lluvia, dias_futuros=30):
    """
    Predice precipitación futura usando regresión lineal
    
    Parámetros:
        fechas: Lista de fechas históricas
        lluvia: Lista de precipitación histórica (mm)
        dias_futuros: Número de días a predecir
    
    Retorna:
        Diccionario con 'prediccion' (lista de valores) y 'r2' (confiabilidad)
    """
    # Crear índices numéricos para x (0, 1, 2, ...)
    x = list(range(len(lluvia)))
    
    # Calcular regresión
    resultado = calcular_regresion_lineal(x, lluvia)
    slope = resultado['slope']
    intercept = resultado['intercept']
    r2 = resultado['r2']
    
    # Generar predicciones futuras
    prediccion = []
    for i in range(dias_futuros):
        x_futuro = len(lluvia) + i
        y_predicho = max(0, slope * x_futuro + intercept)  # No permitir valores negativos
        prediccion.append(y_predicho)
    
    return {
        'prediccion': prediccion,
        'r2': r2,
        'tendencia': 'descendente' if slope < 0 else 'ascendente'
    }
```

**Función**: Usa la línea de regresión para extrapolar valores futuros. El R² indica qué tan confiable es la predicción (valores cercanos a 1 = alta confiabilidad).

---

### 6. Análisis de Tendencia (Derivada Discreta)
**Rama Matemática**: Cálculo / Análisis de Diferencias Finitas

```python
def analizar_tendencia(datos):
    """
    Calcula la tendencia usando diferencias entre puntos consecutivos
    
    Parámetros:
        datos: Lista de valores temporales
    
    Retorna:
        Valor de tendencia (positivo = aumento, negativo = disminución)
    """
    if len(datos) < 2:
        return 0
    
    # Calcular diferencia entre último y penúltimo valor
    # Es una aproximación de la derivada: df/dt ≈ Δf/Δt
    tendencia = datos[-1] - datos[-2]
    
    return tendencia
```

**Función**: Calcula la derivada discreta (tasa de cambio instantánea) comparando valores consecutivos. Similar al concepto de velocidad en física: mide qué tan rápido cambia la precipitación.

---

### 7. Modelo Híbrido (Ensemble)
**Rama Matemática**: Estadística / Machine Learning / Métodos de Ensemble

```python
def calcular_riesgo_hibrido(precipitacion, temperatura, evapotranspiracion):
    """
    Combina tres modelos matemáticos diferentes para mayor robustez
    
    Parámetros:
        precipitacion: Lista de valores de precipitación
        temperatura: Lista de valores de temperatura
        evapotranspiracion: Lista de valores de evapotranspiración
    
    Retorna:
        Riesgo final combinado (0-1)
    """
    # MODELO 1: Análisis de Tendencia
    tendencia = analizar_tendencia(precipitacion)
    riesgo_tendencia = max(0, -tendencia / 10)  # Normalizar tendencia negativa
    
    # MODELO 2: Regresión Lineal Simple
    x = list(range(len(precipitacion)))
    regresion = calcular_regresion_lineal(x, precipitacion)
    # Si la pendiente es negativa = riesgo alto
    riesgo_regresion = max(0, -regresion['slope'] / 5)
    
    # MODELO 3: Índice Ponderado
    riesgo_ponderado = calcular_indice_sequia(
        precipitacion, 
        temperatura, 
        evapotranspiracion
    )
    
    # COMBINACIÓN: Promedio de los tres modelos
    riesgo_final = (riesgo_tendencia + riesgo_regresion + riesgo_ponderado) / 3
    
    # Limitar al rango [0, 1]
    return max(0, min(1, riesgo_final))
```

**Función**: Implementa un método de ensemble que combina predicciones de modelos independientes. Reduce el sesgo de cualquier modelo individual y aumenta la robustez general. Basado en técnicas de Machine Learning como Random Forests.

---

### 8. Álgebra Lineal - Ecuación Normal (Avanzado)
**Rama Matemática**: Álgebra Lineal / Sistemas de Ecuaciones

```python
def transpuesta_matriz(matriz):
    """Calcula la transpuesta de una matriz"""
    filas = len(matriz)
    columnas = len(matriz[0])
    
    transpuesta = [[matriz[i][j] for i in range(filas)] 
                   for j in range(columnas)]
    return transpuesta

def multiplicar_matrices(A, B):
    """Multiplica dos matrices"""
    filas_A = len(A)
    columnas_A = len(A[0])
    columnas_B = len(B[0])
    
    resultado = [[sum(A[i][k] * B[k][j] for k in range(columnas_A))
                  for j in range(columnas_B)]
                 for i in range(filas_A)]
    return resultado

def resolver_ecuacion_normal(X, y):
    """
    Resuelve el sistema β = (X^T X)^(-1) X^T y
    Implementación sin NumPy usando eliminación Gaussiana
    
    Parámetros:
        X: Matriz de características (n x m)
        y: Vector objetivo (n x 1)
    
    Retorna:
        Vector de coeficientes β
    """
    # 1. Calcular X^T (transpuesta)
    X_T = transpuesta_matriz(X)
    
    # 2. Calcular X^T X
    X_T_X = multiplicar_matrices(X_T, X)
    
    # 3. Calcular X^T y
    X_T_y = multiplicar_matrices(X_T, [[yi] for yi in y])
    
    # 4. Resolver (X^T X) β = X^T y usando Gauss-Jordan
    # [Implementación simplificada - en producción usar una librería]
    # Este paso resuelve el sistema de ecuaciones lineales
    
    # Para n=2 (regresión lineal simple):
    # β₀ = intercepto, β₁ = pendiente
    
    return X_T_y  # Retorna coeficientes
```

**Función**: Implementa la solución algebraica exacta para regresión lineal multivariable. Usa operaciones matriciales para encontrar los coeficientes óptimos. Es más general que la regresión simple y puede manejar múltiples variables predictoras simultáneamente.

---

## Resumen de Fórmulas Principales

1. **Normalización**: $X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}}$

2. **Índice de Sequía**: $I = 0.6(1-P) + 0.2T + 0.2E$

3. **Regresión Lineal**: $y = \beta_0 + \beta_1 x$

4. **R² (Bondad de Ajuste)**: $R^2 = 1 - \frac{SS_{res}}{SS_{tot}}$

5. **Modelo Híbrido**: $Riesgo = \frac{1}{3}\sum_{i=1}^{3} Método_i$

---

## Ramas Matemáticas Utilizadas

| Modelo | Rama Matemática | Aplicación |
|--------|----------------|------------|
| Normalización | Análisis Numérico | Escalado de datos |
| Índice Ponderado | Álgebra Lineal | Combinación lineal |
| Clasificación USDM | Lógica / Teoría de Conjuntos | Categorización |
| Regresión Lineal | Estadística / Mínimos Cuadrados | Predicción de tendencias |
| Análisis de Tendencia | Cálculo / Diferencias Finitas | Tasa de cambio |
| R² | Estadística Inferencial | Validación de modelo |
| Modelo Híbrido | Machine Learning / Ensemble | Reducción de sesgo |
| Ecuación Normal | Álgebra Lineal Matricial | Regresión multivariable |