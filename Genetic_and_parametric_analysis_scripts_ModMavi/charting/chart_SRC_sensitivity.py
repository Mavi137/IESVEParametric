"""
==========================================
SRC Sensitivity Analysis - CIBSE TM54 Method
==========================================

Module description
------------------
Calcula Standardized Regression Coefficients (SRC) siguiendo la metodología 
CIBSE TM54 para análisis de sensibilidad paramétrica. Utiliza regresión 
multivariada con variables estandarizadas para identificar qué parámetros 
tienen mayor influencia en la variabilidad del EUI.

El script:
- Carga datos de diseño factorial completo (3×3×3×3 = 81 simulaciones)
- Estandariza todas las variables (X e Y) usando z-score
- Realiza regresión multivariada con statsmodels
- Calcula correlaciones simples (Pearson) para comparación
- Genera 8 visualizaciones: Tornado charts, scatter plots, matriz de correlación,
  histograma de incertidumbre, box plots, análisis de residuos y contribución a varianza
- Valida resultados (multicolinealidad, R², significancia)
- Exporta resultados en CSV y gráficos en PNG

Usage
-----
python chart_SRC_sensitivity.py

El script buscará automáticamente Para_sim_table.csv en:
- Genetic_and_parametric_analysis_scripts_ModMavi/Resultados/

Output
------
- sensitivity_SRC_results.csv: Tabla con SRC, correlaciones, p-values
- SRC_Tornado_TM54_Horizontal_EUI_kWh_m2.png: Gráfico tornado horizontal
- SRC_Tornado_TM54_Vertical_EUI_kWh_m2.png: Gráfico tornado vertical
- SRC_Scatter_TM54_EUI_kWh_m2.png: Scatter plots con líneas de regresión
- SRC_CorrelationMatrix_TM54_EUI_kWh_m2.png: Matriz de correlación
- SRC_UncertaintyHistogram_TM54_EUI_kWh_m2.png: Histograma de distribución EUI
- SRC_BoxPlots_TM54_EUI_kWh_m2.png: Box plots por nivel de parámetro
- SRC_Residuals_TM54_EUI_kWh_m2.png: Análisis de residuos del modelo
- SRC_VarianceContribution_TM54_EUI_kWh_m2.png: Contribución % a varianza

Notes
-----
- Requiere: pandas, numpy, scipy, statsmodels, plotly, kaleido (para PNG)
- Opcional: tabulate (para mejor formato de tablas)
- Todas las variables deben ser continuas numéricas
- Separador CSV: punto y coma (;)
- Decimal: punto (.)
"""

import pandas as pd
import numpy as np
from scipy.stats import zscore, probplot
import statsmodels.api as sm
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Tuple, Dict, List
from datetime import datetime
import sys

# Intentar importar tabulate, si no está disponible usar función alternativa
try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

# Parámetros de entrada (variables continuas) con colores personalizados
# Mismo esquema de colores que chart_sensitivity_tm54.py
PARAMS_CONFIG = {
    'dhw_lph_per_person': {
        'display_name': 'DHW',
        'color': '#CCCCFF'  # Morado - ACS (Agua Caliente Sanitaria)
    },
    'people_m2_per_person': {
        'display_name': 'Occupancy',
        'color': '#fea1ff'  # Rosa - Ocupación
    },
    'gen_lighting_gain': {
        'display_name': 'Lighting',
        'color': '#A699A9'  # Gris - Iluminación
    },
    'computer_gain': {
        'display_name': 'Equipment',
        'color': '#CCECFF'  # Azulito - Equipamiento
    }
}

# Lista de parámetros (orden)
PARAMS = list(PARAMS_CONFIG.keys())

# Variable de salida (target)
TARGET = 'EUI_kWh/m2'

# Carpeta donde está el CSV (relativo a la carpeta padre del script)
RESULTS_FOLDER = 'Resultados'


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def format_table_simple(df: pd.DataFrame) -> str:
    """
    Formatea un DataFrame como tabla simple sin usar tabulate.
    
    Args:
        df: DataFrame a formatear
        
    Returns:
        String con la tabla formateada
    """
    # Obtener nombres de columnas
    cols = df.columns.tolist()
    
    # Calcular ancho de cada columna
    col_widths = {}
    for col in cols:
        # Ancho mínimo: longitud del nombre de columna
        max_width = len(str(col))
        # Revisar valores en la columna
        for val in df[col]:
            max_width = max(max_width, len(f"{val:.4f}" if isinstance(val, (int, float)) else str(val)))
        col_widths[col] = max_width + 2  # Espacio extra
    
    # Crear línea separadora
    total_width = sum(col_widths.values()) + len(cols) - 1
    separator = "=" * total_width
    
    # Construir tabla
    lines = [separator]
    
    # Encabezados
    header = " | ".join(str(col).ljust(col_widths[col]) for col in cols)
    lines.append(header)
    lines.append(separator)
    
    # Filas de datos
    for _, row in df.iterrows():
        row_str = " | ".join(
            (f"{val:.4f}" if isinstance(val, (int, float)) else str(val)).ljust(col_widths[col])
            for col, val in zip(cols, row)
        )
        lines.append(row_str)
    
    lines.append(separator)
    
    return "\n".join(lines)


