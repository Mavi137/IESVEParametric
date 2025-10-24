"""
==================================
Multiple Parametric Sensitivity Orchestrator
==================================

Module description
------------------
Script orquestador que ejecuta análisis de sensibilidad paramétrica de forma secuencial
para múltiples variables. Este script ejecuta parametric_sensitivity.py una vez por cada
variable definida, asegurando que solo una variable esté activa en cada ejecución.

Este enfoque resuelve problemas de estabilidad del modelo cuando se ejecutan múltiples
variables simultáneamente, ya que permite que el modelo se "resetee" correctamente
entre cada análisis de sensibilidad.

Uso:
----
1. Definir las variables a analizar en el diccionario variables_to_test
2. Ejecutar el script
3. El script procesará cada variable secuencialmente
4. Los resultados se guardarán en archivos CSV separados por variable

"""

import os
import iesve
import importlib
import numpy as np
import utils_parametric as utils_parametric
from datetime import datetime
from pathlib import Path
import time

# Reload pu to pick up any edits in the current session
importlib.reload(utils_parametric)

def run_single_sensitivity_analysis(project, variable_name, variable_range, outputs, 
                                  route, loads_on, model_index, project_folder):
    """
    Ejecuta un análisis de sensibilidad para una sola variable.
    
    Args:
        project: Proyecto VE actual
        variable_name: Nombre de la variable a analizar
        variable_range: Lista de valores para la variable
        outputs: Lista de métricas de salida
        route: Ruta de simulación (0=Apache, 1=UK Part L)
        loads_on: Si ejecutar simulaciones de cargas
        model_index: Índice del modelo a editar
        project_folder: Carpeta del proyecto
    
    Returns:
        bool: True si la ejecución fue exitosa, False en caso contrario
    """
    try:
        print(f"    → Creando diccionario de entrada para {variable_name}...")
        
        # Crear diccionario de entrada con SOLO esta variable
        inputs = {variable_name: variable_range}
        
        print(f"    → Generando escenarios para {len(variable_range)} valores...")
        
        # Crear dataframe de escenarios
        scenarios_df = utils_parametric.scenarios(inputs)
        
        print(f"    → Ejecutando simulaciones paramétricas...")
        
        # Ejecutar simulaciones paramétricas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        simulations_output_name = project_folder + f'{variable_name}_{timestamp}.csv'
        
        try:
            print(f"    → Ejecutando simulaciones paramétricas...")
            
            utils_parametric.simulations(project,
                                       model_index,
                                       route,
                                       loads_on,
                                       scenarios_df,
                                       simulations_output_name,
                                       outputs)
            
        except Exception as e:
            print(f"    ✗ ERROR en simulaciones de {variable_name}: {str(e)}")
            print(f"    → Intentando resetear modelo de todas formas...")
            
        finally:
            # SIEMPRE intentar resetear, incluso si falló
            try:
                print(f"    → Reseteando modelo para siguiente análisis...")
                utils_parametric.reset_changes(project, model_index, scenarios_df)
                # Esperar a que el reset se complete
                time.sleep(3)
            except Exception as e:
                print(f"    ✗ ERROR al resetear: {str(e)}")
        
        print(f"    ✓ Análisis completado exitosamente para {variable_name}")
        return True
        
    except Exception as e:
        print(f"    ✗ ERROR en análisis de {variable_name}: {str(e)}")
        return False

