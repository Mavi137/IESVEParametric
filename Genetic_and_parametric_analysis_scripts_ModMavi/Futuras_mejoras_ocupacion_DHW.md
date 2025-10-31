## Ideas futuras: ocupación y ACS por template

### Objetivo
- **Permitir distintas ocupaciones por template** y parametrizar ACS (DHW) de forma independiente, manteniendo la integración con las simulaciones de sensibilidad.

### Enfoques para ocupación por template
- **Por nombre/patrón de template**
  - Filtrar `project.thermal_templates(True)` por `template.name` (p. ej. "Bedroom", "OfficeEnclosed").
  - Aplicar setters específicos:
    - `set_people_number(project, value)` para gains en unidades "people".
    - `set_people_density_m2_per_person(project, value)` para gains en unidades "m²/person".
- **Por tipo/estándar**
  - Usar `template.standard` para segmentar (genérico, NCM, PRM) si fuera útil.

### Propuesta de inputs específicos
- Añadir claves de input mapeadas por subconjunto de templates:
  - `people_m2_bedroom`
  - `people_m2_office`
  - `people_number_bedroom`
  - …
- En `apply_model_modifications`, aplicar cada clave solo a los templates objetivo.

### Consideraciones técnicas
- Los gains People pueden estar en dos modalidades:
  - Unidades "people" con `number_of_people`.
  - Unidades "m²/person" con `occupancy_density`.
- Evitar cambiar el tipo de unidades del gain (no siempre lo permite la API). Preferir settear el campo que corresponda a su modalidad.
- Mantener `asp_file` en inputs cuando se modifiquen templates para forzar que el ASP recoja los cambios.

### ACS (DHW)
- Clave actual: `dhw_lph_per_person` (l/(h·pers)).
- En templates, `room_conditions` puede exponer `dhw` y `dhw_units`; si hay perfil "Occupancy", el valor se interpreta per cápita.
- Para usos con DHW nulo, validar que exista sistema DHW activo en el ASP o no habrá consumo aunque aumente el caudal.

### Rangos recomendados (sensibilidad)
- DHW l/(h·pers):
  - Oficinas: 0.5–3 (típico 1–2)
  - Residencial: 3–15 (típico 6–10)
  - Docencia: 1–6 (típico 2–4)
  - Gimnasios/vestuarios: 10–40 (típico 15–25)
- Ocupación m²/person:
  - Oficinas open-plan: 7–15 (típico 8–12)
  - Despachos: 10–20 (típico 12–15)
  - Residencial: 10–30 (típico 12–20)
  - Aulas: 1.5–2.5 (típico 2)

### Estrategia de muestreo
- 5–7 puntos por variable cubriendo percentiles (p5–p95).
- Para 2 variables: rejilla 5×5 (25 sims) o Latin Hypercube.
- Evitar valores irreales (DHW=0 salvo escenarios control).

### Posible extensión
- Inputs por template: `people_m2_<slug_del_template>` y `dhw_lph_per_person_<slug_del_template>`; mapear dinámicamente leyendo templates y emparejando claves por prefijo.


