"""
==========================================
Sensitivity Analysis Chart - TM54 Style
==========================================

Module description
------------------
Creates a horizontal bar chart showing sensitivity analysis (beta coefficients) 
following CIBSE TM54 Figure 7 style. Reads individual CSV files for each 
input variable and calculates standardized regression coefficients.

The chart displays:
- Horizontal bars in orange/salmon color (#FF9966)
- Positive bars extend right (increasing variable → increases energy)
- Negative bars extend left (increasing variable → decreases energy)
- Sorted by absolute beta value (most impactful first)
- Annotations explaining the direction of effect

Usage
-----
python chart_sensitivity_tm54.py

The script will:
1. Load CSV files from 'resultados' folder
2. Calculate beta coefficients for each variable
3. Generate and display TM54-style sensitivity chart
4. Optionally save as HTML/PNG

Notes
-----
- Requires: pandas, numpy, plotly, scipy, statsmodels
- Input: CSV files in 'resultados' folder
- Output: Interactive Plotly chart
- Variables can be easily enabled/disabled via configuration
"""

import numpy as np
from scipy import stats
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import statsmodels.formula.api as smf

# ============================================================================
# CONFIGURACIÓN - Fácil activar/desactivar variables
# ============================================================================

# Variables a analizar (activar/desactivar comentando líneas)
# Paleta personalizada con significado semántico
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

# ============================================================================
# FUNCIONES
# ============================================================================

def calculate_beta(df, var_name, target, is_categorical=False):
    """
    Calcula el coeficiente beta estandarizado mediante regresión.
    
    Args:
        df (pd.DataFrame): Datos con la variable y el target
        var_name (str): Nombre de la columna de la variable
        target (str): Nombre de la columna del target
        is_categorical (bool): Si la variable es categórica (string)
    
    Returns:
        float: Coeficiente beta estandarizado
    """
    # Seleccionar columnas relevantes
    df_work = df[[var_name, target]].copy()
    
    # Si es categórica, codificar numéricamente
    if is_categorical:
        df_work['x'] = pd.Categorical(df_work[var_name]).codes
    else:
        df_work['x'] = df_work[var_name]
    
    # Renombrar target para statsmodels
    df_work.rename(columns={target: 'y'}, inplace=True)
    
    # Seleccionar solo las columnas necesarias y filtrar valores nulos
    df_work = df_work[['x', 'y']].dropna()
    
    # Verificar que hay variación en los datos
    if df_work['x'].std() == 0 or df_work['y'].std() == 0:
        print(f"Advertencia: Sin variación en {var_name}, beta = 0")
        return 0.0
    
    # Estandarizar datos usando z-score
    df_z = df_work.apply(stats.zscore)
    
    # Regresión lineal estandarizada
    model = smf.ols('y ~ x', data=df_z)
    result = model.fit()
    
    # Obtener coeficiente beta (pendiente)
    beta = result.params['x']
    
    return beta


