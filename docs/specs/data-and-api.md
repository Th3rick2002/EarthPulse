# Datos, fuentes y API

## Revisión del esquema propuesto

El esquema separa bien catálogo, regiones, observaciones, análisis y caché. Para hacerlo implementable:

- Usar claves estables y unicidad para variable/región/fecha/fuente; un `seriesId` por observación duplica identidad sin aportar mucho.
- Guardar en `variables` la definición y unidad canónica, y en una relación de fuentes/productos (o metadatos equivalentes) el proveedor, colección/producto, identificador de variable y unidad nativa. “Giovanni” es una plataforma de acceso/visualización, no identifica por sí sola el producto científico.
- Guardar bbox como cuatro campos validados y especificar CRS/orden. El bbox del Ártico cruza los límites de longitud; las consultas pueden requerir dos ventanas o una representación normalizada.
- El registro temporal debe identificar variable, región, fecha de periodo mensual, producto/fuente y valor. Definir cómo se agrega cada variable (media, suma u otra regla); no usar una agregación común a precipitación, temperatura y NDVI.
- No almacenar “missing” como si fuera un valor. Conservar estado de calidad junto a observaciones reales/interpoladas, e informar cobertura faltante por separado.
- Un análisis debe registrar intervalo, frecuencia, método/versión, número de observaciones, pendiente y unidad de pendiente, p-value, significancia y fecha de cálculo. Debe poder rastrearse a la serie/producto analizado.
- La clave de caché debe incluir fuente/producto, resolución/frecuencia, bbox o región, intervalo y versión de transformación. `ttl: 24h` es una duración; persistir `expiresAt`/`fetchedAt` y purgar o ignorar entradas vencidas.

## Persistencia sugerida

El plan original propone Firestore opcional para caché y despliega backend en Cloud Run. Firestore encaja mejor como persistencia compartida del MVP desplegado porque el disco local de Cloud Run no es persistente y puede haber varias instancias. SQLite sirve para desarrollo/local o una primera prueba de concepto; en producción requiere almacenamiento persistente y estrategia de concurrencia/backups. Mantener una capa de repositorio para que el motor analítico no dependa del almacén.

No hace falta guardar cada observación indefinidamente en una base si la fuente es reproducible y la política/licencia lo desaconseja: la serie puede vivir en caché con procedencia y caducidad. Aclarar esta política por dataset antes de persistir datos externos.

## Entidades recomendadas

- **Variable:** `id`, nombre, definición, categoría, unidad canónica, `minYears`, frecuencia objetivo.
- **Fuente/producto:** `id`, proveedor (Microsoft Planetary Computer o Meteomatics), colección/producto, variable nativa, unidad nativa, resolución, cobertura y método de acceso.
- **Región:** `id`, nombre, descripción, tipo (`predefined`/`custom`), bbox validado y CRS.
- **Observación:** `variableId`, `regionId`, `sourceProductId`, `periodStart`, `periodEnd`, `value`, `unit`, `quality`; clave única según esos identificadores y periodo.
- **Análisis:** `id`, referencias a variable/región/producto, intervalo, frecuencia, método y versión, `nObservations`, slope y unidad, p-value, significant, interpretación y `createdAt`.
- **Caché:** `cacheKey`, proveedor/producto, consulta normalizada, payload o referencia a observaciones, `fetchedAt`, `expiresAt` y versión del procesamiento.

En Firestore estas relaciones son IDs validados por la aplicación, no claves foráneas. En SQL conviene usar claves foráneas e índices por variable/región/fecha y clave de caché.

## Fuentes y catálogo inicial

- **Meteomatics:** considerar temperatura y precipitación; confirmar variables, unidades, frecuencia, disponibilidad histórica, autenticación y límites del plan contratado.
- **Microsoft Planetary Computer:** candidato para NDVI/productos MODIS; registrar Collection/STAC item, banda, escala, resolución y agregación espacial/temporal.
- **Giovanni:** mantener como posible vía de descubrimiento/consulta de productos NASA, no como fuente intercambiable hasta verificar API y términos. La propuesta de CO₂ requiere identificar dataset y endpoint concretos; no asumir que está disponible por el proveedor citado.

No presentar estos candidatos como integraciones terminadas. Habilitar una variable solo después de validar producto, cobertura mínima, licencia, transformaciones y unidad.

## Contrato HTTP

### GET /variables

Lista todas las variables disponibles con metadatos completos.

**Respuesta 200:**
```json
{
  "variables": [
    {
      "id": "ndvi",
      "name": "NDVI (Normalized Difference Vegetation Index)",
      "definition": "Vegetation health index from MODIS surface reflectance. Values range -1 to 1; higher = greener.",
      "category": "vegetation",
      "canonical_unit": "index",
      "min_years": 5,
      "frequency": "monthly",
      "source": {
        "provider": "planetary-computer",
        "product": "modis-13Q1-061",
        "source_id": "250m_16_days_NDVI",
        "native_unit": "index",
        "scale_factor": 0.0001,
        "aggregation": "mean",
        "resolution": "250m / 16-day",
        "access_method": "STAC API / rasterio"
      },
      "supported_region_ids": ["amazon"]
    },
    {
      "id": "air_temperature",
      "name": "Air Temperature (2m)",
      "definition": "Near-surface air temperature from ERA5 reanalysis. Monthly mean of hourly values.",
      "category": "temperature",
      "canonical_unit": "°C",
      "min_years": 5,
      "frequency": "monthly",
      "source": {
        "provider": "meteomatics",
        "product": "ecmwf-era5",
        "source_id": "t_2m:C",
        "native_unit": "°C",
        "scale_factor": null,
        "aggregation": "mean",
        "resolution": "~30km / hourly",
        "access_method": "Meteomatics API"
      },
      "supported_region_ids": ["arctic"]
    },
    {
      "id": "precipitation",
      "name": "Precipitation",
      "definition": "Total monthly precipitation from CHIRPS satellite-gauge blend. Sum of daily 24h accumulations.",
      "category": "precipitation",
      "canonical_unit": "mm",
      "min_years": 5,
      "frequency": "monthly",
      "source": {
        "provider": "meteomatics",
        "product": "chc-chirps3",
        "source_id": "precip_24h:mm",
        "native_unit": "mm",
        "scale_factor": null,
        "aggregation": "sum",
        "resolution": "~5km / daily",
        "access_method": "Meteomatics API"
      },
      "supported_region_ids": ["amazon"]
    }
  ]
}
```

