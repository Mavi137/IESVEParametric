"""
Script para analizar los logs paramétricos de la carpeta Logs
Identifica el caso base por EUI común (225.61) y genera resumen en Excel y gráficas
Analiza: computer_gain, dhw_lph_per_person, gen_lighting_gain, people_m2_per_person
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
import os

# Configurar matplotlib para español
matplotlib.rcParams['font.size'] = 10
plt.rcParams['figure.figsize'] = (12, 8)

def cargar_logs(carpeta_logs):
    """Carga todos los CSV de la carpeta Logs"""
    
    carpeta_logs_path = Path(carpeta_logs)
    
    if not carpeta_logs_path.exists():
        print(f"Error: No se encuentra la carpeta {carpeta_logs_path}")
        return {}
    
    # Archivos específicos a analizar
    archivos_objetivo = [
        'computer_gain.csv',
        'dhw_lph_per_person.csv',
        'gen_lighting_gain.csv',
        'people_m2_per_person.csv'
    ]
    
    archivos_csv = [carpeta_logs_path / archivo for archivo in archivos_objetivo 
                    if (carpeta_logs_path / archivo).exists()]
    
    if len(archivos_csv) == 0:
        print(f"No se encontraron archivos CSV objetivo en {carpeta_logs_path}")
        return {}
    
    datos = {}
    
    for archivo in archivos_csv:
        nombre_var = archivo.stem.replace("_", "")
        print(f"Cargando: {archivo.name}")
        
        try:
            df = pd.read_csv(archivo, index_col='run')
            datos[nombre_var] = {
                'archivo': archivo.name,
                'dataframe': df,
                'variable': df.columns[0]  # Primera columna después de 'run'
            }
        except Exception as e:
            print(f"  Error al cargar {archivo.name}: {e}")
    
    return datos

def identificar_caso_base(datos):
    """Identifica el caso base por el EUI común entre todos los CSV"""
    
    # Primero, encontrar el EUI común
    eui_comun = None
    eui_values = []
    
    print("  Buscando EUI comun entre todos los archivos...")
    for nombre_var, info in datos.items():
        df = info['dataframe']
        if 'EUI_kWh/m2' in df.columns:
            euis = df['EUI_kWh/m2'].dropna().unique()
            eui_values.append(set(euis))
            print(f"    {nombre_var}: EUIs encontrados = {sorted(euis)}")
    
    # Encontrar la intersección (EUI común)
    if len(eui_values) > 0:
        eui_comun_set = eui_values[0]
        for eui_set in eui_values[1:]:
            eui_comun_set = eui_comun_set.intersection(eui_set)
        
        if len(eui_comun_set) > 0:
            eui_comun = sorted(eui_comun_set)[0]  # Tomar el primero si hay múltiples
            print(f"  [OK] EUI comun encontrado: {eui_comun} kWh/m2")
            # Verificar que es el esperado (225.61)
            if abs(eui_comun - 225.61) < 0.01:
                print(f"  [OK] Confirma caso base esperado (EUI = 225.61)")
        else:
            print("  [ADVERTENCIA] No se encontro EUI comun. Usando run 0 como caso base.")
            eui_comun = None
    else:
        print("  [ERROR] No se encontraron valores de EUI")
        return {}
    
    # Ahora identificar el caso base en cada CSV por el EUI común
    casos_base = {}
    
    for nombre_var, info in datos.items():
        df = info['dataframe']
        
        if eui_comun is not None and 'EUI_kWh/m2' in df.columns:
            # Buscar el run que tiene el EUI común
            mask = df['EUI_kWh/m2'] == eui_comun
            runs_con_eui_comun = df.index[mask].tolist()
            
            if len(runs_con_eui_comun) > 0:
                # Tomar el primer run que tenga el EUI común
                run_caso_base = runs_con_eui_comun[0]
                caso_base = df.loc[run_caso_base].to_dict()
                
                casos_base[nombre_var] = {
                    'variable': info['variable'],
                    'valor_variable': caso_base[info['variable']],
                    'resultados': caso_base,
                    'dataframe': df,
                    'run': run_caso_base,
                    'EUI': eui_comun
                }
                print(f"    {nombre_var}: Caso base = run {run_caso_base} ({info['variable']} = {caso_base[info['variable']]})")
            else:
                print(f"  [ADVERTENCIA] No se encontro run con EUI {eui_comun} en {info['archivo']}")
                # Fallback: usar run 0 si existe
                if 0 in df.index:
                    caso_base = df.loc[0].to_dict()
                    casos_base[nombre_var] = {
                        'variable': info['variable'],
                        'valor_variable': caso_base[info['variable']],
                        'resultados': caso_base,
                        'dataframe': df,
                        'run': 0,
                        'EUI': caso_base.get('EUI_kWh/m2', None)
                    }
        else:
            # Fallback: usar run 0 si no hay EUI común
            if 0 in df.index:
                caso_base = df.loc[0].to_dict()
                casos_base[nombre_var] = {
                    'variable': info['variable'],
                    'valor_variable': caso_base[info['variable']],
                    'resultados': caso_base,
                    'dataframe': df,
                    'run': 0,
                    'EUI': caso_base.get('EUI_kWh/m2', None)
                }
    
    return casos_base

def generar_resumen_excel(casos_base, carpeta_salida):
    """Genera un archivo Excel con resumen de resultados"""
    
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    archivo_excel = carpeta_salida / "Resumen_Caso_Base.xlsx"
    
    with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
        
        # Hoja 1: Resumen del caso base
        resumen_data = []
        for nombre_var, info in casos_base.items():
            variable = info['variable']
            valor = info['valor_variable']
            
            resultados = info['resultados']
            
            # Filtrar solo métricas importantes
            metricas_importantes = [
                'Gas_MWh', 'Elec_MWh', 'Gas_kWh/m2', 'Elec_kWh/m2',
                'EUI_kWh/m2', 'CE_kgCO2/m2', 'UK_BER_kgCO2/m2',
                'Ta_max_degC', 'Boiler_max_kW', 'Chiller_max_kW',
                'DHW_heating_kWh/m2', 'Space_heating_(gas)_kWh/m2',
                'Space_heating_(elec)_kWh/m2', 'Space_cooling_kWh/m2'
            ]
            
            fila = {
                'Análisis': nombre_var,
                'Variable': variable,
                'Run_Caso_Base': info.get('run', 'N/A'),
                'Valor_Caso_Base': valor,
                'EUI_kWh/m2_Caso_Base': info.get('EUI', 'N/A')
            }
            
            for metrica in metricas_importantes:
                if metrica in resultados:
                    fila[metrica] = resultados[metrica]
            
            resumen_data.append(fila)
        
        df_resumen = pd.DataFrame(resumen_data)
        df_resumen.to_excel(writer, sheet_name='Caso_Base', index=False)
        
        # Hoja 2: Comparación con variaciones (si existen)
        for nombre_var, info in casos_base.items():
            df = info['dataframe']
            
            if len(df) > 1:  # Si hay más de un run
                # Crear comparación con caso base
                caso_base_val = info['valor_variable']
                
                comparacion_data = []
                for idx in df.index:
                    fila = df.loc[idx].to_dict()
                    valor_actual = fila[info['variable']]
                    
                    # Determinar si la variable es numérica
                    def es_valor_numerico(valor):
                        if isinstance(valor, (int, float)):
                            return True
                        if isinstance(valor, str):
                            try:
                                float(valor)
                                return True
                            except ValueError:
                                return False
                        return False
                    
                    es_numerica = es_valor_numerico(caso_base_val)
                    
                    variacion = {
                        'Run': idx,
                        'Variable': info['variable'],
                        'Valor': valor_actual,
                    }
                    
                    # Solo calcular diferencia si es numérica
                    if es_numerica:
                        try:
                            valor_actual_num = float(valor_actual) if isinstance(valor_actual, str) else valor_actual
                            caso_base_val_num = float(caso_base_val) if isinstance(caso_base_val, str) else caso_base_val
                            variacion['Dif_VS_Caso_Base'] = valor_actual_num - caso_base_val_num
                            variacion['%_Cambio'] = ((valor_actual_num - caso_base_val_num) / caso_base_val_num * 100) if caso_base_val_num != 0 else 0
                        except (ValueError, TypeError):
                            variacion['Dif_VS_Caso_Base'] = 'N/A'
                            variacion['%_Cambio'] = 'N/A'
                    else:
                        variacion['Dif_VS_Caso_Base'] = 'N/A'
                        variacion['%_Cambio'] = 'N/A'
                    
                    # Añadir métricas principales
                    for metrica in ['EUI_kWh/m2', 'Elec_kWh/m2', 'Gas_kWh/m2', 
                                   'CE_kgCO2/m2', 'DHW_heating_kWh/m2']:
                        if metrica in fila:
                            variacion[f'{metrica}_Caso_Base'] = info['resultados'][metrica]
                            variacion[f'{metrica}_Run_{idx}'] = fila[metrica]
                            variacion[f'{metrica}_Cambio'] = fila[metrica] - info['resultados'][metrica]
                            variacion[f'{metrica}_%_Cambio'] = ((fila[metrica] - info['resultados'][metrica]) / 
                                                               abs(info['resultados'][metrica]) * 100) if info['resultados'][metrica] != 0 else 0
                    
                    comparacion_data.append(variacion)
                
                df_comp = pd.DataFrame(comparacion_data)
                nombre_hoja = f'{nombre_var[:30]}'  # Limitar longitud del nombre
                df_comp.to_excel(writer, sheet_name=nombre_hoja, index=False)
        
        # Hoja 3: Todos los datos completos
        for nombre_var, info in casos_base.items():
            df = info['dataframe']
            nombre_hoja = f'Datos_{nombre_var[:25]}'  # Limitar longitud
            df.to_excel(writer, sheet_name=nombre_hoja)
    
    print(f"\n[OK] Excel generado: {archivo_excel}")
    return archivo_excel

def generar_graficas(casos_base, carpeta_salida):
    """Genera gráficas de los resultados"""
    
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    
    metricas_principales = {
        'EUI_kWh/m2': 'EUI (kWh/m2)',
        'Elec_kWh/m2': 'Electricidad (kWh/m2)',
        'Gas_kWh/m2': 'Gas (kWh/m2)',
        'CE_kgCO2/m2': 'Emisiones CO2 (kgCO2/m2)',
        'DHW_heating_kWh/m2': 'ACS (kWh/m2)',
        'Ta_max_degC': 'Temp. Max. Aire (C)'
    }
    
    for nombre_var, info in casos_base.items():
        df = info['dataframe']
        variable = info['variable']
        
        if len(df) == 0:
            continue
        
        # Gráfica 1: Comparación de métricas principales para diferentes valores
        if len(df) > 1:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            axes = axes.flatten()
            
            metrica_idx = 0
            for metrica, titulo in list(metricas_principales.items())[:4]:
                if metrica in df.columns:
                    ax = axes[metrica_idx]
                    
                    # Ordenar por valor de variable
                    df_sorted = df.sort_values(variable)
                    
                    ax.plot(df_sorted[variable], df_sorted[metrica], 
                           marker='o', linewidth=2, markersize=8)
                    
                    # Marcar caso base
                    caso_base_val = info['valor_variable']
                    caso_base_res = info['resultados'].get(metrica, 0)
                    ax.plot(caso_base_val, caso_base_res, 
                           marker='s', markersize=12, color='red', 
                           label='Caso Base', zorder=5)
                    
                    ax.set_xlabel(variable, fontsize=11, fontweight='bold')
                    ax.set_ylabel(titulo, fontsize=11, fontweight='bold')
                    ax.set_title(titulo, fontsize=12, fontweight='bold')
                    ax.grid(True, alpha=0.3)
                    ax.legend()
                    
                    metrica_idx += 1
            
            # Ocultar ejes no usados
            for idx in range(metrica_idx, 4):
                axes[idx].axis('off')
            
            plt.suptitle(f'Análisis de Sensibilidad: {variable}', 
                        fontsize=14, fontweight='bold', y=0.995)
            plt.tight_layout()
            
            nombre_archivo = carpeta_salida / f"Grafica_{nombre_var}_sensibilidad.png"
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  [OK] Grafica guardada: {nombre_archivo.name}")
        
        # Gráfica 2: Comparación de métricas del caso base
        metricas_caso_base = []
        valores_caso_base = []
        
        for metrica, titulo in metricas_principales.items():
            if metrica in info['resultados']:
                valor = info['resultados'][metrica]
                if not np.isnan(valor) and valor != 0:
                    metricas_caso_base.append(titulo)
                    valores_caso_base.append(valor)
        
        if len(metricas_caso_base) > 0:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Normalizar valores para mejor visualización
            valores_norm = np.array(valores_caso_base)
            valores_norm = valores_norm / np.max(np.abs(valores_norm))
            
            bars = ax.barh(metricas_caso_base, valores_caso_base, 
                          color='steelblue', alpha=0.7)
            
            # Añadir valores en las barras
            for i, (bar, valor) in enumerate(zip(bars, valores_caso_base)):
                ax.text(valor, i, f' {valor:.2f}', 
                       va='center', fontweight='bold', fontsize=10)
            
            ax.set_xlabel('Valor', fontsize=12, fontweight='bold')
            ax.set_title(f'Caso Base - {variable} = {info["valor_variable"]}', 
                         fontsize=13, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            plt.tight_layout()
            
            nombre_archivo = carpeta_salida / f"Grafica_{nombre_var}_caso_base.png"
            plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"  [OK] Grafica guardada: {nombre_archivo.name}")

def main():
    """Función principal"""
    
    print("="*70)
    print("ANALISIS DE LOGS PARAMETRICOS - CASO BASE")
    print("="*70)
    
    # Ruta a la carpeta de logs
    carpeta_logs = Path(__file__).parent / "Logs"
    carpeta_salida = carpeta_logs / "analisis"
    
    # Cargar datos
    print("\n1. Cargando archivos CSV...")
    datos = cargar_logs(carpeta_logs)
    
    if len(datos) == 0:
        print("\n[ERROR] No se encontraron datos para analizar")
        return
    
    print(f"   [OK] {len(datos)} archivo(s) cargado(s)")
    
    # Identificar caso base
    print("\n2. Identificando caso base...")
    casos_base = identificar_caso_base(datos)
    
    if len(casos_base) == 0:
        print("\n[ERROR] No se encontro caso base")
        return
    
    print(f"   [OK] {len(casos_base)} caso(s) base identificado(s)")
    
    # Mostrar resumen del caso base
    print("\n3. RESUMEN DEL CASO BASE:")
    print("-"*70)
    
    # Mostrar EUI común primero
    if len(casos_base) > 0:
        eui_comun = list(casos_base.values())[0].get('EUI', None)
        if eui_comun is not None:
            print(f"\nEUI comun identificado: {eui_comun} kWh/m2")
            print("="*70)
    
    for nombre_var, info in casos_base.items():
        print(f"\n{nombre_var}:")
        print(f"  Variable: {info['variable']}")
        print(f"  Run caso base: {info.get('run', 'N/A')}")
        print(f"  Valor caso base: {info['valor_variable']}")
        print(f"  EUI: {info['resultados'].get('EUI_kWh/m2', 'N/A')} kWh/m2")
        print(f"  Electricidad: {info['resultados'].get('Elec_kWh/m2', 'N/A')} kWh/m2")
        print(f"  Gas: {info['resultados'].get('Gas_kWh/m2', 'N/A')} kWh/m2")
        print(f"  Emisiones CO2: {info['resultados'].get('CE_kgCO2/m2', 'N/A')} kgCO2/m2")
        print(f"  ACS: {info['resultados'].get('DHW_heating_kWh/m2', 'N/A')} kWh/m2")
        print(f"  Temp. max.: {info['resultados'].get('Ta_max_degC', 'N/A')} C")
        print(f"  Numero de runs: {len(info['dataframe'])}")
    
    # Generar Excel
    print("\n4. Generando archivo Excel...")
    archivo_excel = generar_resumen_excel(casos_base, carpeta_salida)
    
    # Generar gráficas
    print("\n5. Generando gráficas...")
    generar_graficas(casos_base, carpeta_salida)
    
    print("\n" + "="*70)
    print("[OK] ANALISIS COMPLETADO")
    print("="*70)
    print(f"\nArchivos generados en: {carpeta_salida}")
    print(f"  - Excel: {archivo_excel.name}")
    print(f"  - Gráficas: *.png")

if __name__ == "__main__":
    main()