def load_and_process_variables(results_folder, variables_config, target_metric):
    """
    Carga los CSV y calcula los coeficientes beta para cada variable.
    
    Args:
        results_folder (str): Ruta a la carpeta con los CSV
        variables_config (dict): Configuración de variables
        target_metric (str): Métrica objetivo
    
    Returns:
        tuple: (DataFrame con variables y betas, dict con colores por variable)
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
        
        # Calcular beta
        try:
            beta = calculate_beta(
                df, 
                var_key, 
                target_metric,
                is_categorical=var_config['is_categorical']
            )
            display_name = var_config['display_name']
            # Invertir beta para Occupancy para que quede positivo
            if display_name == 'Occupancy':
                beta = -beta
            results[display_name] = beta
            colors_map[display_name] = var_config.get('color', '#FF9966')  # Color por defecto si no existe
            print(f"[OK] {display_name}: beta = {beta:.4f}")
        except Exception as e:
            print(f"Error procesando {var_key}: {e}")
            continue
    
    if not results:
        raise ValueError("No se pudieron calcular coeficientes beta. Verifica los archivos CSV.")
    
    # Crear DataFrame para el gráfico
    plot_data = pd.DataFrame.from_dict(
        results, 
        orient='index', 
        columns=['beta']
    )
    
    # Ordenar por valor absoluto de beta (descendente) - de mayor a menor impacto
    plot_data = plot_data.sort_values(by=['beta'], ascending=False, key=abs)
    
    return plot_data, colors_map


def create_tm54_sensitivity_chart(plot_data, target_metric, colors_map):
    """
    Crea el gráfico de sensibilidad estilo TM54 Figura 7.
    
    Args:
        plot_data (pd.DataFrame): DataFrame con variables y coeficientes beta
        target_metric (str): Métrica objetivo analizada
        colors_map (dict): Diccionario con colores por variable (display_name -> color)
    
    Returns:
        go.Figure: Figura de Plotly
    """
    # Preparar datos
    variables = plot_data.index.tolist()
    betas = plot_data['beta'].values
    
    # Obtener colores individuales para cada variable
    colors = [colors_map.get(var, '#FF9966') for var in variables]  # Color por defecto si no existe
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar barras horizontales con colores individuales
    fig.add_trace(go.Bar(
        x=betas,
        y=variables,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='white', width=1.5)  # Borde blanco para mejor contraste
        ),
        text=[f'{b:.3f}' for b in betas],
        textposition='outside',
        textfont=dict(size=13, color='gray'),
        name='Beta coefficient'
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
            'text': f'<b>SENSITIVITY ANALYSIS: IMPACT ON {target_metric.upper()}</b>',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top',
            'font': {'size': 22, 'family': 'Arial', 'color': 'black'}
        },
        xaxis=dict(
            title=dict(
                text='Standardized Regression Coefficient (SRC)',
                font=dict(size=14, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            range=[min(betas.min() * 1.2, -1), max(betas.max() * 1.2, 1)]
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


def create_tm54_sensitivity_chart_vertical(plot_data, target_metric, colors_map):
    """
    Crea el gráfico de sensibilidad estilo TM54 con barras VERTICALES.
    
    Args:
        plot_data (pd.DataFrame): DataFrame con variables y coeficientes beta
        target_metric (str): Métrica objetivo analizada
        colors_map (dict): Diccionario con colores por variable (display_name -> color)
    
    Returns:
        go.Figure: Figura de Plotly
    """
    # Preparar datos
    variables = plot_data.index.tolist()
    betas = plot_data['beta'].values
    
    # Obtener colores individuales para cada variable
    colors = [colors_map.get(var, '#FF9966') for var in variables]  # Color por defecto si no existe
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar barras VERTICALES con colores individuales
    fig.add_trace(go.Bar(
        x=variables,
        y=betas,
        orientation='v',  # Vertical
        marker=dict(
            color=colors,
            line=dict(color='white', width=1.5)  # Borde blanco para mejor contraste
        ),
        text=[f'{b:.3f}' for b in betas],
        textposition='outside',
        textfont=dict(size=13, color='gray'),
        name='Beta coefficient'
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
            'text': f'<b>SENSITIVITY ANALYSIS: IMPACT ON {target_metric.upper()}</b>',
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
                text='Standardized Regression Coefficient (SRC)',
                font=dict(size=14, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            range=[min(betas.min() * 1.2, -1), max(betas.max() * 1.2, 1)]
        ),
        font={'size': 12, 'family': 'Arial', 'color': 'gray'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=max(600, len(variables) * 120),
        height=700,
        margin=dict(l=80, r=100, t=120, b=150),  # Más margen inferior para etiquetas rotadas
        showlegend=False
    )
    
    return fig


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Análisis de Sensibilidad - Estilo TM54")
    print("=" * 60)
    print(f"Métrica objetivo: {TARGET_METRIC}")
    print(f"Carpeta de resultados: {RESULTS_FOLDER}")
    print("-" * 60)
    
    try:
        # Cargar datos y calcular betas
        plot_data, colors_map = load_and_process_variables(
            RESULTS_FOLDER, 
            VARIABLES_CONFIG, 
            TARGET_METRIC
        )
        
        print("-" * 60)
        print("\nCoeficientes Beta calculados:")
        print(plot_data)
        print("-" * 60)
        
        # Crear gráficos con colores personalizados (horizontal y vertical)
        fig_horizontal = create_tm54_sensitivity_chart(plot_data, TARGET_METRIC, colors_map)
        fig_vertical = create_tm54_sensitivity_chart_vertical(plot_data, TARGET_METRIC, colors_map)
        
        # Crear directorio de salida con fecha y hora en Resultados/
        script_dir = Path(__file__).parent.parent
        resultados_dir = script_dir / 'Resultados'
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_dir = resultados_dir / f'Sensibilidad_TM54_{timestamp}'
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n✓ Directorio de salida: {output_dir.name}")
        
        # Nombre del archivo: limpiar caracteres especiales de la métrica
        metric_clean = TARGET_METRIC.replace('/', '_').replace('(', '').replace(')', '')
        
        # Guardar versión HORIZONTAL
        output_file_h = output_dir / f'Sensibilidad_TM54_Horizontal_{metric_clean}.png'
        fig_horizontal.write_image(
            str(output_file_h),
            width=1200,
            height=max(600, len(plot_data) * 100),
            scale=2  # Doble resolución para mejor calidad
        )
        print(f"\n[OK] Imagen HORIZONTAL guardada en: {output_file_h.name}")
        print(f"     Dimensiones: {1200}x{max(600, len(plot_data) * 100)} px (escala 2x)")
        
        # Guardar versión VERTICAL
        output_file_v = output_dir / f'Sensibilidad_TM54_Vertical_{metric_clean}.png'
        fig_vertical.write_image(
            str(output_file_v),
            width=max(800, len(plot_data) * 150),
            height=1000,
            scale=2  # Doble resolución para mejor calidad
        )
        print(f"[OK] Imagen VERTICAL guardada en: {output_file_v.name}")
        print(f"     Dimensiones: {max(800, len(plot_data) * 150)}x1000 px (escala 2x)")
        print(f"\n📁 Todos los archivos guardados en: {output_dir}")
        
        # Opcional: También guardar HTML interactivo (descomentar si lo necesitas)
        # html_file = output_dir / f'Sensibilidad_TM54_{metric_clean}.html'
        # fig.write_html(str(html_file))
        # print(f"[OK] Version HTML guardada en: {html_file}")
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] Error: {e}")
        print("\nAsegurate de que la carpeta 'resultados' existe y contiene los archivos CSV.")
    except ValueError as e:
        print(f"\n[ERROR] Error: {e}")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()

