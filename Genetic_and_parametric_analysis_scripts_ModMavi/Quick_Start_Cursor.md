# Quick Start Guide para Cursor - Scripts de Visualización

## Resumen Ejecutivo

Necesito crear **5 nuevos scripts de Python** para visualizar datos de simulación energética. Los scripts deben leer `Para_sim_table.csv` y generar gráficos profesionales siguiendo el estándar CIBSE TM54.

## Scripts a Crear (en orden de prioridad)

### 1️⃣ chart_sensitivity_tm54.py - PRIORITARIO ⭐⭐⭐
**Objetivo**: Gráfico de barras horizontal tipo Figura 7 del TM54
- Entrada: `Para_sim_table.csv`
- Análisis: Regresión estandarizada (beta coefficients)
- Variables: dhw, people, lighting, equipment vs métrica objetivo
- Visual: Barras naranjas horizontales, positivas arriba, negativas abajo
- Anotaciones con flechas explicativas
- Ordenar por |beta| descendente

**Código base a replicar**: `chart_sensitivity.py` (ya existe, úsalo de referencia)

```python
# Pseudocódigo
def sensitivity_tm54(csv_path, target_metric='EUI_kWh/m2'):
    df = pd.read_csv(csv_path)
    
    # Para cada variable de entrada
    input_vars = ['dhw_lph_per_person', 'people_m2_per_person', 
                  'gen_lighting_gain', 'computer_gain']
    
    betas = {}
    for var in input_vars:
        # Standardize data
        df_z = standardize(df[[var, target_metric]])
        # Regression
        model = smf.ols('y ~ x', data=df_z).fit()
        betas[var] = model.params['x']
    
    # Plot horizontal bars
    # Add annotations
    # Show plot
```

---

### 2️⃣ chart_uncertainty_enduse.py - IMPORTANTE ⭐⭐
**Objetivo**: Box plots de incertidumbre por uso final (Figura 8)
- Box plots verticales para cada categoría
- Categorías: Heating, Cooling, DHW, Lighting, Equipment, Fans, Total
- Colores diferenciados

```python
# Mapeo de columnas
end_uses = {
    'Heating': 'Space_heating_(gas)_kWh/m2',
    'Cooling': 'Space_cooling_kWh/m2',
    'Hot Water': 'DHW_heating_kWh/m2',
    'Lighting': 'Interior_lighting_kWh/m2',
    'Equipment': 'Receptacle_equipment_kWh/m2',
    'Fans/Pumps': ['Fans_interior_kWh/m2', 'Pumps_kWh/m2'],  # sumar
    'Total': 'EUI_kWh/m2'
}
```

---

### 3️⃣ chart_parametric_heatmap.py - ÚTIL ⭐
**Objetivo**: Heatmaps de combinaciones de parámetros
- 2D heatmap: variable X vs variable Y, color = resultado
- Múltiples heatmaps para variables categóricas

---

### 4️⃣ chart_sensitivity_detailed.py - OPCIONAL
**Objetivo**: Análisis extendido con todas las variables
- Similar a script 1 pero más detallado
- Incluir valores categóricos expandidos

---

### 5️⃣ chart_tornado.py - OPCIONAL
**Objetivo**: Gráfico tornado
- Barras dobles mostrando rango de variación
- Ordenado por impacto

---

## Estructura de Para_sim_table.csv

```
run,dhw_lph_per_person,people_m2_per_person,gen_lighting_gain,computer_gain,
    Gas_MWh,Elec_MWh,Gas_kWh/m2,Elec_kWh/m2,EUI_kWh/m2,CE_kgCO2/m2,...
0,  0.4,            8.6,                 Lighting1,     Equipment1,    ...
1,  0.4,            8.6,                 Lighting1,     Equipment2,    ...
...
80, 0.2,            5.75,                Lighting3,     Equipment3,    ...
```

**Variables entrada** (4):
- dhw_lph_per_person: [0.2, 0.4, 0.7]
- people_m2_per_person: [5.75, 8.6, 17.24]
- gen_lighting_gain: [Lighting1, Lighting2, Lighting3]
- computer_gain: [Equipment1, Equipment2, Equipment3]

**Variables salida** (29 columnas): EUI, emisiones, por sistema, usos finales, etc.

---

## Plantilla de Script