# ============================================================================
# FUNCIONES DE CARGA Y LIMPIEZA
# ============================================================================

def find_csv_file() -> Path:
    """
    Busca el archivo Para_sim_table.csv en la carpeta Resultados.
    
    Returns:
        Path: Ruta al archivo CSV encontrado
        
    Raises:
        FileNotFoundError: Si no se encuentra el archivo
    """
    # Obtener ruta relativa desde charting/ hacia Resultados/
    script_dir = Path(__file__).parent.parent
    csv_path = script_dir / RESULTS_FOLDER / 'Para_sim_table.csv'
    
    if csv_path.exists():
        print(f"✓ Archivo encontrado: {csv_path}")
        return csv_path
    
    raise FileNotFoundError(
        f"No se encontró Para_sim_table.csv en: {csv_path}\n"
        "Asegúrate de que el archivo existe en la carpeta 'Resultados'."
    )


def load_and_validate_data(
    csv_path: Path,
    params: List[str],
    target: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """
    Carga el CSV y valida que contenga las columnas necesarias.
    
    Args:
        csv_path: Ruta al archivo CSV
        params: Lista de nombres de parámetros
        target: Nombre de la variable objetivo
        
    Returns:
        Tuple: (DataFrame completo, DataFrame X con parámetros, Series y con target)
        
    Raises:
        ValueError: Si faltan columnas o hay valores NaN
    """
    try:
        # Intentar cargar con punto y coma como separador
        df = pd.read_csv(csv_path, sep=';', decimal='.')
    except Exception as e:
        # Si falla, intentar con coma
        try:
            df = pd.read_csv(csv_path, sep=',', decimal='.')
            print("⚠️  Advertencia: Se usó coma como separador (se esperaba punto y coma)")
        except Exception as e2:
            raise ValueError(f"Error al cargar CSV: {e}. También falló con coma: {e2}")
    
    print(f"✓ Datos cargados: {len(df)} simulaciones")
    print(f"✓ Columnas disponibles: {len(df.columns)}")
    
    # Verificar que existen todas las columnas necesarias
    missing_params = [p for p in params if p not in df.columns]
    if missing_params:
        raise ValueError(
            f"Faltan parámetros en el CSV: {missing_params}\n"
            f"Columnas disponibles: {list(df.columns)}"
        )
    
    if target not in df.columns:
        raise ValueError(
            f"Variable objetivo '{target}' no encontrada en el CSV.\n"
            f"Columnas disponibles: {list(df.columns)}"
        )
    
    # Extraer X e Y
    X = df[params].copy()
    y = df[target].copy()
    
    # Verificar que no hay NaN
    nan_in_X = X.isna().sum().sum()
    nan_in_y = y.isna().sum()
    
    if nan_in_X > 0:
        print(f"⚠️  Advertencia: {nan_in_X} valores NaN encontrados en parámetros")
        print("   Eliminando filas con NaN...")
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask].copy()
        y = y[mask].copy()
        print(f"✓ Datos después de limpieza: {len(X)} simulaciones")
    
    if nan_in_y > 0 and nan_in_X == 0:
        raise ValueError(f"Hay {nan_in_y} valores NaN en la variable objetivo '{target}'")
    
    # Verificar que todas las variables son numéricas
    non_numeric = []
    for col in params:
        if not pd.api.types.is_numeric_dtype(X[col]):
            non_numeric.append(col)
    
    if non_numeric:
        raise ValueError(
            f"Las siguientes columnas no son numéricas: {non_numeric}\n"
            "Todas las variables deben ser continuas numéricas."
        )
    
    print(f"✓ Parámetros: {params}")
    print(f"\nRangos de variación:")
    print(X.describe())
    
    return df, X, y


# ============================================================================
# FUNCIONES DE ESTANDARIZACIÓN
# ============================================================================

