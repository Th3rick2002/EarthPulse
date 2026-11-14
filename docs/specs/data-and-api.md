# Datos, fuentes y API

## Modelo compartido

El contrato conserva las cinco entidades del esquema acordado: `variables`, `regions`, `time_series`, `trend_analysis` y `cache`. El backend puede mapearlas a documentos Firestore o tablas SQL, pero la API siempre usa los campos de esta especificación.

| Entidad | Campos del contrato | Regla |
|---|---|---|
| Variable | `variableId`, `name`, `description`, `unit`, `source`, `category`, `minYears` | IDs estables; `source` identifica proveedor y producto configurado. |
| Región | `regionId`, `name`, `bbox`, `description`, `type` | `bbox` es objeto `{latMin, latMax, lonMin, lonMax}`; `type` es `predefined` o `custom`. La capa del proveedor convierte el orden según su API. |
| Punto mensual | `seriesId`, `variableId`, `regionId`, `date`, `value`, `quality` | `date` es el primer día del mes UTC; `quality` es `ok`, `missing` o `interpolated`. Missing tiene `value: null`, nunca cero. `seriesId` se mantiene igual en todos los puntos de una misma serie. |
| Tendencia | `analysisId`, `variableId`, `regionId`, `startDate`, `endDate`, `slope`, `pValue`, `significant`, `interpretation`, `createdAt` | `startDate`/`endDate` son inclusivos; `slope` usa unidad de `variables.unit` por año. La fila solo existe cuando hay datos suficientes. |
| Cache | `cacheKey`, `variableId`, `regionId`, `startDate`, `endDate`, `data`, `fetchedAt`, `ttl` | La clave es `variableId_regionId_startDate_endDate`; TTL es 24 horas. Es interna del backend, no se expone al frontend. |

En JSON, los nombres de propiedades usan camelCase (`timeSeries`, `trendAnalysis`, `latMin`); los nombres de las entidades persistidas conservan `time_series`/`trend_analysis`. Es un mapeo de presentación, no cambia el significado ni los campos del esquema. `quality=missing` permite que la gráfica deje un hueco; el análisis excluye puntos missing. No se crean interpolaciones silenciosas.

## Persistencia sugerida

El plan original propone Firestore opcional para caché y despliega backend en Cloud Run. Firestore encaja mejor como persistencia compartida del MVP desplegado porque el disco local de Cloud Run no es persistente y puede haber varias instancias. SQLite sirve para desarrollo/local o una primera prueba de concepto; en producción requiere almacenamiento persistente y estrategia de concurrencia/backups. Mantener una capa de repositorio para que el motor analítico no dependa del almacén.

No hace falta guardar cada observación indefinidamente en una base si la fuente es reproducible y la política/licencia lo desaconseja: la serie puede vivir en caché con procedencia y caducidad. Aclarar esta política por dataset antes de persistir datos externos.

En Firestore las referencias por ID se validan en el backend; en SQL se implementan como claves foráneas. En ambos casos los nombres y campos externos se mantienen iguales.

## Catálogo MVP propuesto

| Variable | Fuente y parámetro | Unidad/resolución de salida | Tratamiento |
|---|---|---|---|
| `ndvi` | Planetary Computer STAC `modis-13Q1-061`, asset `250m_16_days_NDVI` | NDVI adimensional; compuesto de 16 días, 250 m, desde 2000 | Aplicar factor `0.0001`, filtrar píxeles por QA, calcular promedio espacial ponderado por área y resumir por mes. |
| `air_temperature` | Meteomatics `ecmwf-era5`, parámetro `t_2m:C` | °C, dato horario | Consultar puntos/cuadrícula de la bbox y calcular promedio espacial y media mensual. Fijar fuente `ecmwf-era5` en todo el intervalo. |
| `precipitation` | Meteomatics `chc-chirps3`, parámetro `precip_24h:mm` | mm/día como entrada, mm/mes como salida | Sumar los valores diarios por mes y calcular el promedio espacial ponderado. Confirmar disponibilidad en el plan contratado. |
| `land_surface_temperature` (después del núcleo) | Planetary Computer STAC `modis-11A2-061`, assets `LST_Day_1km` o `LST_Night_1km` | °C de superficie; compuesto de 8 días, 1 km, desde 2000 | Elegir día o noche, aplicar escala `0.02` K y conversión a °C, filtrar QA/ausencia de observación y resumir por mes. No etiquetar como temperatura del aire. |

Regiones del caso inicial: Amazonía para NDVI/precipitación y Ártico para temperatura del aire. No todas las variables aplican a todas las regiones: NDVI/LST representan píxeles terrestres y la cobertura de nubes, nieve/agua y estacionalidad polar reduce observaciones válidas.

La API STAC de Planetary Computer sirve para buscar colección/items por fecha y bbox; los assets Azure se firman con SAS de corta duración. Meteomatics requiere autenticación y el acceso/historial depende del plan. No usar `mix` para una serie histórica si los años pueden proceder de productos distintos. Giovanni queda fuera de la integración del MVP; CO₂ también hasta identificar producto, acceso y cobertura concretos.