### GET /regions

Lista todas las regiones predefinidas con metadatos completos.

**Respuesta 200:**
```json
{
  "regions": [
    {
      "id": "amazon",
      "name": "Amazon Basin",
      "description": "Amazon rainforest extent for vegetation and precipitation monitoring.",
      "type": "predefined",
      "bbox": [-20.0, 5.0, -80.0, -50.0],
      "crs": "EPSG:4326",
      "supported_variable_ids": ["ndvi", "precipitation"]
    },
    {
      "id": "arctic",
      "name": "Arctic Circle",
      "description": "High-latitude region for air temperature trend monitoring (crosses antimeridian).",
      "type": "predefined",
      "bbox": [66.5, 90.0, -180.0, 180.0],
      "crs": "EPSG:4326",
      "supported_variable_ids": ["air_temperature"]
    }
  ]
}
```

### GET /series

Obtiene serie temporal mensual con análisis de tendencia para una variable/región.

**Parámetros:**
- `variableId` (requerido): ID de variable del catálogo
- `regionId` (requerido): ID de región del catálogo
- `startDate` (requerido): Fecha inicio YYYY-MM-DD
- `endDate` (requerido): Fecha fin YYYY-MM-DD

**Respuesta 200 (con análisis):**
```json
{
  "variable": { ... },
  "region": { ... },
  "source": {
    "provider": "planetary-computer",
    "product": "modis-13Q1-061",
    "sourceId": "250m_16_days_NDVI"
  },
  "unit": "index",
  "frequency": "monthly",
  "coverage": {
    "start": "2018-01-01",
    "end": "2023-12-31",
    "validObservations": 72,
    "expectedObservations": 72,
    "coverageRatio": 1.0,
    "insufficientReason": null
  },
  "observations": [
    { "date": "2018-01-01", "value": 0.6548, "quality": "observed" },
    { "date": "2018-02-01", "value": 0.6182, "quality": "observed" }
  ],
  "analysis": {
    "method": "mann-kendall",
    "slope": -0.000081,
    "slopeUnit": "index/year",
    "pValue": 0.774255,
    "significant": false,
    "nObservations": 72,
    "interpretation": "The monthly index shows a decreasing trend (-0.0010 index/year), which is not statistically significant (Mann-Kendall p = 0.7743). Note: significance does not imply causation.",
    "periodStart": "2018-01-01",
    "periodEnd": "2023-12-31"
  }
}
```

**Respuesta 200 (cobertura insuficiente - sin análisis):**
```json
{
  "variable": { ... },
  "region": { ... },
  "source": { ... },
  "unit": "index",
  "frequency": "monthly",
  "coverage": {
    "start": "2023-01-01",
    "end": "2023-12-31",
    "validObservations": 12,
    "expectedObservations": 12,
    "coverageRatio": 1.0,
    "insufficientReason": "Time span (1.0 years) less than minimum 5 years required for trend analysis"
  },
  "observations": [ ... ],
  "analysis": null
}
```

**Códigos de error:**
- `400`: Parámetros inválidos (fechas, bbox, combinación variable-región no soportada)
- `404`: Variable o región no encontrada en catálogo

## Catálogo MVP implementado

### Variables

| ID | Nombre | Categoría | Unidad | Fuente | Producto | Variable nativa | Agregación | Regiones |
|---|---|---|---|---|---|---|---|---|
| `ndvi` | NDVI | vegetation | index | planetary-computer | modis-13Q1-061 | 250m_16_days_NDVI | mean | amazon |
| `air_temperature` | Air Temperature (2m) | temperature | °C | meteomatics | ecmwf-era5 | t_2m:C | mean | arctic |
| `precipitation` | Precipitation | precipitation | mm | meteomatics | chc-chirps3 | precip_24h:mm | sum | amazon |

### Regiones

| ID | Nombre | Tipo | BBox (lat_min, lat_max, lon_min, lon_max) | CRS | Variables |
|---|---|---|---|---|---|
| `amazon` | Amazon Basin | predefined | (-20.0, 5.0, -80.0, -50.0) | EPSG:4326 | ndvi, precipitation |
| `arctic` | Arctic Circle | predefined | (66.5, 90.0, -180.0, 180.0) | EPSG:4326 | air_temperature |

## Conversión de bbox por proveedor

- **Planetary Computer (STAC)**: `[lon_min, lat_min, lon_max, lat_max]`
- **Meteomatics**: `{lat_min, lat_max, lon_min, lon_max}`

El Ártico usa bbox con rango longitudinal completo (-180, 180) para cruzar el antimeridiano.