"""
Script para generar gráficas de influencia de variables para informe CRREM
Muestra qué variable tiene más impacto en métricas clave de energía y carbono
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path

# Configurar matplotlib
matplotlib.rcParams['font.size'] = 11
plt.rcParams['figure.figsize'] = (14, 10)

def cargar_datos_logs(carpeta_logs):
    """Carga los CSV de análisis paramétrico"""
    
    carpeta_logs_path = Path(carpeta_logs)
    
    archivos_csv = {
        'computer_gain': carpeta_logs_path / 'computer_gain.csv',
        'dhw_lph_per_person': carpeta_logs_path / 'dhw_lph_per_person.csv',
        'gen_lighting_gain': carpeta_logs_path / 'gen_lighting_gain.csv',
        'people_m2_per_person': carpeta_logs_path / 'people_m2_per_person.csv'
    }
    
    datos = {}
    for nombre, archivo in archivos_csv.items():
        if archivo.exists():
            df = pd.read_csv(archivo, index_col='run')
            datos[nombre] = df
        else:
            print(f"[ADVERTENCIA] No se encontro: {archivo}")
    
    return datos

def calcular_rango_variacion(df, variable, metrica, caso_base_val):
    """Calcula el rango de variación de una métrica respecto al caso base"""
    
    valores = df[metrica].values
    caso_base = df.loc[df[variable] == caso_base_val, metrica].values[0] if len(df[df[variable] == caso_base_val]) > 0 else valores[0]
    
    max_val = valores.max()
    min_val = valores.min()
    
    variacion_max = max_val - caso_base
    variacion_min = min_val - caso_base
    
    return {
        'caso_base': caso_base,
        'max': max_val,
        'min': min_val,
        'variacion_max': variacion_max,
        'variacion_min': variacion_min,
        'rango_total': max_val - min_val
    }

def calcular_sensibilidad_simple(df, variable, metrica):
    """Calcula sensibilidad simple basada en variación relativa"""
    
    try:
        # Convertir variable a numérico si es posible
        df_numeric = df[[variable, metrica]].copy()
        df_numeric[variable] = pd.to_numeric(df_numeric[variable], errors='coerce')
        df_numeric = df_numeric.dropna()
        
        if len(df_numeric) < 2:
            return None
        
        # Calcular variación relativa normalizada por rango de la variable
        rango_var = df_numeric[variable].max() - df_numeric[variable].min()
        rango_metrica = df_numeric[metrica].max() - df_numeric[metrica].min()
        
        if rango_var == 0:
            return None
        
        # Sensibilidad = cambio en métrica por unidad de cambio en variable
        sensibilidad = rango_metrica / rango_var if rango_var != 0 else 0
        
        return sensibilidad
    except:
        return None

def generar_tornado_chart(datos, metrica, carpeta_salida, nombre_archivo):
    """Genera gráfica tipo tornado mostrando rango de variación"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    variables_nombres = {
        'computer_gain': 'Equipos informaticos',
        'dhw_lph_per_person': 'ACS (l/h·pers)',
        'gen_lighting_gain': 'Iluminacion',
        'people_m2_per_person': 'Densidad ocupacion (m²/pers)'
    }
    
    resultados = []
    
    # Identificar caso base (EUI = 225.61)
    eui_base = 225.61
    
    for nombre_var, df in datos.items():
        variable_col = None
        for col in df.columns:
            if col in ['computer_gain', 'dhw_lph_per_person', 'gen_lighting_gain', 'people_m2_per_person']:
                variable_col = col
                break
        
        if variable_col is None:
            continue
        
        # Encontrar valor del caso base
        mask_base = np.abs(df['EUI_kWh/m2'] - eui_base) < 0.1
        if mask_base.sum() > 0:
            caso_base_val = df.loc[mask_base.index[mask_base], variable_col].values[0]
        else:
            caso_base_val = df[variable_col].iloc[0]
        
        rango = calcular_rango_variacion(df, variable_col, metrica, caso_base_val)
        
        resultados.append({
            'variable': variables_nombres.get(nombre_var, nombre_var),
            'rango_total': abs(rango['variacion_max']) + abs(rango['variacion_min']),
            'variacion_max': rango['variacion_max'],
            'variacion_min': rango['variacion_min'],
            'caso_base': rango['caso_base']
        })
    
    # Ordenar por rango total
    resultados.sort(key=lambda x: x['rango_total'], reverse=True)
    
    # Crear gráfica
    y_pos = np.arange(len(resultados))
    colors_pos = ['#2ecc71' if r['variacion_max'] > 0 else '#e74c3c' for r in resultados]
    colors_neg = ['#e74c3c' if r['variacion_min'] < 0 else '#2ecc71' for r in resultados]
    
    # Barras de variación máxima (positiva)
    variaciones_max = [max(0, r['variacion_max']) for r in resultados]
    variaciones_min = [min(0, r['variacion_min']) for r in resultados]
    
    ax.barh(y_pos, variaciones_max, left=[r['caso_base'] for r in resultados], 
            color=colors_pos, alpha=0.7, label='Aumento')
    ax.barh(y_pos, variaciones_min, left=[r['caso_base'] + r['variacion_max'] for r in resultados],
            color=colors_neg, alpha=0.7, label='Reduccion')
    
    # Línea de caso base
    for i, r in enumerate(resultados):
        ax.axvline(r['caso_base'], color='black', linestyle='--', linewidth=1, alpha=0.5)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([r['variable'] for r in resultados])
    ax.set_xlabel(f'{metrica}', fontsize=12, fontweight='bold')
    ax.set_title(f'Analisis de Sensibilidad: {metrica}\n(Caso base: EUI = 225.61 kWh/m²)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='x')
    ax.legend(loc='upper right')
    
    # Añadir valores en las barras
    for i, r in enumerate(resultados):
        if r['variacion_max'] > 0:
            ax.text(r['caso_base'] + r['variacion_max']/2, i, 
                   f"+{r['variacion_max']:.1f}", 
                   ha='center', va='center', fontweight='bold', fontsize=9)
        if r['variacion_min'] < 0:
            ax.text(r['caso_base'] + r['variacion_max'] + r['variacion_min']/2, i,
                   f"{r['variacion_min']:.1f}",
                   ha='center', va='center', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(carpeta_salida / nombre_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Grafica guardada: {nombre_archivo}")

def generar_influence_chart(datos, metrica, carpeta_salida, nombre_archivo):
    """Genera gráfica de coeficientes beta (influencia)"""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    variables_nombres = {
        'computer_gain': 'Equipos informaticos',
        'dhw_lph_per_person': 'ACS',
        'gen_lighting_gain': 'Iluminacion',
        'people_m2_per_person': 'Densidad ocupacion'
    }
    
    resultados = []
    
    for nombre_var, df in datos.items():
        variable_col = None
        for col in df.columns:
            if col in ['computer_gain', 'dhw_lph_per_person', 'gen_lighting_gain', 'people_m2_per_person']:
                variable_col = col
                break
        
        if variable_col is None:
            continue
        
        # Calcular variación relativa respecto al caso base
        eui_base = 225.61
        mask_base = np.abs(df['EUI_kWh/m2'] - eui_base) < 0.1
        if mask_base.sum() > 0:
            caso_base_val = df.loc[mask_base.index[mask_base], metrica].values[0]
        else:
            caso_base_val = df[metrica].iloc[0]
        
        valores = df[metrica].values
        variacion_rel = ((valores.max() - valores.min()) / abs(caso_base_val)) * 100 if caso_base_val != 0 else 0
        
        # Para variables numéricas, también calcular sensibilidad simple
        sensibilidad = None
        if variable_col in ['dhw_lph_per_person', 'people_m2_per_person']:
            sensibilidad = calcular_sensibilidad_simple(df, variable_col, metrica)
        
        resultados.append({
            'variable': variables_nombres.get(nombre_var, nombre_var),
            'beta': variacion_rel,
            'sensibilidad': sensibilidad if sensibilidad is not None else variacion_rel
        })
    
    # Ordenar por valor absoluto
    resultados.sort(key=lambda x: abs(x['sensibilidad']), reverse=True)
    
    # Crear gráfica de barras
    variables = [r['variable'] for r in resultados]
    betas = [r['sensibilidad'] for r in resultados]
    colors = ['#3498db' if b > 0 else '#e74c3c' for b in betas]
    
    bars = ax.barh(variables, betas, color=colors, alpha=0.7)
    
    # Añadir valores
    for i, (bar, beta) in enumerate(zip(bars, betas)):
        ax.text(beta, i, f' {beta:.2f}', 
               va='center', fontweight='bold', fontsize=10)
    
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    ax.set_xlabel('Indice de Influencia (Variacion Relativa %)', fontsize=12, fontweight='bold')
    ax.set_title(f'Influencia de Variables: {metrica}\n(Valores mayores = mayor impacto)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(carpeta_salida / nombre_archivo, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Grafica guardada: {nombre_archivo}")

def generar_comparacion_rangos(datos, carpeta_salida):
    """Genera gráfica comparativa de rangos de variación para múltiples métricas"""
    
    metricas_crrem = {
        'EUI_kWh/m2': 'EUI (kWh/m²)',
        'CE_kgCO2/m2': 'Emisiones CO₂ (kgCO₂/m²)',
        'Elec_kWh/m2': 'Electricidad (kWh/m²)'
    }
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    variables_nombres = {
        'computer_gain': 'Equipos',
        'dhw_lph_per_person': 'ACS',
        'gen_lighting_gain': 'Iluminacion',
        'people_m2_per_person': 'Ocupacion'
    }
    
    eui_base = 225.61
    
    for ax_idx, (metrica, titulo) in enumerate(metricas_crrem.items()):
        ax = axes[ax_idx]
        
        rangos = []
        nombres_vars = []
        
        for nombre_var, df in datos.items():
            variable_col = None
            for col in df.columns:
                if col in ['computer_gain', 'dhw_lph_per_person', 'gen_lighting_gain', 'people_m2_per_person']:
                    variable_col = col
                    break
            
            if variable_col is None or metrica not in df.columns:
                continue
            
            # Encontrar caso base
            mask_base = np.abs(df['EUI_kWh/m2'] - eui_base) < 0.1
            if mask_base.sum() > 0:
                caso_base_val = df.loc[mask_base.index[mask_base], variable_col].values[0]
            else:
                caso_base_val = df[variable_col].iloc[0]
            
            valores = df[metrica].values
            caso_base_metrica = df.loc[df[variable_col] == caso_base_val, metrica].values[0] if len(df[df[variable_col] == caso_base_val]) > 0 else valores[0]
            
            rango_total = valores.max() - valores.min()
            variacion_rel = (rango_total / abs(caso_base_metrica)) * 100 if caso_base_metrica != 0 else 0
            
            rangos.append(variacion_rel)
            nombres_vars.append(variables_nombres.get(nombre_var, nombre_var))
        
        # Ordenar
        sorted_data = sorted(zip(rangos, nombres_vars), reverse=True)
        rangos, nombres_vars = zip(*sorted_data)
        
        colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(rangos)))
        bars = ax.bar(nombres_vars, rangos, color=colors, alpha=0.7)
        
        # Valores en barras
        for bar, rango in zip(bars, rangos):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                   f'{rango:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        ax.set_ylabel('% Variacion Relativa', fontsize=11, fontweight='bold')
        ax.set_title(titulo, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='x', rotation=45)
    
    plt.suptitle('Comparacion de Influencia de Variables\n(Rango de variacion relativa respecto al caso base)', 
                fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(carpeta_salida / 'Comparacion_Influencia_Variables.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  [OK] Grafica guardada: Comparacion_Influencia_Variables.png")

def main():
    """Función principal"""
    
    print("="*70)
    print("GENERACION DE GRAFICAS DE INFLUENCIA PARA INFORME CRREM")
    print("="*70)
    
    # Rutas
    carpeta_logs = Path(__file__).parent / "Logs"
    carpeta_salida = carpeta_logs / "analisis"
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    # Cargar datos
    print("\n1. Cargando datos...")
    datos = cargar_datos_logs(carpeta_logs)
    
    if len(datos) == 0:
        print("[ERROR] No se encontraron datos")
        return
    
    print(f"   [OK] {len(datos)} archivo(s) cargado(s)")
    
    # Métricas clave para CRREM
    metricas_crrem = {
        'CE_kgCO2/m2': 'Emisiones_CO2',
        'EUI_kWh/m2': 'EUI',
        'Elec_kWh/m2': 'Electricidad'
    }
    
    # Generar gráficas tornado para cada métrica
    print("\n2. Generando graficas de sensibilidad (Tornado)...")
    for metrica, nombre_corto in metricas_crrem.items():
        nombre_archivo = f'Tornado_{nombre_corto}.png'
        generar_tornado_chart(datos, metrica, carpeta_salida, nombre_archivo)
    
    # Generar gráficas de influencia (beta coefficients)
    print("\n3. Generando graficas de influencia (Beta)...")
    for metrica, nombre_corto in metricas_crrem.items():
        nombre_archivo = f'Influencia_{nombre_corto}.png'
        generar_influence_chart(datos, metrica, carpeta_salida, nombre_archivo)
    
    # Generar comparación de rangos
    print("\n4. Generando grafica comparativa...")
    generar_comparacion_rangos(datos, carpeta_salida)
    
    print("\n" + "="*70)
    print("[OK] GRAFICAS GENERADAS")
    print("="*70)
    print(f"\nArchivos generados en: {carpeta_salida}")
    print("\nGraficas CRREM:")
    print("  - Tornado_Emisiones_CO2.png: Rango de variacion de emisiones")
    print("  - Tornado_EUI.png: Rango de variacion de EUI")
    print("  - Tornado_Electricidad.png: Rango de variacion de electricidad")
    print("  - Influencia_*.png: Coeficientes beta de influencia")
    print("  - Comparacion_Influencia_Variables.png: Comparacion general")

if __name__ == "__main__":
    main()