def standardize_variables(
    X: pd.DataFrame,
    y: pd.Series
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Estandariza todas las variables usando z-score (media=0, std=1).
    
    Args:
        X: DataFrame con parámetros
        y: Series con variable objetivo
        
    Returns:
        Tuple: (X_std, y_std) variables estandarizadas
    """
    # Estandarizar X
    X_std = X.apply(zscore)
    
    # Estandarizar y
    y_std = pd.Series(zscore(y), index=y.index)
    
    # Verificar estandarización
    print(f"\n✓ Medias después de estandarizar (deben ser ≈0):")
    means_X = X_std.mean()
    for param, mean_val in means_X.items():
        print(f"   {param}: {mean_val:.6f}")
    print(f"   {TARGET}: {y_std.mean():.6f}")
    
    print(f"\n✓ Desviaciones estándar (deben ser ≈1):")
    stds_X = X_std.std()
    for param, std_val in stds_X.items():
        print(f"   {param}: {std_val:.6f}")
    print(f"   {TARGET}: {y_std.std():.6f}")
    
    return X_std, y_std


# ============================================================================
# FUNCIONES DE REGRESIÓN
# ============================================================================

def fit_multivariate_regression(
    X_std: pd.DataFrame,
    y_std: pd.Series
) -> sm.regression.linear_model.RegressionResultsWrapper:
    """
    Ajusta modelo de regresión multivariada con variables estandarizadas.
    
    Args:
        X_std: Parámetros estandarizados
        y_std: Variable objetivo estandarizada
        
    Returns:
        Modelo de regresión ajustado de statsmodels
    """
    # Añadir constante (intercepto)
    X_std_with_const = sm.add_constant(X_std)
    
    # Ajustar modelo OLS
    model = sm.OLS(y_std, X_std_with_const).fit()
    
    return model


def calculate_simple_correlations(
    X: pd.DataFrame,
    y: pd.Series,
    params: List[str]
) -> Dict[str, float]:
    """
    Calcula correlación de Pearson (bivariada) para cada parámetro.
    
    Args:
        X: DataFrame con parámetros originales
        y: Series con variable objetivo
        params: Lista de nombres de parámetros
        
    Returns:
        Diccionario con correlaciones {param: correlation}
    """
    correlations = {}
    for param in params:
        r = np.corrcoef(X[param], y)[0, 1]
        correlations[param] = r
    
    return correlations


# ============================================================================
# FUNCIONES DE RESULTADOS
# ============================================================================

def create_results_table(
    params: List[str],
    model: sm.regression.linear_model.RegressionResultsWrapper,
    correlations: Dict[str, float]
) -> pd.DataFrame:
    """
    Crea DataFrame con todos los resultados del análisis.
    
    Args:
        params: Lista de nombres de parámetros
        model: Modelo de regresión ajustado
        correlations: Diccionario con correlaciones simples
        
    Returns:
        DataFrame con resultados ordenados por ranking
    """
    # Extraer SRC (excluir intercepto)
    src_values = model.params[1:]
    p_values = model.pvalues[1:]
    
    # Crear DataFrame
    results = pd.DataFrame({
        'Parameter': params,
        'SRC': src_values.values,
        'r (correlation)': [correlations[p] for p in params],
        'p-value': p_values.values,
        'Significant': [
            '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
            for p in p_values.values
        ]
    })
    
    # Añadir ranking por |SRC|
    results['Ranking'] = results['SRC'].abs().rank(ascending=False).astype(int)
    results = results.sort_values('Ranking')
    
    return results


def validate_results(
    results: pd.DataFrame,
    model: sm.regression.linear_model.RegressionResultsWrapper,
    X: pd.DataFrame
) -> None:
    """
    Valida los resultados y muestra advertencias si es necesario.
    
    Args:
        results: DataFrame con resultados
        model: Modelo de regresión ajustado
        X: DataFrame con parámetros originales
    """
    r_squared = model.rsquared
    max_src = results['SRC'].abs().max()
    
    # Validar SRC
    if max_src > 1.5:
        print(f"\n⚠️  WARNING: SRC máximo = {max_src:.2f} > 1.5")
        print("   Posible multicolinealidad. Verificar correlación entre parámetros.")
        
        # Matriz de correlación entre parámetros
        corr_matrix = X.corr()
        print("\n   Correlación entre parámetros:")
        print(corr_matrix.round(4))
    else:
        print(f"\n✓ Todos los SRC dentro de rango razonable (máx |SRC| = {max_src:.2f})")
    
    # Validar R²
    if r_squared < 0.3:
        print(f"\n⚠️  WARNING: R² = {r_squared:.2f} < 0.3")
        print("   La relación podría ser no lineal o hay otros factores importantes.")
    else:
        print(f"\n✓ R² aceptable ({r_squared:.2f}), el modelo lineal explica bien los datos")
    
    # Contar parámetros significativos
    n_significant = (results['p-value'] < 0.05).sum()
    print(f"\n✓ Parámetros significativos (p < 0.05): {n_significant}/{len(results)}")


# ============================================================================
# FUNCIONES DE VISUALIZACIÓN
# ============================================================================

def create_tornado_chart_horizontal(
    results: pd.DataFrame,
    target_metric: str,
    params_config: Dict
) -> go.Figure:
    """
    Crea gráfico tornado horizontal (barras horizontales) de SRC con colores personalizados.
    
    Args:
        results: DataFrame con resultados ordenados por ranking
        target_metric: Nombre de la métrica objetivo
        params_config: Diccionario con configuración de parámetros (colores, nombres)
        
    Returns:
        Figura de Plotly
    """
    # Ordenar por valor absoluto de SRC (de mayor a menor impacto)
    results_plot = results.copy()
    results_plot = results_plot.sort_values('SRC', ascending=False, key=abs)
    
    # Obtener nombres de visualización y colores
    display_names = [params_config[p]['display_name'] for p in results_plot['Parameter']]
    colors = [params_config[p]['color'] for p in results_plot['Parameter']]
    src_values = results_plot['SRC'].values
    
    # Crear gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=display_names,
        x=src_values,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='white', width=1.5)  # Borde blanco para mejor contraste
        ),
        text=[f'{src:.3f}' for src in src_values],
        textposition='outside',
        textfont=dict(size=13, color='gray'),
        name='SRC'
    ))
    
    # Línea vertical en x=0
    fig.add_vline(
        x=0,
        line_width=2,
        line_color='black',
        line_dash='solid',
        annotation_text='No effect',
        annotation_position='top'
    )
    
    # Calcular rango apropiado
    max_abs_src = abs(src_values).max()
    x_range = [-max_abs_src * 1.2, max_abs_src * 1.2]
    
    # Actualizar layout estilo TM54
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
                font=dict(size=18, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black',
            range=x_range,
            tickfont=dict(size=16, family='Arial', color='black')
        ),
        yaxis=dict(
            title='',
            showgrid=False,
            tickfont=dict(size=18, family='Arial', color='black')
        ),
        font={'size': 12, 'family': 'Arial', 'color': 'gray'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=1200,
        height=max(600, len(display_names) * 100),
        margin=dict(l=250, r=100, t=120, b=80),
        showlegend=False
    )
    
    return fig


def create_tornado_chart_vertical(
    results: pd.DataFrame,
    target_metric: str,
    params_config: Dict
) -> go.Figure:
    """
    Crea gráfico tornado vertical (barras verticales) de SRC con colores personalizados.
    
    Args:
        results: DataFrame con resultados ordenados por ranking
        target_metric: Nombre de la métrica objetivo
        params_config: Diccionario con configuración de parámetros (colores, nombres)
        
    Returns:
        Figura de Plotly
    """
    # Ordenar por valor absoluto de SRC (de mayor a menor impacto)
    results_plot = results.copy()
    results_plot = results_plot.sort_values('SRC', ascending=False, key=abs)
    
    # Invertir signo del SRC de Occupancy solo para este gráfico vertical
    # (para que salga positivo como en chart_sensitivity_tm54.py)
    occupancy_mask = results_plot['Parameter'] == 'people_m2_per_person'
    if occupancy_mask.any():
        results_plot.loc[occupancy_mask, 'SRC'] = -results_plot.loc[occupancy_mask, 'SRC']
    
    # Obtener nombres de visualización y colores
    display_names = [params_config[p]['display_name'] for p in results_plot['Parameter']]
    colors = [params_config[p]['color'] for p in results_plot['Parameter']]
    src_values = results_plot['SRC'].values
    
    # Crear gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=display_names,
        y=src_values,
        orientation='v',
        marker=dict(
            color=colors,
            line=dict(color='white', width=1.5)  # Borde blanco para mejor contraste
        ),
        text=[f'{src:.3f}' for src in src_values],
        textposition='outside',
        textfont=dict(size=13, color='gray'),
        name='SRC'
    ))
    
    # Línea horizontal en y=0 (solo si hay valores negativos)
    # Como todos los valores son positivos después de invertir Occupancy, no se muestra
    
    # Calcular rango apropiado (solo parte positiva)
    max_src = src_values.max()
    min_src = src_values.min()
    # Rango desde 0 hasta el máximo con un poco de margen
    y_range = [0, max_src * 1.15]  # 15% de margen superior
    
    # Actualizar layout estilo TM54
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
            tickfont=dict(size=18, family='Arial', color='black'),
            tickangle=-45  # Rotar etiquetas para mejor legibilidad
        ),
        yaxis=dict(
            title=dict(
                text='Standardized Regression Coefficient (SRC)',
                font=dict(size=18, family='Arial', color='black')
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=False,  # No mostrar línea en y=0 ya que solo hay valores positivos
            range=y_range,
            tickfont=dict(size=16, family='Arial', color='black')
        ),
        font={'size': 12, 'family': 'Arial', 'color': 'gray'},
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=max(800, len(display_names) * 150),
        height=1000,
        margin=dict(l=80, r=100, t=120, b=150),  # Más margen inferior para etiquetas rotadas
        showlegend=False
    )
    
    return fig


def create_scatter_plots(
    X: pd.DataFrame,
    y: pd.Series,
    params: List[str],
    params_config: Dict,
    correlations: Dict[str, float]
) -> go.Figure:
    """
    Crea scatter plots con líneas de regresión para cada parámetro.
    
    Args:
        X: DataFrame con parámetros originales
        y: Series con variable objetivo
        params: Lista de nombres de parámetros
        params_config: Diccionario con configuración de parámetros (colores, nombres)
        correlations: Diccionario con correlaciones
        
    Returns:
        Figura de Plotly con subplots
    """
    # Crear subplots 2x2
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f"{params_config[p]['display_name']}<br>r² = {correlations[p]**2:.3f}" 
            for p in params
        ],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    # Mapeo de posiciones
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    
    for i, param in enumerate(params):
        row, col = positions[i]
        color = params_config[param]['color']
        
        # Scatter plot (variables ORIGINALES, no estandarizadas)
        fig.add_trace(
            go.Scatter(
                x=X[param],
                y=y,
                mode='markers',
                marker=dict(size=6, opacity=0.6, color=color),
                name=params_config[param]['display_name'],
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Línea de regresión
        z = np.polyfit(X[param], y, 1)
        p = np.poly1d(z)
        x_line = np.linspace(X[param].min(), X[param].max(), 100)
        
        fig.add_trace(
            go.Scatter(
                x=x_line,
                y=p(x_line),
                mode='lines',
                line=dict(color='red', width=2),
                name='Regression',
                showlegend=False
            ),
            row=row, col=col
        )
        
        # Etiquetas de ejes
        fig.update_xaxes(
            title_text=params_config[param]['display_name'], 
            title_font=dict(size=18, family='Arial', color='black'),
            tickfont=dict(size=16, family='Arial', color='black'),
            row=row, col=col
        )
        fig.update_yaxes(
            title_text="EUI (kWh/m²)", 
            title_font=dict(size=18, family='Arial', color='black'),
            tickfont=dict(size=16, family='Arial', color='black'),
            row=row, col=col
        )
    
    fig.update_layout(
        title_text="Parameter vs EUI - Individual R² Values",
        height=800,
        template='plotly_white'
    )
    
    return fig


# ============================================================================
# FUNCIONES DE EXPORTACIÓN
# ============================================================================

def get_output_directory() -> Path:
    """
    Crea y retorna un directorio de salida con fecha y hora en Resultados/.
    
    Returns:
        Path: Directorio de salida con formato YYYY-MM-DD_HH-MM-SS
    """
    # Obtener ruta a Resultados/
    script_dir = Path(__file__).parent.parent
    resultados_dir = script_dir / 'Resultados'
    
    # Crear subcarpeta con fecha y hora
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_dir = resultados_dir / f'SRC_Analysis_{timestamp}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir


def save_results(
    results: pd.DataFrame,
    output_dir: Path = None
) -> Path:
    """
    Guarda resultados en CSV.
    
    Args:
        results: DataFrame con resultados
        output_dir: Directorio de salida (None = carpeta actual)
        
    Returns:
        Path al archivo guardado
    """
    if output_dir is None:
        output_dir = Path.cwd()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'sensitivity_SRC_results.csv'
    results.to_csv(output_file, index=False)
    
    return output_file


def save_plots_png(
    fig_tornado_h: go.Figure,
    fig_tornado_v: go.Figure,
    fig_scatter: go.Figure,
    target_metric: str,
    output_dir: Path = None
) -> Tuple[Path, Path, Path]:
    """
    Guarda gráficos en PNG con estilo TM54.
    
    Args:
        fig_tornado_h: Figura del gráfico tornado horizontal
        fig_tornado_v: Figura del gráfico tornado vertical
        fig_scatter: Figura de scatter plots
        target_metric: Nombre de la métrica objetivo
        output_dir: Directorio de salida (None = Resultados/SRC_Analysis_YYYY-MM-DD_HH-MM-SS)
        
    Returns:
        Tuple: (Path tornado_h, Path tornado_v, Path scatter)
    """
    if output_dir is None:
        # Guardar en Resultados/ con subcarpeta de fecha y hora
        output_dir = get_output_directory()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Limpiar nombre de métrica para el archivo
    metric_clean = target_metric.replace('/', '_').replace('(', '').replace(')', '')
    
    # Guardar tornado horizontal
    tornado_h_file = output_dir / f'SRC_Tornado_TM54_Horizontal_{metric_clean}.png'
    fig_tornado_h.write_image(
        str(tornado_h_file),
        width=1200,
        height=max(600, len(PARAMS) * 100),
        scale=2  # Doble resolución para mejor calidad
    )
    
    # Guardar tornado vertical
    tornado_v_file = output_dir / f'SRC_Tornado_TM54_Vertical_{metric_clean}.png'
    fig_tornado_v.write_image(
        str(tornado_v_file),
        width=max(800, len(PARAMS) * 150),
        height=1000,
        scale=2  # Doble resolución para mejor calidad
    )
    
    # Guardar scatter plots
    scatter_file = output_dir / f'SRC_Scatter_TM54_{metric_clean}.png'
    fig_scatter.write_image(
        str(scatter_file),
        width=1600,
        height=1200,
        scale=2  # Doble resolución para mejor calidad
    )
    
    return tornado_h_file, tornado_v_file, scatter_file


# ============================================================================
# FUNCIONES DE VISUALIZACIONES ADICIONALES
# ============================================================================

def create_correlation_matrix(
    X: pd.DataFrame,
    y: pd.Series,
    output_path: Path
) -> go.Figure:
    """
    Crea heatmap de matriz de correlación entre parámetros y EUI.
    
    Args:
        X: DataFrame con parámetros
        y: Series con variable objetivo
        output_path: Ruta donde guardar el gráfico
        
    Returns:
        Figura de Plotly
    """
    # Combinar X e Y
    df_corr = X.copy()
    df_corr['EUI_kWh/m2'] = y.values
    
    # Calcular matriz de correlación
    corr_matrix = df_corr.corr()
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        zmin=-1,
        zmax=1,
        text=corr_matrix.values.round(3),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation (r)")
    ))
    
    fig.update_layout(
        title="Correlation Matrix - Parameters and EUI",
        height=600,
        width=700,
        template='plotly_white'
    )
    fig.update_xaxes(
        title_text="",
        tickfont=dict(size=16, family='Arial', color='black')
    )
    fig.update_yaxes(
        title_text="",
        tickfont=dict(size=16, family='Arial', color='black')
    )
    
    # Guardar
    fig.write_image(str(output_path), width=700, height=600, scale=2)
    print(f"  - {output_path.name}")
    
    return fig


def create_uncertainty_histogram(
    y: pd.Series,
    output_path: Path
) -> go.Figure:
    """
    Crea histograma de distribución del EUI con estadísticas.
    
    Args:
        y: Series con variable objetivo (EUI)
        output_path: Ruta donde guardar el gráfico
        
    Returns:
        Figura de Plotly
    """
    # Estadísticas
    mean_val = y.mean()
    median_val = y.median()
    std_val = y.std()
    p10 = y.quantile(0.10)
    p90 = y.quantile(0.90)
    min_val = y.min()
    max_val = y.max()
    
    # Histograma
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=y,
        nbinsx=20,
        name='EUI Distribution',
        marker=dict(color='steelblue', line=dict(color='white', width=1)),
        opacity=0.7
    ))
    
    # Líneas de estadísticas
    fig.add_vline(
        x=mean_val, 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"Mean: {mean_val:.1f}", 
        annotation_position="top"
    )
    fig.add_vline(
        x=median_val, 
        line_dash="dash", 
        line_color="green",
        annotation_text=f"Median: {median_val:.1f}", 
        annotation_position="top"
    )
    fig.add_vline(
        x=p10, 
        line_dash="dot", 
        line_color="orange",
        annotation_text=f"P10: {p10:.1f}", 
        annotation_position="bottom left"
    )
    fig.add_vline(
        x=p90, 
        line_dash="dot", 
        line_color="orange",
        annotation_text=f"P90: {p90:.1f}", 
        annotation_position="bottom right"
    )
    
    fig.update_layout(
        title=f"EUI Uncertainty Distribution<br>Range: [{min_val:.1f}, {max_val:.1f}] kWh/m² | σ = {std_val:.1f}",
        height=500,
        showlegend=True,
        template='plotly_white'
    )
    fig.update_xaxes(
        title_text="EUI (kWh/m²)",
        title_font=dict(size=18, family='Arial', color='black'),
        tickfont=dict(size=16, family='Arial', color='black')
    )
    fig.update_yaxes(
        title_text="Frequency",
        title_font=dict(size=18, family='Arial', color='black'),
        tickfont=dict(size=16, family='Arial', color='black')
    )
    
    # Guardar
    fig.write_image(str(output_path), width=1000, height=500, scale=2)
    print(f"  - {output_path.name}")
    
    return fig


def create_boxplots_by_parameter(
    X: pd.DataFrame,
    y: pd.Series,
    params: List[str],
    params_config: Dict,
    output_path: Path
) -> go.Figure:
    """
    Crea box plots mostrando distribución de EUI para cada nivel de cada parámetro.
    
    Args:
        X: DataFrame con parámetros
        y: Series con variable objetivo
        params: Lista de nombres de parámetros
        params_config: Diccionario con configuración de parámetros
        output_path: Ruta donde guardar el gráfico
        
    Returns:
        Figura de Plotly
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[params_config[p]['display_name'] for p in params],
        vertical_spacing=0.12,
        horizontal_spacing=0.1
    )
    
    positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    
    for i, param in enumerate(params):
        row, col = positions[i]
        
        # Obtener valores únicos del parámetro
        unique_vals = sorted(X[param].unique())
        
        for val in unique_vals:
            mask = X[param] == val
            eui_subset = y[mask]
            
            fig.add_trace(
                go.Box(
                    y=eui_subset,
                    name=f"{val}",
                    boxmean='sd',  # Mostrar media y std
                    marker=dict(size=4)
                ),
                row=row, col=col
            )
        
        fig.update_xaxes(
            title_text=params_config[param]['display_name'],
            title_font=dict(size=18, family='Arial', color='black'),
            tickfont=dict(size=16, family='Arial', color='black'),
            row=row, col=col
        )
        fig.update_yaxes(
            title_text="EUI (kWh/m²)",
            title_font=dict(size=18, family='Arial', color='black'),
            tickfont=dict(size=16, family='Arial', color='black'),
            row=row, col=col
        )
    
    fig.update_layout(
        title_text="EUI Distribution by Parameter Level",
        height=800,
        showlegend=False,
        template='plotly_white'
    )
    
    # Guardar
    fig.write_image(str(output_path), width=1600, height=800, scale=2)
    print(f"  - {output_path.name}")
    
    return fig


