"""
==========================================
Uncertainty Analysis by End Use - TM54 Style
==========================================

Module description
------------------
Creates box plots showing uncertainty ranges for different energy end uses,
following CIBSE TM54 Figure 8 style. Reads Para_sim_table.csv and generates
box plots for each energy end-use category.

The chart displays:
- Box plots for each end-use category
- Color-coded by category (Heating, Cooling, DHW, Lighting, Equipment, etc.)
- Shows quartiles, median, and outliers
- Professional styling matching TM54 standards

Usage
-----
python chart_uncertainty_enduse.py

The script will:
1. Load Para_sim_table.csv from 'Resultados' folder
2. Process data for each end-use category
3. Generate and display TM54-style box plot chart
4. Save as PNG image automatically

Notes
-----
- Requires: pandas, numpy, plotly, scipy
- Input: Para_sim_table.csv
- Output: Interactive Plotly chart saved as PNG
- Categories can be easily enabled/disabled via configuration
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN - Fácil activar/desactivar categorías
# ============================================================================

# Mapeo de categorías de uso final y sus columnas en el CSV
END_USE_CONFIG = {
    'Lighting': {
        'columns': ['Interior_lighting_kWh/m2', 'Exterior_lighting_kWh/m2'],
        'enabled': True,
        'color': '#A699A9',  # Gris - iluminación (igual que en sensibilidad)
        'operation': 'sum'  # Sumar interior y exterior
    },
    'Space heating': {
        'columns': ['Space_heating_(elec)_kWh/m2'],
        'enabled': True,
        'color': '#E74C3C',  # Rojo - calefacción (mantener)
        'operation': 'single'  # Columna W (eléctrica)
    },
    'Space cooling': {
        'columns': ['Space_cooling_kWh/m2'],
        'enabled': True,
        'color': '#3498DB',  # Azul - refrigeración (mantener)
        'operation': 'single'  # Columna X
    },
    'Fans interior': {
        'columns': ['Fans_interior_kWh/m2'],
        'enabled': True,
        'color': '#95A5A6',  # Gris - ventilación (mantener)
        'operation': 'single'  # Columna Z
    },
    'DHW heating': {
        'columns': ['DHW_heating_kWh/m2'],
        'enabled': True,
        'color': '#CCCCFF',  # Morado-ACS (igual que DHW en sensibilidad)
        'operation': 'single'  # Columna AA
    },
    'Receptacle equipment': {
        'columns': ['Receptacle_equipment_kWh/m2'],
        'enabled': True,
        'color': '#CCECFF',  # Azulito-EQUIPMENT (igual que Equipment en sensibilidad)
        'operation': 'single'  # Columna AB
    }
}

# Carpeta donde está el CSV
RESULTS_FOLDER = 'Resultados'  # Relativo a la carpeta del script
CSV_FILE = 'Para_sim_table.csv'

# ============================================================================
# FUNCIONES
# ============================================================================

def process_end_use_data(df, end_use_config):
    """
    Procesa los datos para cada categoría de uso final.
    
    Args:
        df (pd.DataFrame): DataFrame con los datos de simulación
        end_use_config (dict): Configuración de categorías de uso final
    
    Returns:
        pd.DataFrame: DataFrame con datos procesados para box plots
    """
    processed_data = []
    
    for category, config in end_use_config.items():
        if not config['enabled']:
            continue
        
        columns = config['columns']
        
        # Verificar que todas las columnas existen
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            print(f"Advertencia: Columnas faltantes para {category}: {missing_cols}")
            continue
        
        # Calcular valor según la operación
        if config['operation'] == 'sum':
            # Sumar múltiples columnas
            values = df[columns].sum(axis=1)
        elif config['operation'] == 'single':
            # Usar una sola columna
            values = df[columns[0]]
        else:
            print(f"Advertencia: Operación desconocida para {category}: {config['operation']}")
            continue
        
        # Filtrar valores nulos (permitir ceros para Space heating)
        values = values.dropna()
        # No filtrar ceros, ya que pueden ser válidos (ej: Space heating puede ser 0)
        
        if len(values) == 0:
            print(f"Advertencia: No hay datos válidos para {category}")
            continue
        
        # Agregar a la lista
        for value in values:
            processed_data.append({
                'Category': category,
                'Value': value,
                'Color': config['color']
            })
    
    if not processed_data:
        raise ValueError("No se pudieron procesar datos para ninguna categoría.")
    
    return pd.DataFrame(processed_data)


def create_tm54_uncertainty_chart(plot_data, end_use_config):
    """
    Crea el gráfico de incertidumbre estilo TM54 Figura 8.
    
    Args:
        plot_data (pd.DataFrame): DataFrame con datos procesados
        end_use_config (dict): Configuración de categorías con colores
    
    Returns:
        go.Figure: Figura de Plotly
    """
    # Obtener categorías habilitadas en orden
    categories = [cat for cat, config in end_use_config.items() 
                  if config['enabled'] and cat in plot_data['Category'].unique()]
    
    # Crear figura
    fig = go.Figure()
    
    # Agregar box plot para cada categoría
    for category in categories:
        category_data = plot_data[plot_data['Category'] == category]['Value']
        color = end_use_config[category]['color']
        
        fig.add_trace(go.Box(
            y=category_data,
            name=category,
            boxmean=False,  # Sin rombo de media/desviación estándar
            marker_color=color,
            line=dict(color='black', width=2),
            fillcolor=color,
            opacity=0.7,
            showlegend=True,
            width=0.6  # Hacer las cajas más anchas (0.6 = 60% del espacio disponible)
        ))
    
    # Actualizar layout
    fig.update_layout(
        title={
            'text': '<b>UNCERTAINTY ANALYSIS: ENERGY USE BY END USE CATEGORY</b><br>'
                   '<sub>Distribution of energy consumption across parametric simulations</sub>',
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98,
            'yanchor': 'top',
            'font': {'size': 22, 'family': 'Arial', 'color': 'black'}
        },
        xaxis=dict(
            title=dict(
                text='End Use Category',
                font=dict(size=18, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            tickfont=dict(size=18, family='Arial', color='black')
        ),
        yaxis=dict(
            title=dict(
                text='Energy Use Intensity (kWh/m²/year)',
                font=dict(size=18, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor='lightgray',
            tickfont=dict(size=16, family='Arial', color='black')
        ),
        font={'size': 12, 'family': 'Arial', 'color': 'gray'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1400,
        height=900,
        margin=dict(l=100, r=100, t=120, b=100),
        boxmode='group',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=13, family='Arial', color='black'),
            title=dict(text='Category', font=dict(size=14, family='Arial'))
        )
    )
    
    
    return fig


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Análisis de Incertidumbre por Uso final - Estilo TM54")
    print("=" * 60)
    print(f"Archivo CSV: {CSV_FILE}")
    print(f"Carpeta de resultados: {RESULTS_FOLDER}")
    print("-" * 60)
    
    try:
        # Obtener ruta del CSV
        script_dir = Path(__file__).parent.parent
        csv_path = script_dir / RESULTS_FOLDER / CSV_FILE
        
        if not csv_path.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo '{CSV_FILE}'. "
                f"Ruta esperada: {csv_path}"
            )
        
        # Cargar CSV (usar punto y coma como separador)
        print(f"Cargando datos de: {csv_path}")
        df = pd.read_csv(csv_path, sep=';')
        print(f"[OK] Datos cargados: {len(df)} simulaciones")
        
        # Procesar datos por categoría
        print("\nProcesando categorías de uso final...")
        plot_data = process_end_use_data(df, END_USE_CONFIG)
        
        print(f"[OK] Datos procesados para {plot_data['Category'].nunique()} categorías")
        print(f"     Total de puntos de datos: {len(plot_data)}")
        
        # Mostrar estadísticas resumidas
        print("\nEstadísticas por categoría:")
        print("-" * 60)
        for category in plot_data['Category'].unique():
            cat_data = plot_data[plot_data['Category'] == category]['Value']
            print(f"{category:20s}: "
                  f"Media={cat_data.mean():6.2f}, "
                  f"Mediana={cat_data.median():6.2f}, "
                  f"Std={cat_data.std():6.2f}")
        
        # Crear gráfico
        print("\nGenerando gráfico...")
        fig = create_tm54_uncertainty_chart(plot_data, END_USE_CONFIG)
        
        # Crear directorio de salida con fecha y hora en Resultados/
        script_dir = Path(__file__).parent.parent
        resultados_dir = script_dir / 'Resultados'
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        output_dir = resultados_dir / f'Uncertainty_EndUse_{timestamp}'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'Incertidumbre_UsoFinal_TM54.png'
        
        # Guardar como PNG (alta resolución)
        fig.write_image(
            str(output_file),
            width=1600,
            height=1100,
            scale=2  # Doble resolución para mejor calidad
        )
        
        print(f"\n[OK] Imagen guardada en: {output_file.name}")
        print(f"     Dimensiones: 1600x1100 px (escala 2x)")
        print(f"     Ubicación: {output_dir}")
        
        # Opcional: También guardar HTML interactivo (descomentar si lo necesitas)
        # html_file = output_dir / 'Incertidumbre_UsoFinal_TM54.html'
        # fig.write_html(str(html_file))
        # print(f"[OK] Version HTML guardada en: {html_file}")
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] Error: {e}")
        print(f"\nAsegurate de que el archivo '{CSV_FILE}' existe en la carpeta '{RESULTS_FOLDER}'.")
    except ValueError as e:
        print(f"\n[ERROR] Error: {e}")
    except Exception as e:
        print(f"\n[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()

