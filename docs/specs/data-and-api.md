# Datos, fuentes y API

## Modelo compartido

El esquema lógico usa cinco entidades: `variables`, `regions`, `time_series`, `trend_analysis` y `cache`. La persistencia puede mapearlas a tablas SQL o documentos; los campos HTTP descritos aquí son el contrato compartido.

| Entidad | Campos principales | Regla |
|---|---|---|
| Variable | `variableId`, `name`, `description`, `unit`, `source`, `category`, `minYears` | IDs estables; `source` identifica proveedor y producto. |
| Región | `regionId`, `name`, `bbox`, `description`, `type` | `bbox` WGS84; `type` es `predefined` o `custom`. |
| Punto mensual | `seriesId`, `variableId`, `regionId`, `date`, `value`, `quality` | Fecha el primer día del mes; `missing` implica `value: null`. |
| Tendencia | `analysisId`, `variableId`, `regionId`, `startDate`, `endDate`, `slope`, `pValue`, `significant`, `interpretation`, `createdAt` | Fechas inclusivas; pendiente en unidad de variable por año. |
| Cache | `cacheKey`, `variableId`, `area`, `startDate`, `endDate`, `data`, `fetchedAt`, `ttl` | Interna del backend; respuesta exacta en SQLite, TTL de 24 horas. |

Las relaciones de variable y región se validan en backend y se representan como claves foráneas en SQL o referencias por ID en Firestore. La caché no se expone al frontend. No se crean interpolaciones silenciosas.

## Contrato HTTP canónico FE/BE

Los modelos Pydantic en `backend/app/schemas/contract.py` y OpenAPI (`/openapi.json`) son la referencia de implementación. Swagger UI está disponible en `/docs`.

- Prefijo: `/api/v1`.
- JSON usa camelCase.
- Respuestas exitosas: `{ "data": ... }`, excepto `/api/v1/health`, que devuelve directamente `HealthResponse`.
- Errores: `{ "error": { "code", "message", "details", "requestId" } }`; el mismo ID se devuelve en `X-Request-ID`.
- Fechas: ISO 8601. `startDate` y `endDate` son inclusivas y cubren meses completos: inicio día 1, fin último día. Periodo de 1 a 50 años.
- El frontend consulta exclusivamente el backend; no llama a Planetary Computer, Meteomatics ni a Firestore.

### DTOs

`Variable`: `variableId`, `name`, `description`, `unit`, `source`, `category`, `minYears`.

`Region`: `regionId`, `name`, `bbox: {latMin, latMax, lonMin, lonMax}`, `description`, `type`.

`TimeSeries`: `seriesId`, `variableId`, `regionId`, `date`, `value`, `quality`. `quality` es `ok`, `missing` o `interpolated`; `value` es null exactamente cuando la calidad es `missing`. Cada fecha es el primer día del mes.

`TrendAnalysis`: `analysisId`, `variableId`, `regionId`, `startDate`, `endDate`, `slope`, `pValue`, `significant`, `interpretation`, `createdAt`. `pValue` está entre 0 y 1; `significant` equivale a `pValue < 0.05`.

### Rutas

| Método y ruta | Respuesta exitosa |
|---|---|
| `GET /api/v1/variables` | `{data: Variable[]}` |
| `GET /api/v1/availability?variableId=precipitation` | Cobertura actual CHIRPS, `{data: {variableId, availableStartDate, availableEndDate}}`. |
| `GET /api/v1/regions` | `{data: Region[]}` |
| `GET /api/v1/series?variableId=…&regionId=…&startDate=…&endDate=…` | `{data: {variable, region, timeSeries[], trendAnalysis}}` |
| `GET /api/v1/series` para Planetary Computer | `202 {data: {jobId, status: "processing"}}`; consultar `GET /api/v1/series/jobs/{jobId}` hasta recibir `200` con la misma respuesta de series |
| `POST /api/v1/series/compare` | Una a cuatro áreas rectangulares independientes; `202` con `jobId` o `200` si todas están en caché. El polling devuelve `{data: {results: [{areaId, name, series}]}}`. |
| `GET /api/v1/health` | `HealthResponse` directa, sin wrapper `data` |

`POST /api/v1/series/compare` recibe `variableId`, `startDate`, `endDate` y `areas: [{areaId, name, bbox}]`. Cada bbox debe ser un rectángulo WGS84 de hasta 35° de ancho por 25° de alto; se procesan como máximo cuatro por tanda y cada zona obtiene su propia serie y tendencia. Las áreas son temporales a la consulta; no se guardan como regiones del catálogo.

La disponibilidad de lluvia se consulta con `GET /api/v1/availability?variableId=precipitation`; el backend cachea el resultado seis horas. Las rutas de series vuelven a validar las fechas contra la cobertura antes de consultar Meteomatics. CHIRPS entrega acumulaciones diarias con fecha en el límite derecho, así que el último día seleccionable se calcula restando un día al `max_date` del proveedor. El frontend limita el selector al último mes completo disponible.

