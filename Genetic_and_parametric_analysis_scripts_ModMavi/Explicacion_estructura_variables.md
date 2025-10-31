# Explicación: Cómo funciona la estructura de variables paramétricas

## Resumen ejecutivo

Las variables como `people_m2_per_person` **NO las inventamos de la nada**. Son **nombres que elegimos nosotros** para mapear a los **campos reales que expone la API de IES-VE** (como `occupancy_density`). El flujo es:

1. **Descubrimos** qué campos tiene IES-VE usando `show_templates.py`
2. **Creamos funciones** en `utils_model_mod.py` que modifican esos campos
3. **Conectamos** esas funciones a nombres de inputs en `apply_model_modifications()`
4. **Usamos** esos nombres en `parametric_sensitivity.py`

---

## 1. Descubrimiento: ¿Qué campos tiene IES-VE?

### Paso 1: Inspección con `show_templates.py`

Cuando ejecutamos `show_templates.py`, vimos en la salida algo como esto:

```
Template: Bedroom
  Internal gains: 3
{'number_of_people': 2.0,
 'type_str': 'People',
 'units_str': 'people',        # ← Esto indica unidades "people"
 'units_val': 1,               # ← 1 = people, 0 = m²/person
 ...
}

Template: OfficeEnclosed
  Internal gains: 4
{'occupancy_density': 10.0,    # ← Este campo aparece cuando units_val = 0
 'type_str': 'People',
 'units_str': 'm²/person',     # ← Esto indica unidades de densidad
 'units_val': 0,               # ← 0 = m²/person
 ...
}
```

**Descubrimos que:**
- Cuando `units_val = 1`: el gain People usa `number_of_people` (número absoluto)
- Cuando `units_val = 0`: el gain People usa `occupancy_density` (m² por persona)

### Paso 2: Descubrimiento de campos de ACS (DHW)

También vimos:

```
Template: Bedroom
	DHW: 10.0000 l/h Occupancy
```

Y al inspeccionar `template.get_room_conditions()`, encontramos que hay un campo `'dhw'` que puede ser ajustado.

---

## 2. Creación de funciones en `utils_model_mod.py`

### ¿Por qué creamos funciones?

El sistema de parametric simulation ya tenía un patrón establecido:
- Cada tipo de modificación tiene su propia función (ej: `set_heating_setpoint()`, `revise_ap_systems()`)
- Todas siguen el mismo patrón: reciben `project` (o `model`) y un `value`

### Función para ocupación en unidades "people"

```python
def set_people_number(project, value):
    """Ajusta number_of_people en gains tipo People con units_val=1"""
    for template in get_thermal_templates(project):
        gains = template.get_casual_gains()
        for gain in gains:
            info = gain.get()
            if info['type_val'] == iesve.PeopleGain_type.people:
                if info.get('units_val') == 1:  # Solo si está en "people"
                    gain.set({'number_of_people': float(value)})
        template.apply_changes()
```

**Nota importante:** Esta función **usa los nombres de campo que expone la API** (`number_of_people`, `units_val`). Nosotros no inventamos esos nombres, los descubrimos.

### Función para ocupación en unidades "m²/person"

```python
def set_people_density_m2_per_person(project, value):
    """Ajusta occupancy_density en gains tipo People con units_val=0"""
    for template in get_thermal_templates(project):
        gains = template.get_casual_gains()
        for gain in gains:
            info = gain.get()
            if info['type_val'] == iesve.PeopleGain_type.people:
                if info.get('units_val') == 0:  # Solo si está en "m²/person"
                    gain.set({'occupancy_density': float(value)})  # ← Campo real de la API
        template.apply_changes()
```

**Nombres que elegimos nosotros:**
- `set_people_density_m2_per_person` ← Nombre de la función (nuestra elección)
- `occupancy_density` ← Campo real de la API (no lo inventamos)

### Función para ACS

```python
def set_dhw_flow_per_person(project, value):
    """Ajusta el caudal DHW"""
    for template in get_thermal_templates(project):
        room_conditions = template.get_room_conditions()
        # Probamos varias claves porque la API puede variar por versión
        candidate_keys = ['dhw', 'dhw_lph_per_person', ...]
        for key in candidate_keys:
            if key in room_conditions:
                template.set_room_conditions({key: float(value)})
                template.apply_changes()
                break
```

---

## 3. Conexión: Mapeo de nombres de input → funciones

### Función central: `apply_model_modifications()`