def main():
    """
    Función principal que orquesta la ejecución de múltiples análisis de sensibilidad.
    """
    
    print("="*80)
    print("ORQUESTADOR DE ANÁLISIS DE SENSIBILIDAD PARAMÉTRICA")
    print("="*80)
    print()
    
    # Obtener el proyecto actual
    project = iesve.VEProject.get_current_project()
    
    # Configurar Apache Sim para simulaciones rápidas de análisis de sensibilidad
    print("Configurando opciones de simulación para análisis rápido...")
    sim = iesve.ApacheSim()
    sim.set_options(
        time_step=10,           # 10 minutos (balance velocidad/precisión)
        HVAC=False,             # Desactivar HVAC detallado
        Suncast=False,          # Desactivar cálculo de sombras (no necesario para U-values)
        RadianceIES=False,      # Desactivar iluminación natural detallada
    )
    print("✓ Opciones configuradas: timestep=10min, Suncast=OFF, RadianceIES=OFF")
    print()
    
    # Archivar el proyecto antes de ejecutar cambios paramétricos
    print("Archivando proyecto...")
    project_folder = project.path
    time_stamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    path = Path(project_folder, 'Backups', f'{project.name}_{time_stamp}.zip')
    project.archive_project(str(path), False)
    print("✓ Proyecto archivado en carpeta de backups del proyecto")
    print()
    
    ### Definir las métricas de salida (mismas que parametric_sensitivity.py)
    outputs = [
        'Gas_MWh',
        'Elec_MWh',
        'Gas_kWh/m2',
        'Elec_kWh/m2',
        'Boilers_MWh',
        'Chillers_MWh',
        'Boilers_kWh/m2',
        'Chillers_kWh/m2',
        'CE_kgCO2/m2',
        'UK_BER_kgCO2/m2',
        'EUI_kWh/m2',
        'Ta_max_degC',
        'Boiler_max_kW',
        'Chiller_max_kW',
        
        'Interior_lighting_kWh/m2',
        'Exterior_lighting_kWh/m2',
        'Space_heating_(gas)_kWh/m2',
        'Space_heating_(elec)_kWh/m2',
        'Space_cooling_kWh/m2',
        'Pumps_kWh/m2',
        'Fans_interior_kWh/m2',
        'DHW_heating_kWh/m2',
        'Receptacle_equipment_kWh/m2',
        'Elevators_escalators_kWh/m2',
        'Data_center_equipment_kWh/m2',
        'Cooking_(gas)_kWh/m2',
        'Cooking_(elec)_kWh/m2',
        'Refrigeration_kWh/m2',
        'Wind_PV_kWh/m2'
    ]
    
    ### Definir las variables a analizar
    # Descomenta las variables que quieras analizar y ajusta los rangos según necesites
    variables_to_test = {
        # Orientación y setpoints
        # 'building_orientation': [90.0, 135.0, 180.0, 270.0],
        # 'room_heating_setpoint': np.arange(16.0, 22.0, 0.25).tolist(),
        # 'room_cooling_setpoint': np.arange(23.0, 29.0, 0.25).tolist(),
        
        # Sistemas HVAC
        # 'apsys_scop': np.arange(0.70, 0.95, 0.0125).tolist(),
        # 'apsys_sseer': np.arange(2.0, 5.0, 0.15).tolist(),
        # 'sys_free_cooling': np.arange(4.0, 6.0, 0.1).tolist(),
        
        # NCM específicos
        # 'ncm_terminal_sfp': np.arange(0.1, 0.5, 0.02).tolist(),
        # 'ncm_localexhaust_sfp': np.arange(0.1, 0.5, 0.02).tolist(),
        # 'ncm_light_pho_parasit': np.arange(0.01, 0.05, 0.002).tolist(),
        # 'ncm_light_occ_parasit': np.arange(0.01, 0.05, 0.002).tolist(),
        
        # Ventanas y aperturas
        # 'window_openable_area': np.arange(10.0, 30.0, 1.0).tolist(),
        # 'ext_wall_glazing': np.arange(20.0, 40.0, 1.0).tolist(),
        
        # Propiedades térmicas de la envolvente
        'wall_const_u_value': np.arange(0.2, 0.6, 0.1).tolist(),
        'window_const_u_value': np.arange(1.0, 1.8, 0.02).tolist(),
        'roof_const_u_value': np.arange(0.1, 0.3, 0.01).tolist(),
        'floor_const_u_value': np.arange(0.1, 0.3, 0.01).tolist(),
        
        # Propiedades del vidrio
        # 'outer_pane_transmittance': np.arange(0.2, 0.4, 0.01).tolist(),
        # 'outer_pane_reflectance': np.arange(0.6, 0.8, 0.01).tolist(),
        
        # Sombras locales
        # 'local_shade_overhang': [-0.05, -0.05, -0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
        #                          0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        # 'local_shade_depth': [-0.05, -0.05, -0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
        #                       0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05],
        
        # Energía renovable
        # 'pv_area': np.arange(0.0, 100.0, 5.0).tolist(),
        
        # Archivos por referencia (descomenta según necesites)
        # 'weather_file': ['LondonDSY2020H.fwt', 'LondonDSY2050H.fwt', 'LondonDSY2080H.fwt'],
        # 'ap_system': ['SYST0001', 'SYST0002', 'SYST0003'],
        # 'infiltration_rate': ['Infiltration 0.5', 'Infiltration 0.75'],
        # 'gen_lighting_gain': ['General Lighting 5','General Lighting 10'],
        # 'computer_gain': ['Computers 3','Computers 5'],
        # 'wall_construction': ['STD_WAL2','STD_WAL3'],
        # 'window_construction': ['STD_EXT1','STD_EXT2'],
        # 'roof_construction': ['STD_ROO1', 'STD_ROO2'],
        # 'floor_construction': ['STD_FLO2', 'STD_FLO3'],
        # 'asp_file': ['CAV.asp', 'VAV.asp', 'UFAD.asp'],
    }
    
    ### Configuración de simulación (misma que parametric_sensitivity.py)
    route = 0  # 0=Apache, 1=UK Part L
    loads_on = False  # True para simulaciones de cargas, False para UK Compliance
    model_index = 0  # Índice del modelo real
    
    ### Variables para seguimiento del progreso
    total_variables = len(variables_to_test)
    successful_variables = []
    failed_variables = []
    
    print(f"Variables a analizar: {total_variables}")
    print(f"Configuración: Route={route}, Loads_on={loads_on}, Model_index={model_index}")
    print()
    
    ### Bucle principal: ejecutar análisis secuencial para cada variable
    for i, (variable_name, variable_range) in enumerate(variables_to_test.items(), 1):
        
        print("="*60)
        print(f"ANÁLISIS {i}/{total_variables}: {variable_name}")
        print("="*60)
        print(f"Rango de valores: {len(variable_range)} puntos")
        print(f"Valores: {variable_range[:3]}{'...' if len(variable_range) > 3 else ''}")
        print()
        
        # Ejecutar análisis para esta variable
        success = run_single_sensitivity_analysis(
            project=project,
            variable_name=variable_name,
            variable_range=variable_range,
            outputs=outputs,
            route=route,
            loads_on=loads_on,
            model_index=model_index,
            project_folder=project_folder
        )
        
        # Registrar resultado
        if success:
            successful_variables.append(variable_name)
        else:
            failed_variables.append(variable_name)
        
        # Esperar entre variables para que el modelo se resetee correctamente
        if i < total_variables:  # No esperar después del último análisis
            print(f"\nEsperando 15 segundos antes del siguiente análisis...")
            time.sleep(15)
        
        print()
    
    ### Resumen final
    print("="*80)
    print("RESUMEN FINAL")
    print("="*80)
    print(f"Total de variables procesadas: {total_variables}")
    print(f"Análisis exitosos: {len(successful_variables)}")
    print(f"Análisis fallidos: {len(failed_variables)}")
    print()
    
    if successful_variables:
        print("✓ Variables procesadas exitosamente:")
        for var in successful_variables:
            print(f"  - {var}")
        print()
    
    if failed_variables:
        print("✗ Variables que fallaron:")
        for var in failed_variables:
            print(f"  - {var}")
        print()
    
    print("="*80)
    print("ANÁLISIS COMPLETADO")
    print("="*80)

# Ejecutar el script principal
if __name__ == "__main__":
    main()
