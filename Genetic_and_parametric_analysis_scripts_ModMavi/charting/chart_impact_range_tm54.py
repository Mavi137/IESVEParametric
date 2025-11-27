"""
==========================================
Range Impact Analysis Chart - TM54 Style
==========================================

Module description
------------------
Creates horizontal and vertical bar charts showing impact based on TOTAL RANGE
of each variable (difference between worst case and lower limit).
This better represents the actual impact of each variable on energy consumption.

Usage
-----
python chart_impact_range_tm54.py
"""

import numpy as np
from scipy import stats
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import statsmodels.formula.api as smf

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

VARIABLES_CONFIG = {
    'dhw_lph_per_person': {
        'csv_file': 'dhw_lph_per_person.csv',
        'enabled': True,
        'display_name': 'DHW',
        'is_categorical': False,
        'color': '#CCCCFF'
    },
    'people_m2_per_person': {
        'csv_file': 'people_m2_per_person.csv',
        'enabled': True,
        'display_name': 'Occupancy',
        'is_categorical': False,
        'color': '#fea1ff'
    },
    'gen_lighting_gain': {
        'csv_file': 'gen_lighting_gain.csv',
        'enabled': True,
        'display_name': 'Lighting',
        'is_categorical': True,
        'color': '#A699A9'
    },
    'computer_gain': {
        'csv_file': 'computer_gain.csv',
        'enabled': True,
        'display_name': 'Equipment',
        'is_categorical': True,
        'color': '#CCECFF'
    }
}

TARGET_METRIC = 'EUI_kWh/m2'
RESULTS_FOLDER = 'Resultados'
OUTPUT_FOLDER = 'Logs/analisis'

# ============================================================================
# FUNCIONES
# ============================================================================

def calculate_range_impact(df, var_name, target, is_categorical=False):
    """
    Calcula el impacto como el RANGO TOTAL de cambio en EUI.
    
    Para variables categóricas: diferencia entre máximo y mínimo EUI
    Para variables numéricas: diferencia entre máximo y mínimo EUI en el rango de la variable
    
    Args:
        df (pd.DataFrame): Datos con la variable y el target
        var_name (str): Nombre de la columna de la variable
        target (str): Nombre de la columna del target
        is_categorical (bool): Si la variable es categórica (string)
    
    Returns:
        float: Impacto como rango total (kWh/m²)
    """
    df_work = df[[var_name, target]].copy()
    df_work = df_work.dropna()
    
    if is_categorical:
        # Para categóricas: calcular media por nivel y luego rango
        df_work['x'] = pd.Categorical(df_work[var_name]).codes
        df_work['y'] = df_work[target]
        
        # Calcular media de EUI por cada nivel
        means = df_work.groupby('x')['y'].mean()
        
        if len(means) < 2:
            return 0.0
        
        # Rango total: máximo - mínimo
        range_impact = means.max() - means.min()
        return range_impact
    else:
        # Para numéricas: calcular rango de EUI en el rango de la variable
        df_work['x'] = df_work[var_name]
        df_work['y'] = df_work[target]
        
        if len(df_work) < 2:
            return 0.0
        
        # Rango total: máximo EUI - mínimo EUI
        range_impact = df_work['y'].max() - df_work['y'].min()
        return range_impact


def normalize_impacts(impacts):
    """Normaliza los impactos dividiendo por el máximo absoluto"""
    abs_impacts = impacts.abs()
    max_abs = abs_impacts.max()
    
    if max_abs == 0:
        return impacts
    
    normalized = impacts / max_abs
    return normalized


