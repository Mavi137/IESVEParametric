"""
==========================================
Impact Analysis Chart - TM54 Style
==========================================

Module description
------------------
Creates horizontal and vertical bar charts showing absolute impact analysis 
(kWh/m² change per unit change in variable) following CIBSE TM54 style. 
Reads individual CSV files for each input variable and calculates absolute impact.

The chart displays:
- Horizontal/vertical bars with custom colors
- Positive bars (increasing variable → increases energy)
- Negative bars (increasing variable → decreases energy)
- Sorted by absolute impact value (most impactful first)
- Shows actual kWh/m² change per unit change

Usage
-----
python chart_impact_tm54.py

The script will:
1. Load CSV files from 'resultados' folder
2. Calculate absolute impact coefficients for each variable
3. Generate and save TM54-style impact charts as PNG images

Notes
-----
- Requires: pandas, numpy, plotly, scipy, statsmodels
- Input: CSV files in 'resultados' folder
- Output: PNG images in 'Logs/analisis' folder
- Variables can be easily enabled/disabled via configuration
"""

import numpy as np
from scipy import stats
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import statsmodels.formula.api as smf

# ============================================================================
# CONFIGURACIÓN - Fácil activar/desactivar variables
# ============================================================================

# Variables a analizar (activar/desactivar comentando líneas)
# Paleta personalizada con significado semántico (igual que sensitivity)
VARIABLES_CONFIG = {
    'dhw_lph_per_person': {
        'csv_file': 'dhw_lph_per_person.csv',
        'enabled': True,
        'display_name': 'DHW',
        'is_categorical': False,
        'color': '#CCCCFF'  # Morado - ACS (Agua Caliente Sanitaria)
    },
    'people_m2_per_person': {
        'csv_file': 'people_m2_per_person.csv',
        'enabled': True,
        'display_name': 'Occupancy',
        'is_categorical': False,
        'color': '#fea1ff'  # Rosa - Ocupación (mantener)
    },
    'gen_lighting_gain': {
        'csv_file': 'gen_lighting_gain.csv',
        'enabled': True,
        'display_name': 'Lighting',
        'is_categorical': True,
        'color': '#A699A9'  # Gris - Iluminación
    },
    'computer_gain': {
        'csv_file': 'computer_gain.csv',
        'enabled': True,
        'display_name': 'Equipment',
        'is_categorical': True,
        'color': '#CCECFF'  # Azulito - Equipamiento
    }
}

# Métrica objetivo a analizar
TARGET_METRIC = 'EUI_kWh/m2'  # Cambiar aquí para analizar otra métrica

# Carpeta donde están los CSV
RESULTS_FOLDER = 'Resultados'  # Relativo a la carpeta del script

# Carpeta donde guardar las imágenes
OUTPUT_FOLDER = 'Logs/analisis'  # Relativo a la carpeta del script

# ============================================================================
# FUNCIONES
# ============================================================================

def calculate_absolute_impact(df, var_name, target, is_categorical=False):
    """
    Calcula el impacto absoluto (cambio en kWh/m² por unidad de cambio en variable).
    
    Para variables numéricas: pendiente de regresión no estandarizada
    Para variables categóricas: diferencia promedio en EUI entre niveles consecutivos
    
    Args:
        df (pd.DataFrame): Datos con la variable y el target
        var_name (str): Nombre de la columna de la variable
        target (str): Nombre de la columna del target
        is_categorical (bool): Si la variable es categórica (string)
    
    Returns:
        float: Impacto absoluto (kWh/m² por unidad de cambio)
    """
    # Seleccionar columnas relevantes
    df_work = df[[var_name, target]].copy()
    
    if is_categorical:
        # Para categóricas: calcular diferencia promedio entre niveles consecutivos
        df_work['x'] = pd.Categorical(df_work[var_name]).codes
        df_work['y'] = df_work[target]
        df_work = df_work[['x', 'y']].dropna()
        
        # Calcular media de EUI por cada nivel
        means = df_work.groupby('x')['y'].mean().sort_index()
        
        if len(means) < 2:
            return 0.0
        
        # Calcular diferencias entre niveles consecutivos
        diffs = means.diff().dropna()
        
        # Retornar la diferencia promedio (impacto por nivel)
        if len(diffs) > 0:
            return diffs.mean()
        else:
            return 0.0
    else:
        # Para numéricas: regresión no estandarizada
        df_work['x'] = df_work[var_name]
        df_work['y'] = df_work[target]
        df_work = df_work[['x', 'y']].dropna()
        
        # Verificar que hay variación en los datos
        if df_work['x'].std() == 0 or df_work['y'].std() == 0:
            print(f"Advertencia: Sin variación en {var_name}, impacto = 0")
            return 0.0
        
        # Regresión lineal NO estandarizada
        model = smf.ols('y ~ x', data=df_work)
        result = model.fit()
        
        # Obtener coeficiente (pendiente) - cambio en kWh/m² por unidad de x
        impact = result.params['x']
        
        return impact


