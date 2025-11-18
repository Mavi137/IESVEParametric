# Resumen Visual - Gráficos Objetivo para Cursor

## 📊 Gráficos a Replicar

### FIGURA 7 - Gráfico de Sensibilidad TM54 ⭐⭐⭐ PRIORITARIO

**Ubicación**: Estudio_Ejemplo_TM54.pdf, página 11

**Descripción Visual**:
Este es el gráfico MÁS IMPORTANTE. Es un gráfico de barras **horizontales** que muestra el impacto de cada variable en el consumo energético total.

**Elementos clave**:
1. **Barras horizontales** en color naranja/salmón (#FF9966 aproximadamente)
2. **Eje X**: "Standardized Regression Coefficient (SRC)" con valores de -0.6 a +0.8
3. **Eje Y**: Nombres de las variables (ej: "Heating setpoint", "DHW demand", "Boilers efficiency")
4. **Línea de referencia** en x=0 (negra, gruesa)
5. **Barras positivas** van hacia la derecha (aumentar variable → aumenta energía)
6. **Barras negativas** van hacia la izquierda (aumentar variable → disminuye energía)
7. **Ordenamiento**: Por valor absoluto de beta, de mayor a menor
8. **Anotaciones con flechas** explicando la dirección del efecto:
   - "As the value increases, energy use increases" (para positivos)
   - "As the value increases, energy use decreases" (para negativos)
9. **Agrupación visual** con líneas punteadas y texto:
   - "Most impactful variables" (|beta| > 0.4)
   - "Moderate impact variables" (0.1 < |beta| < 0.4)  
   - "Low/negligible impact variables" (|beta| < 0.1)
10. **Subtítulos descriptivos** debajo de cada grupo explicando qué tipo de variables son

**Variables mostradas en el ejemplo**:
- Heating setpoint (~0.7) ← Mayor impacto positivo
- DHW demand (~0.5)
- Boilers efficiency (~-0.5) ← Mayor impacto negativo
- Specific Fan Power (~0.15)
- Wall U-value (~0.12)
- Window U-value (~0.12)
- Roof U-value (~0.08)
- Occupancy density (~0.08)
- Equipment power density (~0.08)
- Lighting power density (~0.05)
- Cooling setpoint (~0.02)
- VRF efficiency (~0.0) ← Sin impacto

**Para nuestro caso** (Para_sim_table.csv):
Las 4 variables de entrada son:
- dhw_lph_per_person → "DHW demand"
- people_m2_per_person → "Occupancy density"
- gen_lighting_gain → "Lighting power"
- computer_gain → "Equipment power"

---

### FIGURA 8 - Gráfico de Incertidumbre por Usos Finales ⭐⭐

**Ubicación**: Estudio_Ejemplo_TM54.pdf, página 11

**Descripción Visual**:
Gráfico de **barras con rangos de error** (error bars) o box plots que muestran la variabilidad en cada categoría de uso energético.

**Elementos clave**:
1. **Barras verticales coloreadas** para cada categoría
2. **Barras de error negras** mostrando el rango (min-max o percentiles)
3. **Eje Y izquierdo**: "Energy Use Intensity (kWh/m²/annum)" para usos individuales (0-140)
4. **Eje Y derecho**: Para "Total Energy Use" (0-200+)
5. **Eje X**: Categorías de uso final
6. **Categorías mostradas**:
   - Heating (rojo/salmón) - mayor variabilidad
   - Cooling (azul claro) - baja variabilidad
   - Auxiliary (gris)
   - Lighting (amarillo)
   - Hot Water (naranja)
   - Equipment (verde)
   - **Total Energy Use** (púrpura, separado visualmente)

**Colores sugeridos**:
- Heating: #FF6B6B o #FF8A8A
- Cooling: #4ECDC4 o #85C1E9
- Hot Water: #FFA07A
- Lighting: #FFE66D
- Equipment: #7BC47F
- Fans/Pumps: #95A5A6
- Total: #9B59B6

**Interpretación**:
- Altura de la barra = valor central (mediana o media)
- Longitud del error bar = rango de incertidumbre
- Cuanto más largo el error bar, mayor la incertidumbre en esa categoría

---

### PÁGINA 25 CIBSE - Ejemplo de Análisis de Escenarios

**Ubicación**: cibsetm542022juliegodefroy.pdf, página 25

**Descripción**:
Gráfico de **barras apiladas** mostrando diferentes escenarios.

**Elementos**:
- 4 columnas representando diferentes escenarios:
  - "2020 weather file"
  - "Chiller SEER improved from 3.5 to 3.65 (approx. 4%)"
  - "7 am-7 pm operation (1 h less per day)"
  - "Weekend shutdown"
- Cada barra **apilada** con segmentos de colores:
  - Heating and hot water (gas) - rojo
  - Cooling - verde
  - Fans, pumps, controls - amarillo
  - Lighting - amarillo claro
  - Office equipment - púrpura
  - Computer suite - morado oscuro
  - Other - gris
- Eje Y: "Annual consumption (kWh/m²)" (0-300)
- Total mostrado en la parte superior de cada barra

Este tipo de gráfico es útil para **comparar escenarios** o **análisis de sensibilidad por categorías**.

---

### PÁGINA 26 CIBSE - Box Plots de Incertidumbre

**Ubicación**: cibsetm542022juliegodefroy.pdf, página 26

**Descripción**:
**Box plots horizontales** mostrando rangos de incertidumbre.

**Elementos**:
- Box plots para cada categoría:
  - Heating (gas)
  - Hot water (gas)
  - Cooling
  - Fans and pumps
  - Lighting
  - Office equipment
  - Lifts
- Cada box plot muestra:
  - Caja (Q1 a Q3)
  - Línea de mediana
  - Whiskers (bigotes) hacia valores extremos
- Etiquetas en el lado derecho:
  - "Worst case"
  - "High end"
  - "Likely"
  - "Low end"
- Eje X: "Annual energy consumption (kWh/m²)" (0-180)

**Este estilo** es más detallado que la Figura 8 y muestra claramente:
- La distribución de valores
- Cuartiles
- Valores atípicos
- Rangos de "probable" vs "extremo"

---

## 🎯 Prioridades de Implementación

### URGENTE - Hacer YA:
1. ✅ **chart_sensitivity_tm54.py** - Réplica de Figura 7
   - Es el gráfico más citado en reportes TM54
   - Muestra claramente qué variables son críticas
   - Fácil de interpretar para no-técnicos

### IMPORTANTE - Hacer después:
2. ⭐ **chart_uncertainty_enduse.py** - Réplica de Figura 8
   - Complementa el análisis de sensibilidad
   - Muestra rangos de variabilidad esperados
   - Útil para establecer márgenes de seguridad

### ÚTIL - Si hay tiempo:
3. 📊 **chart_parametric_heatmap.py** - Heatmaps de interacciones
4. 📊 **chart_scenario_comparison.py** - Barras apiladas (estilo pág. 25)
5. 📊 **chart_tornado.py** - Gráfico tornado alternativo

---

## 📐 Dimensiones y Proporciones

### Para Figura 7 (Sensibilidad):
```python
width = 900   # ancho en píxeles
height = 600  # alto depende del número de variables
# Si tienes 4 variables: height = 500
# Si tienes 10 variables: height = 700
# Si tienes 20 variables: height = 1000

margin = dict(
    l=250,  # margen izquierdo para nombres largos
    r=100,  # margen derecho
    t=100,  # margen superior para título
    b=100   # margen inferior para anotaciones
)
```

### Para Figura 8 (Box plots):
```python
width = 1000  # más ancho para acomodar todas las categorías
height = 600
margin = dict(l=80, r=80, t=100, b=80)
```

---

## 🎨 Paleta de Colores Profesional

### Colores para sensibilidad:
```python
SENSITIVITY_COLOR = '#FF9966'  # naranja salmón
POSITIVE_ANNOTATION = '#FF6600'  # naranja
NEGATIVE_ANNOTATION = '#0066FF'  # azul
```

### Colores para usos finales:
```python
END_USE_COLORS = {
    'Heating': '#E74C3C',        # rojo
    'Cooling': '#3498DB',        # azul
    'Hot Water': '#E67E22',      # naranja
    'Lighting': '#F1C40F',       # amarillo
    'Equipment': '#27AE60',      # verde
    'Fans/Pumps': '#95A5A6',     # gris
    'Total': '#9B59B6'           # púrpura
}
```

### Paleta alternativa (más suave):
```python
SOFT_PALETTE = [
    '#FF6B6B',  # rojo suave
    '#4ECDC4',  # turquesa
    '#FFE66D',  # amarillo suave
    '#7BC47F',  # verde suave
    '#FFA07A',  # salmón
    '#B39DDB',  # púrpura suave
    '#90CAF9'   # azul suave
]
```

---

## 📝 Texto de Anotaciones Sugerido

### Para gráfico de sensibilidad:

```python
ANNOTATIONS = {
    'positive_high': {
        'text': 'As this value increases,<br>energy use increases significantly',
        'color': '#FF3333'
    },
    'negative_high': {
        'text': 'As this value increases,<br>energy use decreases significantly',
        'color': '#0066FF'
    },
    'moderate': {
        'text': 'Moderate impact on energy use',
        'color': '#FF9933'
    },
    'low': {
        'text': 'Low impact - not critical for design',
        'color': '#CCCCCC'
    }
}
```

### Títulos sugeridos:

```python
TITLES = {
    'sensitivity': 'Sensitivity analysis of variable inputs on {metric}',
    'uncertainty': 'Uncertainty around baseline energy use for various end uses',
    'heatmap': 'Parametric analysis: {var1} vs {var2} impact on {metric}',
    'scenario': 'Energy use comparison across different scenarios'
}
```

---

## 🔧 Configuración de Ejes Estándar

```python
# Para todos los gráficos
STANDARD_LAYOUT = {
    'font': {
        'size': 12, 
        'family': 'Arial', 
        'color': 'gray'
    },
    'plot_bgcolor': 'white',
    'paper_bgcolor': 'white'
}

STANDARD_GRID = {
    'showgrid': True,
    'gridwidth': 1,
    'gridcolor': 'lightgray'
}

ZERO_LINE = {
    'zeroline': True,
    'zerolinewidth': 2,
    'zerolinecolor': 'black'
}
```

---

## ✅ Checklist de Calidad Visual

Antes de dar por terminado cada gráfico, verificar:

- [ ] Título claro y descriptivo
- [ ] Etiquetas de ejes legibles
- [ ] Colores profesionales (no colores por defecto)
- [ ] Grid sutil pero visible
- [ ] Márgenes adecuados (sin texto cortado)
- [ ] Números/valores legibles (tamaño adecuado)
- [ ] Leyenda clara (si aplica)
- [ ] Fondo blanco (no gris)
- [ ] Líneas de referencia visibles (ej: y=0)
- [ ] Anotaciones útiles (no saturadas)
- [ ] Proporciones agradables (no muy alto ni muy ancho)
- [ ] Funciona bien en pantalla Y en impresión

---

## 📤 Opciones de Exportación

Los scripts deben permitir guardar en:

```python
# HTML interactivo (recomendado para análisis)
fig.write_html("sensitivity_analysis.html")

# PNG para reportes (requiere kaleido)
fig.write_image("sensitivity_analysis.png", width=1200, height=800, scale=2)

# PDF vectorial (mejor calidad)
fig.write_image("sensitivity_analysis.pdf")

# SVG editable
fig.write_image("sensitivity_analysis.svg")
```

---

## 🚀 ¡Listo para Cursor!

Con estos 4 documentos, Cursor tiene toda la información necesaria:

1. ✅ **Instrucciones_Cursor_Graficos.md** - Guía completa y detallada
2. ✅ **Quick_Start_Cursor.md** - Guía rápida y concisa
3. ✅ **chart_sensitivity_tm54_EJEMPLO.py** - Código completo del script prioritario
4. ✅ **Resumen_Visual_Graficos.md** (este archivo) - Referencias visuales

**Próximos pasos**:
1. Abrir proyecto en Cursor
2. Compartir estos documentos con Cursor
3. Pedirle que cree los scripts siguiendo las especificaciones
4. Testear con Para_sim_table.csv
5. Ajustar según necesidad

¡Éxito con la implementación! 🎉
