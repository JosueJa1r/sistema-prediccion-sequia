"""Módulo de análisis y modelo predictivo (refactorizado desde el archivo adjunto).

Provee funciones puras y una función pública `calcular_riesgo_modelo`
que devuelve un diccionario con `riesgo` (0-1), `categoria` (D0..D4)
y `nombre_categoria`.
"""
from typing import List, Optional, Dict, Any


def derivada_tendencia(datos: List[float]) -> float:
    """Derivada simple: diferencia entre los últimos dos puntos.
    Devuelve 0 si no hay suficientes datos."""
    if not datos or len(datos) < 2:
        return 0.0
    return float(datos[-1] - datos[-2])


def media(datos: List[float]) -> float:
    if not datos:
        return 0.0
    return sum(datos) / len(datos)


def regresion_lineal_simple(x: List[float], y: List[float]):
    """Regresión lineal simple (sin librerías): devuelve (beta0, beta1).
    Si no es posible calcular, devuelve (0, 0)."""
    n = len(x)
    if n == 0:
        return 0.0, 0.0
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(x[i] * y[i] for i in range(n))
    sum_x2 = sum(xi ** 2 for xi in x)
    denom = n * sum_x2 - sum_x ** 2
    if denom == 0:
        return 0.0, 0.0
    beta1 = (n * sum_xy - sum_x * sum_y) / denom
    beta0 = (sum_y - beta1 * sum_x) / n
    return beta0, beta1


def transpuesta_matriz(A):
    return [[A[j][i] for j in range(len(A))] for i in range(len(A[0]))]


def resolver_sistema_gauss_jordan(A, b):
    """Resuelve A*x = b mediante Gauss-Jordan (precario, sin pivotado avanzado)."""
    n = len(A)
    # matriz aumentada
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for i in range(n):
        if abs(M[i][i]) < 1e-12:
            for k in range(i + 1, n):
                if abs(M[k][i]) > 1e-12:
                    M[i], M[k] = M[k], M[i]
                    break
        if abs(M[i][i]) < 1e-12:
            continue
        pivote = M[i][i]
        for j in range(i, n + 1):
            M[i][j] /= pivote
        for k in range(n):
            if k != i and abs(M[k][i]) > 1e-12:
                factor = M[k][i]
                for j in range(i, n + 1):
                    M[k][j] -= factor * M[i][j]
    return [M[i][n] for i in range(n)]


def modelo_algebra_lineal(precip: float, temp: float, marg: float,
                         X: Optional[List[List[float]]] = None,
                         y: Optional[List[float]] = None) -> float:
    """Modelo multivariable simple. Si no se proporcionan X,y usa regla de respaldo.
    Devuelve valor en [0,1]."""
    # Datos de ejemplo mínimos (pueden reemplazarse con historia)
    if X is None or y is None or len(X) < 3:
        if precip < 20 and marg > 0.7:
            return 0.9
        elif precip < 30:
            return 0.5
        else:
            return 0.1

    # Añadir columna de 1s para el intercepto
    X_con_const = [fila + [1] for fila in X]
    Xt = transpuesta_matriz(X_con_const)

    # XtX y Xty
    n_cols = len(X_con_const[0])
    XtX = [[sum(Xt[i][k] * X_con_const[k][j] for k in range(len(X_con_const)))
            for j in range(n_cols)] for i in range(n_cols)]
    Xty = [sum(Xt[i][k] * y[k] for k in range(len(y))) for i in range(n_cols)]
    try:
        beta = resolver_sistema_gauss_jordan(XtX, Xty)
        # beta order: coef_0..coef_n-1, intercept last
        pred = 0.0
        for i in range(len(beta) - 1):
            if i == 0:
                pred += beta[i] * precip
            elif i == 1:
                pred += beta[i] * temp
            elif i == 2:
                pred += beta[i] * marg
            else:
                # si hay más columnas, ignorarlas por ahora
                pred += beta[i] * 0
        pred += beta[-1]
        return max(0.0, min(1.0, pred))
    except Exception:
        return 0.5


def _clasificar_por_umbral(riesgo: float) -> Dict[str, str]:
    # Usamos los mismos umbrales ajustados que el API principal
    if riesgo < 0.35:
        return {"categoria": "D0", "nombre": "Anormalmente Seco"}
    elif riesgo < 0.50:
        return {"categoria": "D1", "nombre": "Sequía Moderada"}
    elif riesgo < 0.65:
        return {"categoria": "D2", "nombre": "Sequía Severa"}
    elif riesgo < 0.80:
        return {"categoria": "D3", "nombre": "Sequía Extrema"}
    else:
        return {"categoria": "D4", "nombre": "Sequía Excepcional"}


