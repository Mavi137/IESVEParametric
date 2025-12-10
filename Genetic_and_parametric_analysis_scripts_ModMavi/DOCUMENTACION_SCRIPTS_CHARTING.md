# Documentación - Scripts de Charting

## 📁 Estructura de Carpetas

### Carpeta `Resultados/`
**Ubicación**: `Genetic_and_parametric_analysis_scripts_ModMavi/Resultados/`

**Contenido**:
- **Archivos de entrada (CSV)**:
  - `Para_sim_table.csv` - Tabla completa con todas las simulaciones (81 filas)
  - `dhw_lph_per_person.csv` - Análisis individual de DHW
  - `people_m2_per_person.csv` - Análisis individual de Ocupación
  - `gen_lighting_gain.csv` - Análisis individual de Iluminación
  - `computer_gain.csv` - Análisis individual de Equipamiento

- **Carpetas de salida** (se crean automáticamente con fecha y hora):
  - `SRC_Analysis_YYYY-MM-DD_HH-MM-SS/` - Resultados de análisis SRC
  - `Uncertainty_EndUse_YYYY-MM-DD_HH-MM-SS/` - Gráficos de incertidumbre por uso final
  - `Uncertainty_Histogram_YYYY-MM-DD_HH-MM-SS/` - Histogramas de incertidumbre
  - `Sensibilidad_TM54_YYYY-MM-DD_HH-MM-SS/` - Gráficos de sensibilidad TM54

### Carpeta `Logs/`
**⚠️ OBSOLETA - Ya no se usa**

La carpeta `Logs/` y su subcarpeta `analisis/` **ya no se utilizan**. Todos los scripts han sido actualizados para guardar resultados en `Resultados/` con subcarpetas con fecha y hora.

**Puedes borrar la carpeta `Logs/` si lo deseas** - no afectará el funcionamiento de los scripts.

---

## 📊 Scripts de Charting - Resumen

### Scripts que leen `Para_sim_table.csv`

| Script | Archivo CSV | Output |
|--------|-------------|--------|
| `chart_SRC_sensitivity.py` | `Para_sim_table.csv` | 8 PNG + 1 CSV en `SRC_Analysis_YYYY-MM-DD_HH-MM-SS/` |
| `chart_uncertainty_enduse.py` | `Para_sim_table.csv` | 1 PNG en `Uncertainty_EndUse_YYYY-MM-DD_HH-MM-SS/` |
| `chart_uncertainty_histogram.py` | `Para_sim_table.csv` | Múltiples PNG en `Uncertainty_Histogram_YYYY-MM-DD_HH-MM-SS/` |

### Scripts que leen CSV individuales

| Script | Archivos CSV | Output |
|--------|--------------|--------|
| `chart_sensitivity_tm54.py` | `dhw_lph_per_person.csv`<br>`people_m2_per_person.csv`<br>`gen_lighting_gain.csv`<br>`computer_gain.csv` | 2 PNG en `Sensibilidad_TM54_YYYY-MM-DD_HH-MM-SS/` |

---

## 🎯 Scripts para Informe TM54

**Para el informe TM54 se están usando las imágenes generadas por:**

### 1. `chart_SRC_sensitivity.py` ⭐
**Análisis de sensibilidad con metodología CIBSE TM54**

**Archivo de entrada**: `Resultados/Para_sim_table.csv`

**Archivos generados** (en `Resultados/SRC_Analysis_YYYY-MM-DD_HH-MM-SS/`):
- `sensitivity_SRC_results.csv` - Tabla con resultados (SRC, correlaciones, p-values)
- `SRC_Tornado_TM54_Horizontal_EUI_kWh_m2.png` - Gráfico tornado horizontal
- `SRC_Tornado_TM54_Vertical_EUI_kWh_m2.png` - Gráfico tornado vertical ⭐ **Usado en informe**
- `SRC_Scatter_TM54_EUI_kWh_m2.png` - Scatter plots con líneas de regresión
- `SRC_CorrelationMatrix_TM54_EUI_kWh_m2.png` - Matriz de correlación
- `SRC_UncertaintyHistogram_TM54_EUI_kWh_m2.png` - Histograma de distribución EUI
- `SRC_BoxPlots_TM54_EUI_kWh_m2.png` - Box plots por nivel de parámetro
- `SRC_Residuals_TM54_EUI_kWh_m2.png` - Análisis de residuos del modelo
- `SRC_VarianceContribution_TM54_EUI_kWh_m2.png` - Contribución % a varianza