def create_residuals_plot(
    model: sm.regression.linear_model.RegressionResultsWrapper,
    X_std: pd.DataFrame,
    y_std: pd.Series,
    output_path: Path
) -> go.Figure:
    """
    Crea gráfico de residuos para diagnóstico del modelo.
    
    Args:
        model: Modelo de regresión ajustado
        X_std: Parámetros estandarizados
        y_std: Variable objetivo estandarizada
        output_path: Ruta donde guardar el gráfico
        
    Returns:
        Figura de Plotly
    """
    # Calcular residuos
    y_pred = model.predict(sm.add_constant(X_std))
    residuals = y_std - y_pred
    
    # Crear subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Residuals vs Fitted", "Q-Q Plot"),
        horizontal_spacing=0.12
    )
    
    # 1. Residuals vs Fitted
    fig.add_trace(
        go.Scatter(
            x=y_pred,
            y=residuals,
            mode='markers',
            marker=dict(size=6, color='steelblue', opacity=0.6),
            name='Residuals'
        ),
        row=1, col=1
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
    
    # 2. Q-Q Plot
    (quantiles, values), (slope, intercept, r) = probplot(residuals, dist="norm")
    
    fig.add_trace(
        go.Scatter(
            x=quantiles,
            y=values,
            mode='markers',
            marker=dict(size=6, color='steelblue', opacity=0.6),
            name='Sample Quantiles'
        ),
        row=1, col=2
    )
    
    # Línea teórica
    fig.add_trace(
        go.Scatter(
            x=quantiles,
            y=slope * quantiles + intercept,
            mode='lines',
            line=dict(color='red', width=2),
            name='Theoretical Line'
        ),
        row=1, col=2
    )
    
    fig.update_xaxes(
        title_text="Fitted Values",
        title_font=dict(size=18, family='Arial', color='black'),
        tickfont=dict(size=16, family='Arial', color='black'),
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Residuals",
        title_font=dict(size=18, family='Arial', color='black'),
        tickfont=dict(size=16, family='Arial', color='black'),
        row=1, col=1
    )
    fig.update_xaxes(
        title_text="Theoretical Quantiles",
        title_font=dict(size=18, family='Arial', color='black'),
        tickfont=dict(size=16, family='Arial', color='black'),
        row=1, col=2
    )
    fig.update_yaxes(
        title_text="Sample Quantiles",
        title_font=dict(size=18, family='Arial', color='black'),
        tickfont=dict(size=16, family='Arial', color='black'),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text="Model Diagnostics - Residual Analysis",
        height=400,
        showlegend=False,
        template='plotly_white'
    )
    
    # Guardar
    fig.write_image(str(output_path), width=1600, height=400, scale=2)
    print(f"  - {output_path.name}")
    
    return fig


def create_variance_contribution(
    results: pd.DataFrame,
    r_squared: float,
    params_config: Dict,
    output_path: Path
) -> go.Figure:
    """
    Crea gráfico de barras mostrando % de varianza explicada por cada parámetro.
    
    Args:
        results: DataFrame con resultados del análisis
        r_squared: R² del modelo
        params_config: Diccionario con configuración de parámetros
        output_path: Ruta donde guardar el gráfico
        
    Returns:
        Figura de Plotly
    """
    # Calcular contribución a varianza (aproximación: SRC²)
    results_sorted = results.copy()
    results_sorted = results_sorted.sort_values('SRC', key=abs, ascending=True)
    
    # R² parcial aproximado
    src_squared = results_sorted['SRC'] ** 2
    total_src_squared = src_squared.sum()
    variance_contrib = (src_squared / total_src_squared) * r_squared * 100
    
    # Obtener nombres de visualización
    display_names = [params_config[p]['display_name'] for p in results_sorted['Parameter']]
    
    # Crear gráfico
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=display_names,
        x=variance_contrib,
        orientation='h',
        marker=dict(
            color=variance_contrib,
            colorscale='Blues',
            showscale=True,
            colorbar=dict(title="% Variance")
        ),
        text=[f"{v:.1f}%" for v in variance_contrib],
        textposition='outside',
        textfont=dict(size=12)
    ))
    
    fig.update_layout(
        title=f"Contribution to Total Variance (R² = {r_squared:.2%})",
        height=500,
        template='plotly_white'
    )
    fig.update_xaxes(
        title_text="% of Explained Variance",
        title_font=dict(size=18, family='Arial', color='black'),
        tickfont=dict(size=16, family='Arial', color='black')
    )
    fig.update_yaxes(
        title_text="Parameter",
        title_font=dict(size=18, family='Arial', color='black'),
        tickfont=dict(size=16, family='Arial', color='black')
    )
    
    # Guardar
    fig.write_image(str(output_path), width=1000, height=500, scale=2)
    print(f"  - {output_path.name}")
    
    return fig


