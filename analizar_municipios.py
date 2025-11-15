"""Script de utilidad: analizar_municipios.py

Este script consulta la API local (/api/municipios y /api/analizar) y muestra
un resumen rápido de cuántos municipios caen en cada categoría (D0..D4).

Notas:
- Está escrito para ejecutarse localmente contra http://127.0.0.1:5000
- Por simplicidad limita el análisis a los primeros 10 municipios
- Maneja errores de red/JSON de forma muy simple (imprime el error)
"""

import urllib.request  # para abrir URLs HTTP sin dependencias externas
import json             # para parsear respuestas JSON
from collections import Counter  # para contar categorías al final

# Envolvemos todo en try/except para atrapar errores globales (conexión, JSON, etc.)
try:
    # 1) Obtener la lista de municipios desde la API local
    resp_municipios = urllib.request.urlopen('http://127.0.0.1:5000/api/municipios')
    municipios_data = json.loads(resp_municipios.read().decode())

    # Limitamos a los primeros 10 municipios para que el script sea rápido
    # Si quieres analizar todos, quita '[:10]'.
    municipios = municipios_data['municipios']

    # Lista para reunir las categorías devueltas por la API
    categorias = []

    print("Analizando municipios...")
    print("-" * 60)

    # 2) Iterar sobre cada municipio y pedir el análisis a la API
    for municipio in municipios:
        try:
            # Llamada GET a /api/analizar?municipio=Nombre
            resp = urllib.request.urlopen(f'http://127.0.0.1:5000/api/analizar?municipio={municipio}')
            data = json.loads(resp.read().decode())

            # Extraer el índice y la categoría de la respuesta JSON.
            # Usamos .get() con valores por defecto para evitar KeyError si la respuesta cambia.
            indice = data.get('indice_sequia', 0)
            categoria = data.get('categoria', 'N/A')

            # Guardar la categoría para el resumen y mostrar la línea por municipio
            categorias.append(categoria)
            print(f"{municipio:<30} => Índice: {indice:>6}% | {categoria}")
        except Exception as e:
            # Si falla la llamada o el parseo, mostramos el error pero seguimos con el siguiente municipio
            print(f"{municipio:<30} => Error: {e}")

    print("-" * 60)
    print("\nResumen de categorías:")

    # 3) Contar ocurrencias de cada categoría y mostrarlas ordenadas D0..D4
    conteo = Counter(categorias)
    for cat in ['D0', 'D1', 'D2', 'D3', 'D4']:
        count = conteo.get(cat, 0)
        print(f"  {cat}: {count}")

except Exception as e:
    # Error general: por ejemplo, la API local no está levantada
    print(f"Error: {e}")