def load_and_process_variables(results_folder, variables_config, target_metric):
    """
    Carga los CSV y calcula los impactos absolutos para cada variable.
    
    Args:
        results_folder (str): Ruta a la carpeta con los CSV
        variables_config (dict): Configuración de variables
        target_metric (str): Métrica objetivo
    
    Returns:
        tuple: (DataFrame con variables e impactos, dict con colores por variable)
    """
    results = {}
    colors_map = {}
    
    # Obtener ruta absoluta de la carpeta resultados
    script_dir = Path(__file__).parent.parent
    results_path = script_dir / results_folder
    
    if not results_path.exists():
        raise FileNotFoundError(
            f"No se encontró la carpeta '{results_folder}'. "
            f"Ruta esperada: {results_path}"
        )
    
    # Procesar cada variable habilitada
    for var_key, var_config in variables_config.items():
        if not var_config['enabled']:
            continue
        
        csv_file = var_config['csv_file']
        csv_path = results_path / csv_file
        
        if not csv_path.exists():
            print(f"Advertencia: No se encontró {csv_file}, omitiendo...")
            continue
        
        # Cargar CSV (usar punto y coma como separador)
        df = pd.read_csv(csv_path, sep=';')
        
        # Verificar que existe la columna de la variable
        if var_key not in df.columns:
            print(f"Advertencia: Columna '{var_key}' no encontrada en {csv_file}")
            continue
        
        # Verificar que existe la métrica objetivo
        if target_metric not in df.columns:
            print(f"Advertencia: Métrica '{target_metric}' no encontrada en {csv_file}")
            continue
        
        # Calcular impacto absoluto
        try:
            impact = calculate_absolute_impact(
                df, 
                var_key, 
                target_metric,
                is_categorical=var_config['is_categorical']
            )
            display_name = var_config['display_name']
            # Invertir impacto para Occupancy para que quede positivo
            if display_name == 'Occupancy':
                impact = -impact
            results[display_name] = impact
            colors_map[display_name] = var_config.get('color', '#FF9966')  # Color por defecto si no existe
            print(f"[OK] {display_name}: impacto = {impact:.2f} kWh/m² por unidad")
        except Exception as e:
            print(f"Error procesando {var_key}: {e}")
            continue
    
    if not results:
        raise ValueError("No se pudieron calcular impactos. Verifica los archivos CSV.")
    
    # Crear DataFrame para el gráfico
    plot_data = pd.DataFrame.from_dict(
        results, 
        orient='index', 
        columns=['impact']
    )
    
    # Ordenar por valor absoluto de impacto (descendente) - de mayor a menor impacto
    plot_data = plot_data.sort_values(by=['impact'], ascending=False, key=abs)
    
    return plot_data, colors_map