### Códigos de error

| HTTP | `error.code` | Uso |
|---|---|---|
| 400 | `INVALID_PARAMS` | Rango que no cubre meses completos o combinación variable-región no admitida. |
| 404 | `NOT_FOUND` | Variable o región inexistente. |
| 422 | `VALIDATION_ERROR` | Parámetros de request con formato inválido. |
| 500 | `INTERNAL_ERROR` | Error interno, sin stack trace ni secretos. |
| 502 | `PROVIDER_ERROR` | El proveedor falla o devuelve datos no admitidos. |
| 503 | `PROVIDER_UNAVAILABLE` | Integración no implementada o credenciales requeridas ausentes. |
| 504 | `PROVIDER_TIMEOUT` | Timeout del proveedor. |

### Análisis y cobertura

- Método: Mann-Kendall y pendiente de Sen (Theil-Sen).
- La pendiente usa el tiempo calendario real entre observaciones y se expresa en unidad de variable por año.
- Para generar tendencia se requiere al menos `minYears` años completos (1 año en el MVP), tres observaciones válidas como mínimo y calidad `ok` en al menos el 50% de los meses solicitados.
- Los puntos `missing` e `interpolated` no cuentan como observaciones del análisis; los meses faltantes no comprimen el intervalo temporal.
- Si la cobertura no alcanza el mínimo, `trendAnalysis` es `null`. Ninguna consulta puede abarcar más de 50 años.
- La significancia es `pValue < 0.05`; significancia no implica causalidad.

## Catálogo MVP

| variableId | Fuente y producto | Unidad de salida | Región |
|---|---|---|---|
| `ndvi` | Planetary Computer STAC `modis-13Q1-061`, asset `250m_16_days_NDVI` | NDVI adimensional | Amazonía |
| `air_temperature` | Meteomatics ERA5 `t_mean_2m_24h:C` | °C | Ártico |
| `precipitation` | Meteomatics CHIRPS `precip_24h:mm` | mm | Amazonía |

NDVI consulta solo plataforma Terra (`MOD13Q1`), por cada tile y mes selecciona el compuesto de 16 días más cercano al día 15. El Data API de Planetary Computer recorta cada tile al bbox intersectado y devuelve NDVI+QA juntos como GeoTIFF de 256×256; se filtran píxeles cuyo `250m_16_days_pixel_reliability` no sea 0, se descartan valores fuera de -2000..10000 y se aplica escala `0.0001`. La media usa los píxeles válidos muestreados del compuesto seleccionado, con ponderación aproximada por área geográfica; es una estimación regional más gruesa que recorrer cada píxel nativo de 250 m. Un mes sin píxeles válidos es `missing`; no se interpola. Las consultas NDVI se ejecutan como trabajo asíncrono. Meteomatics consulta una sola serie diaria por polígono, la agrega a meses y usa concurrencia acotada entre zonas. La media diaria de temperatura (`t_mean_2m_24h:C`) se promedia por mes; la precipitación diaria (`precip_24h:mm`) se suma por mes. Mantener el mismo producto durante todo el intervalo; no mezclar fuentes históricas.

Las respuestas completas de series se guardan en SQLite por variable, producto, bbox y periodo; TTL de 24 horas. Una repetición exacta evita volver a llamar al proveedor y también funciona después de reiniciar la API local. NDVI conserva además su caché en memoria durante el proceso.

Planetary Computer se consulta mediante STAC y assets cloud-optimized. Meteomatics requiere autenticación y el historial depende del plan. Giovanni y CO₂ quedan fuera del MVP hasta identificar producto, acceso y cobertura. LST MODIS (`modis-11A2-061`) es posterior y representa temperatura de superficie, no temperatura del aire.

| regionId | BBox `(latMin, latMax, lonMin, lonMax)` | Variables |
|---|---|---|
| `amazon` | `(-20, 5, -80, -45)` | `ndvi`, `precipitation` |
| `arctic` | `(66.5, 90, -180, 180)` | `air_temperature` |

Las coordenadas son WGS84. Planetary Computer recibe `[lonMin, latMin, lonMax, latMax]`; Meteomatics usa el orden de coordenadas propio de su API.

## Ejemplo de respuesta de series

```json
{
  "data": {
    "variable": { "variableId": "ndvi", "name": "NDVI", "description": "Índice de vegetación", "unit": "index", "source": "planetary-computer:modis-13Q1-061:250m_16_days_NDVI", "category": "vegetation", "minYears": 1 },
    "region": { "regionId": "amazon", "name": "Amazon Basin", "bbox": { "latMin": -20, "latMax": 5, "lonMin": -80, "lonMax": -45 }, "description": "Amazon rainforest extent", "type": "predefined" },
    "timeSeries": [
      { "seriesId": "ndvi:amazon:2020-01-01", "variableId": "ndvi", "regionId": "amazon", "date": "2020-01-01", "value": 0.72, "quality": "ok" }
    ],
    "trendAnalysis": null
  }
}
```
