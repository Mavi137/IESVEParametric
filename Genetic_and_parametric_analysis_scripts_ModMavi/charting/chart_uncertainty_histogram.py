"""
==========================================
Uncertainty Histogram Analysis - TM54 Style
==========================================

Module description
------------------
Creates uncertainty histograms showing the distribution of output metrics
across parametric simulations. These histograms show how results vary,
helping to understand the range and probability of different outcomes.

The charts display:
- Histogram showing frequency distribution of output values
- Box plot in the margin (optional)
- Statistics (mean, median, std, quartiles) as annotations
- Density curve overlay (KDE)

Usage
-----
python chart_uncertainty_histogram.py

The script will:
1. Load Para_sim_table.csv from 'Resultados' folder
2. Generate uncertainty histograms for each configured output metric
3. Save as PNG images automatically

Notes
-----
- Requires: pandas, numpy, plotly, scipy
- Input: Para_sim_table.csv
- Output: PNG images saved automatically
- Metrics can be easily enabled/disabled via configuration
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN - Fácil activar/desactivar métricas
# ============================================================================

# Métricas de salida a analizar
OUTPUT_METRICS = {
    'EUI_kWh/m2': {
        'enabled': True,
        'display_name': 'Energy Use Intensity (EUI)',
        'color': '#9B59B6',  # Púrpura - total
        'unit': 'kWh/m²'
    },
    'Elec_kWh/m2': {
        'enabled': True,
        'display_name': 'Electricity Consumption',
        'color': '#3498DB',  # Azul - electricidad
        'unit': 'kWh/m²'
    },
    'Gas_kWh/m2': {
        'enabled': True,
        'display_name': 'Gas Consumption',
        'color': '#E74C3C',  # Rojo - gas
        'unit': 'kWh/m²'
    },
    'CE_kgCO2/m2': {
        'enabled': True,
        'display_name': 'Carbon Emissions',
        'color': '#27AE60',  # Verde - emisiones
        'unit': 'kg CO₂/m²'
    }
}

# Carpeta donde está el CSV
RESULTS_FOLDER = 'Resultados'
CSV_FILE = 'Para_sim_table.csv'

# ============================================================================
# FUNCIONES
# ============================================================================

def create_uncertainty_histogram(metric_key, metric_config, values):
    """
    Crea un histograma de incertidumbre para una métrica de salida.
    
    Args:
        metric_key (str): Clave de la métrica
        metric_config (dict): Configuración de la métrica
        values (pd.Series): Valores de la métrica
    
    Returns:
        go.Figure: Figura de Plotly
    """
    # Filtrar valores nulos
    values_clean = values.dropna()
    
    if len(values_clean) == 0:
        raise ValueError(f"No hay datos válidos para {metric_key}")
    
    # Calcular estadísticas
    mean_val = values_clean.mean()
    median_val = values_clean.median()
    std_val = values_clean.std()
    q1 = values_clean.quantile(0.25)
    q3 = values_clean.quantile(0.75)
    min_val = values_clean.min()
    max_val = values_clean.max()
    
    # Crear bins para el histograma
    n_bins = min(50, max(10, int(np.sqrt(len(values_clean)))))
    hist_data, bin_edges = np.histogram(values_clean, bins=n_bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]
    
    # Crear figura
    fig = go.Figure()
    
    # Histograma principal
    fig.add_trace(go.Bar(
        x=bin_centers,
        y=hist_data,
        marker_color=metric_config['color'],
        marker_line=dict(color='white', width=1),
        opacity=0.7,
        name='Frequency',
        width=bin_width * 0.9
    ))
    
    # Curva de densidad (KDE)
    if len(values_clean) > 1:
        try:
            kde = stats.gaussian_kde(values_clean)
            x_density = np.linspace(values_clean.min(), values_clean.max(), 200)
            y_density = kde(x_density) * len(values_clean) * bin_width
            
            fig.add_trace(go.Scatter(
                x=x_density,
                y=y_density,
                mode='lines',
                name='Density curve',
                line=dict(color='darkblue', width=2.5),
                fill='tonexty',
                fillcolor='rgba(0, 0, 139, 0.15)'
            ))
        except:
            pass
    
    # Línea de media
    max_freq = hist_data.max()
    fig.add_vline(
        x=mean_val,
        line_dash="dash",
        line_color="red",
        line_width=2,
        annotation_text="Mean",
        annotation_position="top"
    )
    
    # Línea de mediana
    fig.add_vline(
        x=median_val,
        line_dash="dot",
        line_color="green",
        line_width=2,
        annotation_text="Median",
        annotation_position="top"
    )
    
    # Actualizar layout
    fig.update_layout(
        title={
            'text': f'<b>UNCERTAINTY ANALYSIS: {metric_config["display_name"].upper()}</b><br>'
                   '<sub>Distribution of results across parametric simulations</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top',
            'font': {'size': 22, 'family': 'Arial', 'color': 'black'}
        },
        xaxis=dict(
            title=dict(
                text=f'{metric_config["display_name"]} ({metric_config["unit"]})',
                font=dict(size=14, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(size=12, family='Arial', color='gray')
        ),
        yaxis=dict(
            title=dict(
                text='Frequency',
                font=dict(size=14, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor='lightgray'
        ),
        font={'size': 12, 'family': 'Arial', 'color': 'gray'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1000,
        height=700,
        margin=dict(l=80, r=200, t=120, b=80),
        showlegend=True,
        legend=dict(
            orientation='v',
            yanchor='top',
            y=0.98,
            xanchor='left',
            x=1.02,
            font=dict(size=13, family='Arial', color='black'),
            title=dict(text='Legend', font=dict(size=14, family='Arial'))
        )
    )
    
    # Agregar estadísticas como anotación
    stats_text = (
        f'<b>Summary Statistics</b><br>'
        f'Count: {len(values_clean)}<br>'
        f'Mean: {mean_val:.2f}<br>'
        f'Median: {median_val:.2f}<br>'
        f'Std Dev: {std_val:.2f}<br>'
        f'Min: {min_val:.2f}<br>'
        f'Q1: {q1:.2f}<br>'
        f'Q3: {q3:.2f}<br>'
        f'Max: {max_val:.2f}'
    )
    
    fig.add_annotation(
        text=stats_text,
        xref='paper',
        yref='paper',
        x=1.15,
        y=0.5,
        showarrow=False,
        font=dict(size=10, family='Arial', color='gray'),
        bgcolor='rgba(240, 240, 240, 0.8)',
        bordercolor='gray',
        borderwidth=1,
        borderpad=8,
        align='left'
    )
    
    return fig


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Análisis de Incertidumbre - Histogramas TM54")
    print("=" * 60)
    print(f"Archivo CSV: {CSV_FILE}")
    print(f"Carpeta de resultados: {RESULTS_FOLDER}")
    print("-" * 60)
    
    # Obtener ruta del CSV
    script_dir = Path(__file__).parent.parent
    csv_path = script_dir / RESULTS_FOLDER / CSV_FILE
    
    if not csv_path.exists():
        print(f"\n[ERROR] No se encontró el archivo '{CSV_FILE}'.")
        print(f"        Ruta esperada: {csv_path}")
        exit(1)
    
    # Cargar CSV (usar punto y coma como separador)
    print(f"Cargando datos de: {csv_path}")
    df = pd.read_csv(csv_path, sep=';')
    print(f"[OK] Datos cargados: {len(df)} simulaciones")
    
    output_dir = Path(__file__).parent.parent / 'Logs' / 'analisis'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    error_count = 0
    
    for metric_key, metric_config in OUTPUT_METRICS.items():
        if not metric_config['enabled']:
            continue
        
        try:
            print(f"\nProcesando: {metric_config['display_name']}...")
            
            # Verificar que la columna existe
            if metric_key not in df.columns:
                print(f"  [ERROR] Columna '{metric_key}' no encontrada en el CSV")
                error_count += 1
                continue
            
            # Obtener valores
            values = df[metric_key]
            
            # Crear gráfico
            fig = create_uncertainty_histogram(metric_key, metric_config, values)
            
            # Guardar imagen
            metric_name_clean = metric_key.replace('/', '_').replace('(', '').replace(')', '').replace(' ', '_')
            output_file = output_dir / f'Incertidumbre_{metric_name_clean}.png'
            
            fig.write_image(
                str(output_file),
                width=1200,
                height=900,
                scale=2
            )
            
            print(f"  [OK] Imagen guardada: {output_file.name}")
            success_count += 1
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            error_count += 1
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Resumen: {success_count} histogramas generados exitosamente")
    if error_count > 0:
        print(f"         {error_count} errores encontrados")
    print("=" * 60)