def create_tm54_impact_chart(plot_data, target_metric, colors_map):
    """
    Crea el gráfico de impacto estilo TM54 con barras HORIZONTALES.
    
    Args:
        plot_data (pd.DataFrame): DataFrame con variables e impactos
        target_metric (str): Métrica objetivo analizada
        colors_map (dict): Diccionario con colores por variable (display_name -> color)
    
    Returns:
        go.Figure: Figura de Plotly
    """
    # Preparar datos
    variables = plot_data.index.tolist()
    impacts = plot_data['impact'].values
    
    # Obtener colores individuales para cada variable
    colors = [colors_map.get(var, '#FF9966') for var in variables]  # Color por defecto si no existe
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar barras horizontales con colores individuales
    fig.add_trace(go.Bar(
        x=impacts,
        y=variables,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='white', width=1.5)  # Borde blanco para mejor contraste
        ),
        text=[f'{i:.2f}' for i in impacts],
        textposition='outside',
        textfont=dict(size=13, color='gray'),
        name='Impact'
    ))
    
    # Línea de referencia en x=0
    fig.add_vline(
        x=0,
        line_width=2,
        line_color='black',
        line_dash='solid',
        annotation_text='No effect',
        annotation_position='top'
    )
    
    # Actualizar layout
    fig.update_layout(
        title={
            'text': f'<b>IMPACT ANALYSIS: IMPACT ON {target_metric.upper()}</b>',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top',
            'font': {'size': 22, 'family': 'Arial', 'color': 'black'}
        },
        xaxis=dict(
            title=dict(
                text='Impact (kWh/m² per unit change)',
                font=dict(size=14, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            range=[min(impacts.min() * 1.2, -max(abs(impacts)) * 1.2), max(impacts.max() * 1.2, max(abs(impacts)) * 1.2)]
        ),
        yaxis=dict(
            title='',
            showgrid=False,
            tickfont=dict(size=13, family='Arial', color='black')
        ),
        font={'size': 12, 'family': 'Arial', 'color': 'gray'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=900,
        height=max(400, len(variables) * 80),
        margin=dict(l=250, r=100, t=120, b=80),
        showlegend=False
    )
    
    return fig


def create_tm54_impact_chart_vertical(plot_data, target_metric, colors_map):
    """
    Crea el gráfico de impacto estilo TM54 con barras VERTICALES.
    
    Args:
        plot_data (pd.DataFrame): DataFrame con variables e impactos
        target_metric (str): Métrica objetivo analizada
        colors_map (dict): Diccionario con colores por variable (display_name -> color)
    
    Returns:
        go.Figure: Figura de Plotly
    """
    # Preparar datos
    variables = plot_data.index.tolist()
    impacts = plot_data['impact'].values
    
    # Obtener colores individuales para cada variable
    colors = [colors_map.get(var, '#FF9966') for var in variables]  # Color por defecto si no existe
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar barras VERTICALES con colores individuales
    fig.add_trace(go.Bar(
        x=variables,
        y=impacts,
        orientation='v',  # Vertical
        marker=dict(
            color=colors,
            line=dict(color='white', width=1.5)  # Borde blanco para mejor contraste
        ),
        text=[f'{i:.2f}' for i in impacts],
        textposition='outside',
        textfont=dict(size=13, color='gray'),
        name='Impact'
    ))
    
    # Línea de referencia en y=0
    fig.add_hline(
        y=0,
        line_width=2,
        line_color='black',
        line_dash='solid',
        annotation_text='No effect',
        annotation_position='right'
    )
    
    # Actualizar layout
    fig.update_layout(
        title={
            'text': f'<b>IMPACT ANALYSIS: IMPACT ON {target_metric.upper()}</b>',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top',
            'font': {'size': 22, 'family': 'Arial', 'color': 'black'}
        },
        xaxis=dict(
            title='',
            showgrid=False,
            tickfont=dict(size=13, family='Arial', color='black'),
            tickangle=-45  # Rotar etiquetas para mejor legibilidad
        ),
        yaxis=dict(
            title=dict(
                text='Impact (kWh/m² per unit change)',
                font=dict(size=14, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            range=[min(impacts.min() * 1.2, -max(abs(impacts)) * 1.2), max(impacts.max() * 1.2, max(abs(impacts)) * 1.2)]
        ),
        font={'size': 13, 'family': 'Arial', 'color': 'black'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=max(800, len(variables) * 150),
        height=1000,
        margin=dict(l=80, r=100, t=120, b=150),
        showlegend=False
    )
    
    return fig


def main():
    """Función principal"""
    print("=" * 60)
    print("Análisis de Impacto - Estilo TM54")
    print("=" * 60)
    print(f"Métrica objetivo: {TARGET_METRIC}")
    print(f"Carpeta de resultados: {RESULTS_FOLDER}")
    print("-" * 60)
    
    # Cargar y procesar variables
    plot_data, colors_map = load_and_process_variables(
        RESULTS_FOLDER, 
        VARIABLES_CONFIG, 
        TARGET_METRIC
    )
    
    print("-" * 60)
    print("\nImpactos calculados:")
    print(plot_data)
    print("-" * 60)
    
    # Crear gráficos
    print("\nGenerando gráficos...\n")
    
    # Gráfico horizontal
    fig_horizontal = create_tm54_impact_chart(plot_data, TARGET_METRIC, colors_map)
    
    # Gráfico vertical
    fig_vertical = create_tm54_impact_chart_vertical(plot_data, TARGET_METRIC, colors_map)
    
    # Guardar imágenes
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / OUTPUT_FOLDER
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Nombre del archivo
    metric_clean = TARGET_METRIC.replace('/', '_').replace('(', '').replace(')', '')
    filename_h = output_path / f'Impacto_TM54_Horizontal_{metric_clean}.png'
    filename_v = output_path / f'Impacto_TM54_Vertical_{metric_clean}.png'
    
    # Guardar con alta resolución
    scale_factor = 2
    fig_horizontal.write_image(str(filename_h), width=fig_horizontal.layout.width * scale_factor, 
                               height=fig_horizontal.layout.height * scale_factor, scale=scale_factor)
    print(f"[OK] Imagen HORIZONTAL guardada en: {filename_h.name}")
    print(f"     Dimensiones: {fig_horizontal.layout.width * scale_factor}x{fig_horizontal.layout.height * scale_factor} px (escala {scale_factor}x)")
    
    fig_vertical.write_image(str(filename_v), width=fig_vertical.layout.width * scale_factor, 
                             height=fig_vertical.layout.height * scale_factor, scale=scale_factor)
    print(f"[OK] Imagen VERTICAL guardada en: {filename_v.name}")
    print(f"     Dimensiones: {fig_vertical.layout.width * scale_factor}x{fig_vertical.layout.height * scale_factor} px (escala {scale_factor}x)")


if __name__ == '__main__':
    main()