def load_and_process_variables(results_folder, variables_config, target_metric):
    """Carga CSV y calcula impactos por rango"""
    results = {}
    colors_map = {}
    
    script_dir = Path(__file__).parent.parent
    results_path = script_dir / results_folder
    
    if not results_path.exists():
        raise FileNotFoundError(f"No se encontró la carpeta '{results_folder}'. Ruta: {results_path}")
    
    for var_key, var_config in variables_config.items():
        if not var_config['enabled']:
            continue
        
        csv_file = var_config['csv_file']
        csv_path = results_path / csv_file
        
        if not csv_path.exists():
            print(f"Advertencia: No se encontró {csv_file}, omitiendo...")
            continue
        
        df = pd.read_csv(csv_path, sep=';')
        
        if var_key not in df.columns:
            print(f"Advertencia: Columna '{var_key}' no encontrada en {csv_file}")
            continue
        
        if target_metric not in df.columns:
            print(f"Advertencia: Métrica '{target_metric}' no encontrada en {csv_file}")
            continue
        
        try:
            impact = calculate_range_impact(
                df, 
                var_key, 
                target_metric,
                is_categorical=var_config['is_categorical']
            )
            display_name = var_config['display_name']
            # Invertir para Occupancy si es necesario
            if display_name == 'Occupancy':
                impact = abs(impact)  # Asegurar positivo
            
            results[display_name] = impact
            colors_map[display_name] = var_config.get('color', '#FF9966')
            print(f"[OK] {display_name}: impacto (rango) = {impact:.2f} kWh/m²")
        except Exception as e:
            print(f"Error procesando {var_key}: {e}")
            continue
    
    if not results:
        raise ValueError("No se pudieron calcular impactos. Verifica los archivos CSV.")
    
    # Normalizar
    impacts_series = pd.Series(results)
    impacts_normalized = normalize_impacts(impacts_series)
    
    plot_data = pd.DataFrame.from_dict(
        impacts_normalized.to_dict(), 
        orient='index', 
        columns=['impact']
    )
    
    plot_data = plot_data.sort_values(by=['impact'], ascending=False, key=abs)
    
    return plot_data, colors_map, results


def create_tm54_range_impact_chart(plot_data, target_metric, colors_map, absolute_impacts):
    """Crea gráfico de impacto por rango - HORIZONTAL"""
    variables = plot_data.index.tolist()
    impacts = plot_data['impact'].values
    colors = [colors_map.get(var, '#FF9966') for var in variables]
    # Mostrar valores normalizados en lugar de absolutos
    text_labels = [f'{imp:.3f}' for imp in impacts]
    
    fig = go.Figure()
    
    # Crear hovertemplate con valores absolutos
    hover_texts = []
    for var in variables:
        abs_val = absolute_impacts.get(var, 0)
        hover_texts.append(f'<b>{var}</b><br>Impacto normalizado: {impacts[variables.index(var)]:.3f}<br>Rango total: {abs_val:.2f} kWh/m²')
    
    fig.add_trace(go.Bar(
        x=impacts,
        y=variables,
        orientation='h',
        marker=dict(color=colors, line=dict(color='white', width=1.5)),
        text=text_labels,
        textposition='outside',
        textfont=dict(size=28, color='black', family='Arial', weight='bold'),
        name='Range Impact',
        customdata=hover_texts,
        hovertemplate='%{customdata}<extra></extra>',
        cliponaxis=False  # Permitir que el texto se vea fuera del área del gráfico
    ))
    
    # No agregar línea en x=0 ya que todos los valores son positivos
    
    fig.update_layout(
        title={
            'text': f'<b>RANGE IMPACT ANALYSIS: IMPACT ON {target_metric.upper()}</b><br>'
                   '<sub>Total range of EUI change (values show absolute range in kWh/m²)</sub>',
            'x': 0.5, 'xanchor': 'center', 'y': 0.98, 'yanchor': 'top',
            'font': {'size': 22, 'family': 'Arial', 'color': 'black'}
        },
        xaxis=dict(
            title=dict(text='Normalized Range Impact', font=dict(size=24, family='Arial', color='black')),
            showgrid=True, gridwidth=1, gridcolor='lightgray',
            zeroline=False,  # No mostrar línea en cero ya que todos son positivos
            range=[0, 1.0],  # Solo valores positivos, máximo 1.0
            tickfont=dict(size=22, family='Arial', color='black')  # Números del eje más grandes
        ),
        yaxis=dict(title='', showgrid=False, tickfont=dict(size=22, family='Arial', color='black')),
        font={'size': 12, 'family': 'Arial', 'color': 'gray'},
        plot_bgcolor='white', paper_bgcolor='white',
        width=900, height=max(400, len(variables) * 80),
        margin=dict(l=250, r=150, t=140, b=80),  # Aumentar margen derecho para que se vea el número de DHW
        showlegend=False
    )
    
    return fig