**Características**:
- Regresión multivariada con variables estandarizadas
- Calcula SRC (Standardized Regression Coefficients)
- Validaciones (multicolinealidad, R², significancia)
- 8 visualizaciones diferentes

### 2. `chart_uncertainty_enduse.py` ⭐
**Análisis de incertidumbre por uso final - Estilo TM54 Figura 8**

**Archivo de entrada**: `Resultados/Para_sim_table.csv`

**Archivo generado** (en `Resultados/Uncertainty_EndUse_YYYY-MM-DD_HH-MM-SS/`):
- `Incertidumbre_UsoFinal_TM54.png` ⭐ **Usado en informe**

**Características**:
- Box plots por categoría de uso final
- Muestra distribución de consumo energético
- Colores personalizados por categoría

---

## 📝 Detalles de cada script

### `chart_SRC_sensitivity.py`
- **Método**: Regresión multivariada con variables estandarizadas (z-score)
- **Parámetros analizados**: 
  - `dhw_lph_per_person` (DHW)
  - `people_m2_per_person` (Occupancy)
  - `gen_lighting_gain` (Lighting)
  - `computer_gain` (Equipment)
- **Variable objetivo**: `EUI_kWh/m2`
- **Nota especial**: En el gráfico vertical, el SRC de "Occupancy" se muestra positivo (invertido)

### `chart_uncertainty_enduse.py`
- **Categorías analizadas**:
  - Lighting (Interior + Exterior)
  - Space heating (Gas + Electric)
  - Space cooling
  - DHW heating
  - Receptacle equipment
  - Fans/Pumps
  - Total (EUI)
- **Muestra**: Distribución de consumo por categoría en todas las simulaciones

### `chart_sensitivity_tm54.py`
- **Método**: Regresión bivariada (una variable a la vez)
- **Lee**: 4 CSV individuales (uno por parámetro)
- **Genera**: Gráficos de sensibilidad horizontal y vertical
- **Nota**: Usa el mismo esquema de colores que `chart_SRC_sensitivity.py`

### `chart_uncertainty_histogram.py`
- **Método**: Histogramas de distribución
- **Métricas analizadas**: EUI, Electricidad, Gas, Emisiones CO₂
- **Muestra**: Distribución de valores con estadísticas (media, mediana, P10, P90)

---

## 🔄 Flujo de Trabajo Recomendado

1. **Generar datos**: Ejecutar análisis paramétrico → genera `Para_sim_table.csv` en `Resultados/`

2. **Análisis principal (para informe TM54)**:
   ```bash
   python chart_SRC_sensitivity.py
   python chart_uncertainty_enduse.py
   ```

3. **Análisis adicionales (opcionales)**:
   ```bash
   python chart_sensitivity_tm54.py  # Requiere CSV individuales
   python chart_uncertainty_histogram.py
   ```

4. **Resultados**: Todos se guardan en `Resultados/` con subcarpetas con fecha y hora

---

## 📌 Notas Importantes

- **Todos los scripts leen de `Resultados/`**
- **Todos los scripts guardan en `Resultados/`** (subcarpetas con fecha y hora)
- **La carpeta `Logs/` ya no se usa** - puede borrarse
- **Para el informe TM54**: usar imágenes de `chart_SRC_sensitivity.py` y `chart_uncertainty_enduse.py`
- **Formato CSV**: Separador punto y coma (`;`), decimal punto (`.`)

---

## 🎨 Esquema de Colores

Los scripts usan un esquema de colores consistente:

- **DHW** (`dhw_lph_per_person`): `#CCCCFF` (Morado)
- **Occupancy** (`people_m2_per_person`): `#fea1ff` (Rosa)
- **Lighting** (`gen_lighting_gain`): `#A699A9` (Gris)
- **Equipment** (`computer_gain`): `#CCECFF` (Azulito)

---

**Última actualización**: Enero 2025