```python
"""
==========================================
[Nombre del Script] - TM54 Analysis
==========================================

Module description
------------------
[Descripción de qué hace el script]

Usage
-----
python [nombre_script].py

The script will:
1. Load Para_sim_table.csv
2. Process data for [análisis específico]
3. Generate and display [tipo de gráfico]
4. Optionally save as HTML/PNG

Notes
-----
- Requires: pandas, numpy, plotly, scipy, statsmodels
- Input: Para_sim_table.csv
- Output: Interactive Plotly chart
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
import statsmodels.formula.api as smf

def main_function(df, target_metric='EUI_kWh/m2'):
    """
    Main analysis and plotting function
    
    Args:
        df (pd.DataFrame): Simulation results
        target_metric (str): Output metric to analyze
    
    Returns:
        fig (plotly figure): Generated chart
    """
    
    # Analysis logic here
    
    # Create figure
    fig = go.Figure()
    
    # Add traces/data
    
    # Update layout
    fig.update_layout(
        title='[Título del Gráfico]',
        font={'size': 12, 'family': 'Arial', 'color': 'gray'},
        width=900,
        height=700,
        plot_bgcolor='white'
    )
    
    return fig

if __name__ == "__main__":
    # Load data
    csv_path = 'Para_sim_table.csv'
    df = pd.read_csv(csv_path)
    
    # Set target metric
    target = 'EUI_kWh/m2'  # Can be changed
    
    # Generate chart
    fig = main_function(df, target)
    
    # Show
    fig.show()
    
    # Optional: Save
    # fig.write_html("output.html")
    # fig.write_image("output.png")
```

---

## Estilo Visual Requerido

### Colores:
- **Sensibilidad**: Naranja/Salmón (#FF9966)
- **Box plots**: Paleta categórica de Plotly
- **Heatmap**: Viridis o RdYlBu (divergente)

### Fuentes:
- Arial, 12pt para texto general
- 10pt para etiquetas de ejes
- 14pt para títulos

### Grid:
```python
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray',
                 zeroline=True, zerolinewidth=2, zerolinecolor='black')
```

---

## Checklist para Cursor

Cuando crees cada script, verifica:

- [ ] ¿Lee correctamente Para_sim_table.csv?
- [ ] ¿Maneja variables categóricas (Lighting, Equipment)?
- [ ] ¿Permite cambiar la métrica objetivo fácilmente?
- [ ] ¿Incluye docstrings y comentarios?
- [ ] ¿Sigue el estilo de los scripts existentes?
- [ ] ¿El gráfico es claro y profesional?
- [ ] ¿Funciona independientemente (sin modificar otros archivos)?
- [ ] ¿Maneja errores (ej: columnas faltantes)?

---

## Comando Rápido para Testing

```bash
# En la carpeta del proyecto:
python chart_sensitivity_tm54.py
python chart_uncertainty_enduse.py
python chart_parametric_heatmap.py
```

---

## Referencias Clave

1. **chart_sensitivity.py** - Lógica de regresión beta
2. **chart_parallel.py** - Estilo Plotly
3. **Para_sim_table.csv** - Estructura de datos
4. **Figura 7 TM54** - Referencia visual principal
5. **Figura 8 TM54** - Box plots por uso final

---

## Tips Importantes

⚠️ **Variables categóricas**: `gen_lighting_gain` y `computer_gain` son strings. 
Para regresión, codifica como:
```python
df['lighting_code'] = pd.Categorical(df['gen_lighting_gain']).codes
df['equipment_code'] = pd.Categorical(df['computer_gain']).codes
```

⚠️ **Normalización**: Usa z-scores para coeficientes comparables:
```python
df_z = df.select_dtypes(include=[np.number]).apply(stats.zscore)
```

⚠️ **Múltiples columnas**: Para "Fans/Pumps" suma dos columnas:
```python
df['Fans_Pumps_total'] = df['Fans_interior_kWh/m2'] + df['Pumps_kWh/m2']
```

---

## Resultado Final Esperado

Después de ejecutar los scripts, deberíamos tener:
1. ✅ Gráfico de sensibilidad profesional tipo TM54
2. ✅ Box plots de incertidumbre por uso final
3. ✅ Heatmaps de interacciones paramétricas
4. ✅ Scripts modulares y reutilizables
5. ✅ Documentación clara en cada script

**¡Todo listo para el análisis post-simulación!** 🎯
