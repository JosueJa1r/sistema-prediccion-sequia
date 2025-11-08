# Sistema de Predicción de Sequía - Chihuahua

Sistema inteligente de análisis de riesgo de sequía para los municipios del estado de Chihuahua, basado en datos meteorológicos históricos y modelos matemáticos avanzados.

## 🚀 Características

- **Análisis por Municipio**: Evaluación de riesgo de sequía para cada municipio de Chihuahua.
- **Modelos Matemáticos**: Cálculo diferencial, estadística y álgebra lineal
- **Interfaz Moderna**: Diseño responsive con efectos visuales

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **Matemáticas**: Cálculo diferencial, regresión lineal, álgebra lineal
- **Visualización**: Gráficos interactivos con Chart.js

## 📋 Requisitos

- Python 3.7+
- Flask
- Flask-CORS

## 🚀 Instalación y Uso

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/sistema-prediccion-sequia.git
   cd sistema-prediccion-sequia
   ```

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**:
   ```bash
   python app_working.py
   ```

4. **Abrir en el navegador**:
   ```
   http://localhost:5001
   ```

## 📁 Estructura del Proyecto

```
├── app.py                 # Aplicación principal (con API externa)
├── app_working.py         # Aplicación simplificada (recomendada)
├── app_simple.py          # Versión alternativa
├── requirements.txt       # Dependencias de Python
├── static/
│   ├── style.css         # Estilos CSS
│   ├── img1.png          # Imágenes
│   └── img2.png
├── templates/
│   └── index.html        # Interfaz web
└── README.md             # Este archivo
```

## 🧮 Modelos Matemáticos

### 1. Cálculo Diferencial
- **Derivada de tendencia**: Analiza la tasa de cambio en la precipitación
- **Fórmula**: `f'(x) ≈ f(x) - f(x-1)`

### 2. Estadística
- **Regresión lineal simple**: `y = β₀ + β₁x`
- **Media y desviación estándar**: Análisis estadístico de datos históricos

### 3. Álgebra Lineal
- **Ecuación Normal**: `(X^T * X) * β = X^T * y`
- **Eliminación Gauss-Jordan**: Resolución de sistemas de ecuaciones

## 🎯 Funcionalidades

### Análisis por Municipio
- Selección de cualquier municipio de Chihuahua.
- Cálculo automático de riesgo de sequía
- Clasificación: BAJO, MEDIO, ALTO

### Recomendaciones
- **
### Variables de Entorno
No se requieren variables de entorno especiales. La aplicación funciona con datos simulados.

### Personalización
- Modificar el diccionario `municipios` para agregar o cambiar coordenadas.
- Ajustar parámetros de riesgo en las funciones de análisis
- Personalizar estilos en `static/style.css`

## 📊 API Endpoints

- `GET /` - Página principal
- `GET /api/analizar?municipio=Chihuahua` - Análisis de riesgo por municipio.

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeatur)re`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Tu Nombre** - *Desarrollo inicial* - [TuGitHub](https://github.com/tu-usuario)

## 🙏 Agradecimientos

- Open-Meteo API para datos meteorológicos
- Chart.js para visualizaciones
- Comunidad de desarrolladores Python/Flask

---

**Nota**: Esta aplicación utiliza datos simulados para demostración. En un entorno de producción, se recomienda integrar con APIs meteorológicas reales.

## 🚀 Despliegue en Vercel
Esta aplicación está optimizada para funcionar en Vercel con la estructura `api/index.py`.
