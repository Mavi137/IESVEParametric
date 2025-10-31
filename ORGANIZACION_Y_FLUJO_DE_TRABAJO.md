# Organización del repositorio y flujo de trabajo

## Estructura de directorios

```
IESVE_Scripts/
├── Software_Scripts/              # Scripts de referencia (desarrolladores IESVE)
│   ├── api_examples/              # Ejemplos de uso de la API
│   ├── Battery_Storage/           # Scripts de ejemplo sobre baterías
│   ├── HVAC/                      # Ejemplos de HVAC
│   ├── Manufacturing/             # Scripts de manufactura
│   └── ...                        # Otros módulos de ejemplo
│
└── [Scripts propios]              # Scripts desarrollados/modificados por nosotros
    └── Genetic_and_parametric_analysis_scripts_ModMavi/
        ├── Explicacion_estructura_variables.md
        ├── Futuras_mejoras_ocupacion_DHW.md
        └── ...
```

## Propósito de cada sección

### `Software_Scripts/` - Documentación de referencia

**Objetivo**: Este directorio contiene scripts creados por los desarrolladores de IES-VE que sirven como **documentación y referencia** de la API.

**Qué contiene:**
- Ejemplos de uso de la API (`api_examples/`)
- Scripts funcionales que demuestran funcionalidades específicas
- Referencias de cómo interactuar con diferentes módulos de IES-VE

**Cómo usarlo:**
- **Como referencia de la API**: Cuando necesites saber cómo hacer algo con la API, explora estos scripts
- **Como plantilla**: Puedes basarte en ellos para entender patrones y estructuras
- **Para descubrir funcionalidades**: Te ayudan a entender qué es posible hacer con la API

**Importante**: Estos scripts son **solo referencia**. No los modificamos directamente, pero podemos copiar patrones o ejemplos de ellos.

### Scripts propios - Desarrollo y modificaciones

**Objetivo**: Directorios en la raíz de `IESVE_Scripts` contienen nuestros propios scripts, desarrollados o modificados según nuestras necesidades.

**Estructura actual:**
- `Genetic_and_parametric_analysis_scripts_ModMavi/`: Scripts para análisis paramétrico y genético
  - Incluye documentación interna sobre cómo funciona la estructura
  - Scripts de generación de gráficos
  - Utilidades para modificaciones de modelo

**Principios:**
- Cada proyecto/módulo propio tiene su propio directorio
- Incluir documentación (`*.md`) explicando la lógica y estructura
- Mantener código comentado y bien estructurado

## Flujo de trabajo recomendado

### 1. Descubrir funcionalidades de la API

Cuando necesites hacer algo nuevo con la API de IES-VE:

1. **Buscar en `Software_Scripts/api_examples/`**:
   - Explora subdirectorios relevantes (ej: `veroomdata/`, `vethermaltemplate/`, etc.)
   - Lee los ejemplos para entender cómo se hace

2. **Buscar en otros directorios de `Software_Scripts`**:
   - Los scripts funcionales también muestran patrones de uso
   - Pueden tener ejemplos más complejos que los de `api_examples/`

3. **Documentar lo que descubres**:
   - Si encuentras algo útil, documenta cómo funciona
   - Actualiza la documentación en tu proyecto propio

### 2. Desarrollar nuevos scripts

1. **Crear un nuevo directorio** en la raíz de `IESVE_Scripts`:
   ```
   IESVE_Scripts/
   └── mi_nuevo_proyecto/
       ├── script_principal.py
       ├── utils.py
       └── README.md (opcional, para documentar)
   ```

2. **Basarse en ejemplos de `Software_Scripts`**:
   - Copia patrones que funcionen
   - Adapta el código a tus necesidades

3. **Seguir la estructura establecida**:
   - Usar utilidades separadas cuando sea apropiado
   - Documentar funciones complejas
   - Mantener código modular

### 3. Modificar scripts existentes

Para los scripts que ya tenemos:

1. **Mantener compatibilidad**:
   - Evitar cambios que rompan funcionalidad existente
   - Documentar cambios importantes

2. **Actualizar documentación**:
   - Si cambias la estructura, actualiza los `.md` correspondientes
   - Explica el "por qué" de los cambios

3. **Versionar cambios importantes**:
   - Usar git para trackear modificaciones
   - Hacer commits descriptivos

## Documentación del proyecto

### Documentos existentes

- `Genetic_and_parametric_analysis_scripts_ModMavi/Explicacion_estructura_variables.md`:
  - Explica cómo funciona el mapeo de variables paramétricas
  - Documenta el flujo desde inputs hasta modificación del modelo
  - Guía para añadir nuevas variables

- `Genetic_and_parametric_analysis_scripts_ModMavi/Futuras_mejoras_ocupacion_DHW.md`:
  - Ideas y mejoras futuras para implementar
  - Consideraciones técnicas
  - Rangos recomendados

### Crear nueva documentación

Cuando crees nuevos scripts o módulos:

1. **README.md o similar** en el directorio del proyecto:
   - Descripción del propósito
   - Cómo usar los scripts
   - Dependencias y requisitos

2. **Documentación técnica** (si aplica):
   - Explicación de la estructura
   - Flujos de datos
   - Extensiones futuras

3. **Logs y notas**:
   - Documentar decisiones importantes
   - Problemas encontrados y soluciones
   - Referencias a scripts de `Software_Scripts` que hayas usado

## Convenciones de nombres

- **Scripts propios**: Nombres descriptivos en español o inglés según contexto
- **Directorios**: Nombre descriptivo del proyecto o funcionalidad
- **Documentación**: `.md` con nombres claros que indiquen el contenido

## Resumen

- **`Software_Scripts/`** = Biblioteca de referencia (no modificar)
- **Scripts propios** = Nuestro código de desarrollo (en la raíz)
- **Documentación** = Mantener `.md` actualizados con explicaciones y guías
- **Flujo** = Referenciar ejemplos → Desarrollar → Documentar

---

*Este documento puede actualizarse según evolucione la estructura del proyecto.*