Esta función es el **"director de orquesta"**. Recibe:
- `mod_categories`: lista de nombres de inputs (ej: `['people_m2_per_person', 'dhw_lph_per_person']`)
- `row`: fila del DataFrame con los valores

```python
def apply_model_modifications(project, model, mod_categories, row):
    # ... muchas otras condiciones ...
    
    # 👇 AQUÍ es donde conectamos nuestro nombre de input con la función
    if 'people_number' in mod_categories:
        set_people_number(project, row.people_number)  # ← Llamada a la función
        
    if 'people_m2_per_person' in mod_categories:
        set_people_density_m2_per_person(project, row.people_m2_per_person)  # ← Llamada
        
    if 'dhw_lph_per_person' in mod_categories:
        set_dhw_flow_per_person(project, row.dhw_lph_per_person)  # ← Llamada
```

**Flujo:**
1. Si `'people_m2_per_person'` está en `mod_categories` → ejecuta `set_people_density_m2_per_person()`
2. La función modifica el campo `occupancy_density` en los templates
3. El template se guarda con `template.apply_changes()`

---

## 4. Uso en `parametric_sensitivity.py`

### Definición de inputs

```python
inputs = {}
inputs['people_m2_per_person'] = [10.0, 20.0]  # ← Nuestro nombre elegido
inputs['dhw_lph_per_person'] = [774.0, 387.0]
```

### Generación de escenarios

```python
# utils_parametric.scenarios() crea un DataFrame con todas las combinaciones
scenarios_df = utils_parametric.scenarios(inputs)
# Resultado:
#   run  people_m2_per_person  dhw_lph_per_person
#   0    10.0                  774.0
#   1    20.0                  774.0
#   2    10.0                  387.0
#   3    20.0                  387.0
```

### Aplicación de modificaciones

```python
for row in scenarios_df.itertuples():
    # 👇 Esta función lee row.people_m2_per_person y ejecuta la función correspondiente
    utils_model_mod.apply_model_modifications(project, model, scenarios_df.columns, row)
```

---

## Resumen: ¿Qué inventamos y qué no?

### ❌ NO inventamos (vienen de la API de IES-VE):
- `occupancy_density` (campo real del gain People)
- `number_of_people` (campo real del gain People)
- `dhw` (campo real de room_conditions)
- `units_val`, `type_val` (enums de la API)

### ✅ SÍ elegimos nosotros (nombres para facilitar uso):
- `people_m2_per_person` ← nombre descriptivo para el input
- `set_people_density_m2_per_person()` ← nombre de la función
- `dhw_lph_per_person` ← nombre descriptivo para el input

---

## Flujo completo

```
parametric_sensitivity.py
    ↓ inputs = {'people_m2_per_person': [10.0, 20.0]}
    ↓
utils_parametric.scenarios()
    ↓ DataFrame con columnas: ['people_m2_per_person']
    ↓
utils_parametric.simulations()
    ↓ Para cada fila del DataFrame:
    ↓
utils_model_mod.apply_model_modifications()
    ↓ Detecta 'people_m2_per_person' en mod_categories
    ↓
set_people_density_m2_per_person(project, row.people_m2_per_person)
    ↓ Busca templates activos
    ↓ Busca gains tipo People con units_val=0
    ↓
gain.set({'occupancy_density': 20.0})  ← Campo real de la API
    ↓
template.apply_changes()
    ↓
IES-VE actualiza el modelo
    ↓
Simulación térmica con nuevos valores
```

---

## ¿Por qué esta estructura?

1. **Separación de responsabilidades:**
   - `parametric_sensitivity.py`: Define QUÉ variar
   - `utils_parametric.py`: Genera escenarios y ejecuta simulaciones
   - `utils_model_mod.py`: Define CÓMO modificar el modelo

2. **Extensibilidad:**
   - Añadir una nueva variable = añadir función + conexión en `apply_model_modifications()`

3. **Reutilización:**
   - Las funciones pueden usarse en otros scripts (uncertainty, etc.)

---

## Para añadir una nueva variable en el futuro

1. **Inspeccionar:** Usar `show_templates.py` o explorar la API para ver qué campos existen
2. **Crear función:** En `utils_model_mod.py`, crear función que modifique ese campo
3. **Conectar:** En `apply_model_modifications()`, añadir condición:
   ```python
   if 'mi_nueva_variable' in mod_categories:
       mi_nueva_funcion(project, row.mi_nueva_variable)
   ```
4. **Usar:** En `parametric_sensitivity.py`, añadir a `inputs`:
   ```python
   inputs['mi_nueva_variable'] = [valor1, valor2, ...]
   ```