def create_tm54_range_impact_chart_vertical(plot_data, target_metric, colors_map, absolute_impacts):
    """Crea gráfico de impacto por rango - VERTICAL"""
    variables = plot_data.index.tolist()
    impacts = plot_data['impact'].values
    colors = [colors_map.get(var, '#FF9966') for var in variables]
    # Mostrar valores normalizados en lugar de absolutos
    text_labels = [f'{imp:.3f}' for imp in impacts]
    
    fig = go.Figure()
    
    # Crear hovertemplate con valores absolutos
    hover_texts = []
    for var in variables:
        abs_val = absolute_impacts.get(var, 0)
        hover_texts.append(f'<b>{var}</b><br>Impacto normalizado: {impacts[variables.index(var)]:.3f}<br>Rango total: {abs_val:.2f} kWh/m²')
    
    fig.add_trace(go.Bar(
        x=variables,
        y=impacts,
        orientation='v',
        marker=dict(color=colors, line=dict(color='white', width=1.5)),
        text=text_labels,
        textposition='outside',
        textfont=dict(size=28, color='black', family='Arial', weight='bold'),
        name='Range Impact',
        customdata=hover_texts,
        hovertemplate='%{customdata}<extra></extra>',
        cliponaxis=False  # Permitir que el texto se vea fuera del área del gráfico
    ))
    
    # No agregar línea en y=0 ya que todos los valores son positivos
    
    fig.update_layout(
        title={
            'text': f'<b>RANGE IMPACT ANALYSIS: IMPACT ON {target_metric.upper()}</b><br>'
                   '<sub>Total range of EUI change (values show absolute range in kWh/m²)</sub>',
            'x': 0.5, 'xanchor': 'center', 'y': 0.98, 'yanchor': 'top',
            'font': {'size': 22, 'family': 'Arial', 'color': 'black'}
        },
        xaxis=dict(
            title='', showgrid=False,
            tickfont=dict(size=22, family='Arial', color='black'),
            tickangle=-45
        ),
        yaxis=dict(
            title=dict(text='Normalized Range Impact', font=dict(size=24, family='Arial', color='black')),
            showgrid=True, gridwidth=1, gridcolor='lightgray',
            zeroline=False,  # No mostrar línea en cero ya que todos son positivos
            range=[0, 1.0],  # Solo valores positivos, máximo 1.0
            tickfont=dict(size=22, family='Arial', color='black')  # Números del eje más grandes
        ),
        font={'size': 13, 'family': 'Arial', 'color': 'black'},
        plot_bgcolor='white', paper_bgcolor='white',
        width=max(800, len(variables) * 150), height=1000,
        margin=dict(l=80, r=150, t=140, b=150),  # Aumentar margen derecho para que se vea el número de DHW
        showlegend=False
    )
    
    return fig


def main():
    print("=" * 60)
    print("Análisis de Impacto por Rango - Estilo TM54")
    print("=" * 60)
    print(f"Métrica objetivo: {TARGET_METRIC}")
    print(f"Carpeta de resultados: {RESULTS_FOLDER}")
    print("-" * 60)
    
    plot_data, colors_map, absolute_impacts = load_and_process_variables(
        RESULTS_FOLDER, VARIABLES_CONFIG, TARGET_METRIC
    )
    
    print("-" * 60)
    print("\nImpactos por rango (valores absolutos):")
    for var, impact in sorted(absolute_impacts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {var}: {impact:.2f} kWh/m²")
    print("-" * 60)
    
    print("\nGenerando gráficos...\n")
    
    fig_h = create_tm54_range_impact_chart(plot_data, TARGET_METRIC, colors_map, absolute_impacts)
    fig_v = create_tm54_range_impact_chart_vertical(plot_data, TARGET_METRIC, colors_map, absolute_impacts)
    
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / OUTPUT_FOLDER
    output_path.mkdir(parents=True, exist_ok=True)
    
    metric_clean = TARGET_METRIC.replace('/', '_').replace('(', '').replace(')', '')
    filename_h = output_path / f'Impacto_Rango_TM54_Horizontal_{metric_clean}.png'
    filename_v = output_path / f'Impacto_Rango_TM54_Vertical_{metric_clean}.png'
    
    scale_factor = 2
    fig_h.write_image(str(filename_h), width=fig_h.layout.width * scale_factor, 
                     height=fig_h.layout.height * scale_factor, scale=scale_factor)
    print(f"[OK] Imagen HORIZONTAL: {filename_h.name}")
    
    fig_v.write_image(str(filename_v), width=fig_v.layout.width * scale_factor, 
                     height=fig_v.layout.height * scale_factor, scale=scale_factor)
    print(f"[OK] Imagen VERTICAL: {filename_v.name}")


if __name__ == '__main__':
    main()