def calcular_riesgo_modelo(precip: float, temp: float, marg: Optional[float] = None,
                          historia: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Función pública que combina tres métodos (diferencial,
    regresión simple y álgebra lineal) y devuelve dict con:
    - riesgo: float en [0,1]
    - categoria, nombre_categoria

    Parámetros:
    - precip, temp: valores actuales (float)
    - marg: índice de marginación entre 0 y 1 (si no se provee, se usa 0.5)
    - historia: opcional, dict con claves 'precipitacion' y 'temperatura' como listas
    """
    if marg is None:
        marg = 0.5

    # Tendencia: usar la historia si existe
    tendencia = 0.0
    if historia and 'precipitacion' in historia and len(historia['precipitacion']) >= 2:
        tendencia = derivada_tendencia(list(historia['precipitacion']))

    # Estadística: regresión simple si hay historia
    pred_estad = 0.5
    if historia and 'precipitacion' in historia:
        precip_hist = [float(x) for x in historia['precipitacion']]
        # construir variable objetivo binaria simple (ejemplo): sequía si p < 20
        y = [1 if p < 20 else 0 for p in precip_hist]
        x = list(range(len(precip_hist)))
        beta0, beta1 = regresion_lineal_simple(x, y)
        pred_estad = beta0 + beta1 * len(precip_hist)  # predicción para el último índice
        # acotar
        pred_estad = max(0.0, min(1.0, pred_estad))

    # Álgebra lineal
    X = None
    y = None
    if historia and 'precipitacion' in historia and 'temperatura' in historia:
        precip_hist = [float(x) for x in historia['precipitacion']]
        temp_hist = [float(x) for x in historia['temperatura']]
        # construir X mínimo: [precip, temp, marg]
        n = min(len(precip_hist), len(temp_hist))
        X = [[precip_hist[i], temp_hist[i], marg] for i in range(n)]
        # objetivo mock: 1 si precip < 20
        y = [1 if precip_hist[i] < 20 else 0 for i in range(n)]

    pred_alg = modelo_algebra_lineal(precip, temp, marg, X=X, y=y)

    # combinar predicciones (0-1)
    # tendencia negativa (caída) incrementa sequía → usamos -tendencia/10 como en el adjunto
    riesgo = (max(0.0, -tendencia / 10.0) + pred_estad + pred_alg) / 3.0
    riesgo = max(0.0, min(1.0, riesgo))

    clas = _clasificar_por_umbral(riesgo)
    return {
        'riesgo': float(riesgo),
        'categoria': clas['categoria'],
        'nombre_categoria': clas['nombre']
    }


def format_result(res: Dict[str, Any]) -> str:
    return (
        f"Riesgo: {res['riesgo']:.3f} (categoria {res['categoria']} - {res['nombre_categoria']})"
    )


def _parse_comma_floats(s: Optional[str]) -> Optional[list]:
    if s is None:
        return None
    try:
        parts = [p.strip() for p in s.split(',') if p.strip()]
        return [float(x) for x in parts]
    except Exception:
        return None


def main_cli():
    """Interfaz de línea de comandos para usar calcular_riesgo_modelo desde terminal.

    Modos:
    - Si se pasan --precip y --temp se calcula y muestra resultado.
    - Si no se pasan, entra en modo interactivo pidiendo valores por teclado.
    """
    import argparse
    import json

    parser = argparse.ArgumentParser(description='Calculador de riesgo de sequía (modelo simple)')
    parser.add_argument('--precip', type=float, help='Precipitación actual (mm)')
    parser.add_argument('--temp', type=float, help='Temperatura actual (°C)')
    parser.add_argument('--marg', type=float, help='Índice de marginación (0..1)')
    parser.add_argument('--hist-preczip', type=str, help='Historial de precipitación como CSV (ej: 10,0,5,3)')
    parser.add_argument('--hist-temp', type=str, help='Historial de temperatura como CSV (ej: 25,26,24)')
    parser.add_argument('--json', action='store_true', help='Imprimir salida en JSON')
    parser.add_argument('--interactive', action='store_true', help='Modo interactivo (pregunta por teclado)')
    args = parser.parse_args()

    if args.interactive or (args.precip is None or args.temp is None):
        try:
            precip = float(input('Precipitación (mm): ').strip())
            temp = float(input('Temperatura promedio (°C): ').strip())
            marg = input('Índice de marginación (0..1) [enter para 0.5]: ').strip()
            marg_val = float(marg) if marg else None
        except Exception:
            print('Entrada inválida. Saliendo.')
            return 1
        historia = None
    else:
        precip = args.precip
        temp = args.temp
        marg_val = args.marg
        historia = {}
        hp = _parse_comma_floats(args.hist_precip) if hasattr(args, 'hist_precip') else None
        ht = _parse_comma_floats(args.hist_temp) if hasattr(args, 'hist_temp') else None
        if hp is not None:
            historia['precipitacion'] = hp
        if ht is not None:
            historia['temperatura'] = ht

    res = calcular_riesgo_modelo(precip, temp, marg=marg_val, historia=historia)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(format_result(res))
        print('\nDetalle:')
        print(f"  categoría: {res['categoria']}")
        print(f"  nombre: {res['nombre_categoria']}")
    return 0


if __name__ == '__main__':
    # Ejecutar CLI si se llama directamente.
    raise SystemExit(main_cli())