Estos son los valores configurados para el catálogo MVP; el adaptador devuelve el `source` configurado para la variable y nunca sustituye de proveedor silenciosamente.

## Contrato HTTP frontend/backend v1

Este contrato usa las cinco entidades anteriores. FastAPI genera `/openapi.json` y Swagger `/docs`; frontend genera tipos desde OpenAPI. El frontend nunca llama directamente a Microsoft, Meteomatics ni a Firestore.

### Rutas

- `GET /api/v1/variables` → `{ "data": [Variable] }`.
- `GET /api/v1/regions` → `{ "data": [Region] }`.
- `POST /api/v1/regions` → recibe `{name, bbox, description}`, asigna `type: "custom"` en backend y devuelve `{ "data": Region }` con HTTP 201.
- `GET /api/v1/series?variableId=ndvi&regionId=amazon&startDate=2020-01-01&endDate=2024-12-31` → puntos mensuales y tendencia en una sola respuesta.
- `GET /api/v1/health` → estado del servicio.

`startDate` y `endDate` son fechas ISO inclusivas y deben cubrir meses completos: inicio día 1, fin último día del mes. `TimeSeries.date` es el primer día del mes UTC. El backend obtiene variable/región/fuente desde catálogo; no recibe bbox ni secretos del frontend.

Para `POST /regions`, validar latitud entre -90 y 90, longitud entre -180 y 180 y `latMin < latMax`; bbox se recibe como objeto camelCase y se persiste según los campos del esquema. El cliente no puede asignar `regionId` ni `type`.

### Nombres y DTOs

`Variable` contiene exactamente `variableId`, `name`, `description`, `unit`, `source`, `category`, `minYears`.

`Region` contiene `regionId`, `name`, `bbox: {latMin, latMax, lonMin, lonMax}`, `description`, `type`. El JSON usa camelCase para bbox; al persistir se mapea a los nombres `lat_min`, `lat_max`, `lon_min`, `lon_max` del esquema.

`TimeSeries` contiene exactamente `seriesId`, `variableId`, `regionId`, `date`, `value`, `quality`; calidad usa `ok`, `missing` o `interpolated`. `value` puede ser null solo con calidad missing.

`TrendAnalysis` contiene exactamente `analysisId`, `variableId`, `regionId`, `startDate`, `endDate`, `slope`, `pValue`, `significant`, `interpretation`, `createdAt`. `startDate`/`endDate` inclusivos, slope en la unidad de la variable por año y `significant = pValue < 0.05`. Si no hay cinco años/datos suficientes, `trendAnalysis` es null y frontend muestra estado insuficiente; no se crea fila falsa.

La respuesta de series combina entidades para evitar llamadas separadas y mantener el mismo filtro:

```json
{
  "data": {
    "variable": { "variableId": "ndvi", "name": "NDVI", "description": "Índice de vegetación", "unit": "index", "source": "Microsoft Planetary Computer: modis-13Q1-061", "category": "vegetación", "minYears": 5 },
    "region": { "regionId": "amazon", "name": "Amazonía", "bbox": { "latMin": -20, "latMax": 5, "lonMin": -80, "lonMax": -45 }, "description": "Región amazónica", "type": "predefined" },
    "timeSeries": [
      { "seriesId": "ndvi_amazon", "variableId": "ndvi", "regionId": "amazon", "date": "2020-01-01", "value": 0.72, "quality": "ok" }
    ],
    "trendAnalysis": {
      "analysisId": "...", "variableId": "ndvi", "regionId": "amazon",
      "startDate": "2020-01-01", "endDate": "2024-12-31", "slope": 0.012,
      "pValue": 0.01, "significant": true,
      "interpretation": "El NDVI presenta una tendencia creciente significativa.", "createdAt": "2025-01-01T00:00:00Z"
    }
  }
}
```

`cache` es interno: usa `cacheKey = variableId_regionId_startDate_endDate`, guarda `data`, `fetchedAt`, `ttl=24h`; no tiene ruta pública ni altera la respuesta del frontend.

### Errores y tipos

No 2xx usa `{ "error": { "code": "INVALID_DATE_RANGE", "message": "...", "details": {}, "requestId": "..." } }`. Códigos HTTP: 400 rango inválido, 422 parámetros mal formados, 404 catálogo inexistente, 502 proveedor, 503 integración no disponible, 504 timeout. No devolver stack traces ni secretos.

Dev 1 crea schemas Pydantic/OpenAPI a partir de estos DTOs. Dev 2 genera `frontend/src/types/api.generated.ts` con `openapi-typescript` y usa un único `api.ts` para rutas, query params y el error común. No mantiene tipos duplicados a mano. Los nombres de campos persistidos mapean 1:1 a este contrato; cambios incompatibles requieren una nueva versión.