# ============================================================================
# FUNCIÓN DE RESUMEN EJECUTIVO
# ============================================================================

def print_executive_summary(
    results: pd.DataFrame,
    r_squared: float,
    adj_r_squared: float
) -> None:
    """
    Imprime resumen ejecutivo del análisis.
    
    Args:
        results: DataFrame con resultados ordenados por ranking
        r_squared: R² del modelo
        adj_r_squared: R² ajustado del modelo
    """
    print("\n" + "=" * 70)
    print("EXECUTIVE SUMMARY")
    print("=" * 70)
    
    # Parámetro más influyente
    top_param = results.iloc[0]
    print(f"\n🎯 Most influential parameter: {top_param['Parameter']}")
    print(f"   SRC = {top_param['SRC']:.3f}")
    print(f"   Correlation (r) = {top_param['r (correlation)']:.3f}")
    print(f"   p-value = {top_param['p-value']:.2e}")
    
    # Interpretación del SRC
    print(f"\n📊 Interpretation:")
    print(f"   When {top_param['Parameter']} increases by 1 standard deviation,")
    print(f"   EUI changes by {top_param['SRC']:.2f} standard deviations.")
    
    # Top 3
    print(f"\n🏆 Top 3 parameters by importance:")
    for i, row in results.head(3).iterrows():
        print(f"   {row['Ranking']}. {row['Parameter']}: SRC = {row['SRC']:.3f}")
    
    print("\n" + "=" * 70)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Función principal que ejecuta todo el análisis."""
    print("=" * 70)
    print("SRC SENSITIVITY ANALYSIS - CIBSE TM54 METHOD")
    print("=" * 70)
    
    try:
        # 1. Cargar y validar datos
        print("\n[1/11] Cargando datos...")
        csv_path = find_csv_file()
        df, X, y = load_and_validate_data(csv_path, PARAMS, TARGET)
        
        # 2. Estandarizar variables
        print("\n[2/11] Estandarizando variables...")
        X_std, y_std = standardize_variables(X, y)
        
        # 3. Ajustar regresión multivariada
        print("\n[3/11] Ajustando modelo de regresión multivariada...")
        model = fit_multivariate_regression(X_std, y_std)
        
        r_squared = model.rsquared
        adj_r_squared = model.rsquared_adj
        
        print(f"\n✓ R² del modelo: {r_squared:.4f}")
        print(f"✓ R² ajustado: {adj_r_squared:.4f}")
        print(f"\n{model.summary()}")
        
        # 4. Calcular correlaciones simples
        print("\n[4/11] Calculando correlaciones simples...")
        correlations = calculate_simple_correlations(X, y, PARAMS)
        
        print("\n✓ Correlaciones simples (r):")
        for param, r in correlations.items():
            print(f"  {param}: {r:.4f}")
        
        # 5. Crear tabla de resultados
        print("\n[5/11] Creando tabla de resultados...")
        results = create_results_table(PARAMS, model, correlations)
        
        print("\n" + "=" * 70)
        print("SENSITIVITY ANALYSIS RESULTS (SRC Method)")
        print("=" * 70)
        print(f"\nModel Statistics:")
        print(f"  R² = {r_squared:.4f}")
        print(f"  Adjusted R² = {adj_r_squared:.4f}")
        print(f"\nParameter Rankings:")
        if HAS_TABULATE:
            print(tabulate(
                results,
                headers='keys',
                tablefmt='grid',
                showindex=False,
                floatfmt='.4f'
            ))
        else:
            print(format_table_simple(results))
        
        # 6. Validaciones
        print("\n[6/11] Validando resultados...")
        validate_results(results, model, X)
        
        # 7. Crear directorio de salida con fecha y hora
        output_dir = get_output_directory()
        print(f"\n✓ Directorio de salida: {output_dir.name}")
        
        # 7. Crear directorio de salida con fecha y hora
        output_dir = get_output_directory()
        print(f"\n✓ Directorio de salida: {output_dir.name}")
        
        # 8. Guardar resultados CSV
        print("\n[8/14] Guardando resultados...")
        csv_output = save_results(results, output_dir)
        print(f"\n✓ Resultados guardados en: {csv_output.name}")
        
        # 9. Crear visualizaciones principales
        print("\n[9/14] Creando visualizaciones principales...")
        fig_tornado_h = create_tornado_chart_horizontal(results, TARGET, PARAMS_CONFIG)
        fig_tornado_v = create_tornado_chart_vertical(results, TARGET, PARAMS_CONFIG)
        fig_scatter = create_scatter_plots(X, y, PARAMS, PARAMS_CONFIG, correlations)
        
        # 10. Guardar gráficos PNG principales
        print("\n[10/14] Guardando gráficos PNG principales...")
        tornado_h_file, tornado_v_file, scatter_file = save_plots_png(
            fig_tornado_h, fig_tornado_v, fig_scatter, TARGET, output_dir
        )
        
        print("\n✓ Gráficos PNG principales guardados:")
        print(f"  - {tornado_h_file.name}")
        print(f"  - {tornado_v_file.name}")
        print(f"  - {scatter_file.name}")
        
        # 11. Crear visualizaciones adicionales
        print("\n[11/14] Creando visualizaciones adicionales...")
        metric_clean = TARGET.replace('/', '_').replace('(', '').replace(')', '')
        
        # 1. Matriz de correlación
        corr_path = output_dir / f"SRC_CorrelationMatrix_TM54_{metric_clean}.png"
        create_correlation_matrix(X, y, corr_path)
        
        # 2. Uncertainty histogram
        hist_path = output_dir / f"SRC_UncertaintyHistogram_TM54_{metric_clean}.png"
        create_uncertainty_histogram(y, hist_path)
        
        # 3. Box plots
        box_path = output_dir / f"SRC_BoxPlots_TM54_{metric_clean}.png"
        create_boxplots_by_parameter(X, y, PARAMS, PARAMS_CONFIG, box_path)
        
        # 4. Residuals plot
        resid_path = output_dir / f"SRC_Residuals_TM54_{metric_clean}.png"
        create_residuals_plot(model, X_std, y_std, resid_path)
        
        # 5. Variance contribution
        var_path = output_dir / f"SRC_VarianceContribution_TM54_{metric_clean}.png"
        create_variance_contribution(results, r_squared, PARAMS_CONFIG, var_path)
        
        print("\n✓ Visualizaciones adicionales guardadas:")
        print(f"  Total: 8 gráficos PNG + 1 CSV en {output_dir}")
        print(f"\n📁 Todos los archivos guardados en: {output_dir}")
        
        # Resumen ejecutivo
        print_executive_summary(results, r_squared, adj_r_squared)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Error de validación: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

