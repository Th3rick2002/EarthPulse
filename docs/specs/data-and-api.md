# Datos, fuentes y API

## Modelo compartido

El esquema lógico usa cinco entidades: `variables`, `regions`, `time_series`, `trend_analysis` y `cache`. La persistencia puede mapearlas a tablas SQL o documentos; los campos HTTP descritos aquí son el contrato compartido.

| Entidad | Campos principales | Regla |
|---|---|---|
| Variable | `variableId`, `name`, `description`, `unit`, `source`, `category`, `minYears` | IDs estables; `source` identifica proveedor y producto. |
| Región | `regionId`, `name`, `bbox`, `description`, `type` | `bbox` WGS84; `type` es `predefined` o `custom`. |
| Punto mensual | `seriesId`, `variableId`, `regionId`, `date`, `value`, `quality` | Fecha el primer día del mes; `missing` implica `value: null`. |
| Tendencia | `analysisId`, `variableId`, `regionId`, `startDate`, `endDate`, `slope`, `pValue`, `significant`, `interpretation`, `createdAt` | Fechas inclusivas; pendiente en unidad de variable por año. |
| Cache | `cacheKey`, `variableId`, `regionId`, `startDate`, `endDate`, `data`, `fetchedAt`, `ttl` | Interna del backend; TTL objetivo de 24 horas. |

Las relaciones de variable y región se validan en backend y se representan como claves foráneas en SQL o referencias por ID en Firestore. La caché no se expone al frontend. No se crean interpolaciones silenciosas.

## Contrato HTTP canónico FE/BE

Los modelos Pydantic en `backend/app/schemas/contract.py` y OpenAPI (`/openapi.json`) son la referencia de implementación. Swagger UI está disponible en `/docs`.

- Prefijo: `/api/v1`.
- JSON usa camelCase.
- Respuestas exitosas: `{ "data": ... }`, excepto `/api/v1/health`, que devuelve directamente `HealthResponse`.
- Errores: `{ "error": { "code", "message", "details", "requestId" } }`; el mismo ID se devuelve en `X-Request-ID`.
- Fechas: ISO 8601. `startDate` y `endDate` son inclusivas y cubren meses completos: inicio día 1, fin último día.
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
| `GET /api/v1/regions` | `{data: Region[]}` |
| `GET /api/v1/series?variableId=…&regionId=…&startDate=…&endDate=…` | `{data: {variable, region, timeSeries[], trendAnalysis}}` |
| `GET /api/v1/health` | `HealthResponse` directa, sin wrapper `data` |

La creación de regiones personalizadas y otros endpoints no enumerados aquí siguen pendientes de implementación; el frontend no debe asumir que `POST /api/v1/regions` está disponible.

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
- Para generar tendencia se requieren al menos `minYears` años completos, tres observaciones válidas como mínimo y calidad `ok` en al menos el 50% de los meses solicitados.
- Los puntos `missing` e `interpolated` no cuentan como observaciones del análisis; los meses faltantes no comprimen el intervalo temporal.
- Si la cobertura no alcanza el mínimo, `trendAnalysis` es `null`.
- La significancia es `pValue < 0.05`; significancia no implica causalidad.

## Catálogo MVP

| variableId | Fuente y producto | Unidad de salida | Región |
|---|---|---|---|
| `ndvi` | Planetary Computer STAC `modis-13Q1-061`, asset `250m_16_days_NDVI` | NDVI adimensional | Amazonía |
| `air_temperature` | Meteomatics ERA5 `t_2m:C` | °C | Ártico |
| `precipitation` | Meteomatics CHIRPS `precip_24h:mm` | mm | Amazonía |

NDVI requiere aplicar escala `0.0001`, filtrar QA y resumir los compuestos de 16 días a mes. Temperatura se resume como media mensual. Precipitación diaria se suma por mes. Confirmar disponibilidad de CHIRPS en el plan Meteomatics. Mantener el mismo producto durante todo el intervalo; no mezclar fuentes históricas.

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
    "variable": { "variableId": "ndvi", "name": "NDVI", "description": "Índice de vegetación", "unit": "index", "source": "planetary-computer:modis-13Q1-061:250m_16_days_NDVI", "category": "vegetation", "minYears": 5 },
    "region": { "regionId": "amazon", "name": "Amazon Basin", "bbox": { "latMin": -20, "latMax": 5, "lonMin": -80, "lonMax": -45 }, "description": "Amazon rainforest extent", "type": "predefined" },
    "timeSeries": [
      { "seriesId": "ndvi:amazon:2020-01-01", "variableId": "ndvi", "regionId": "amazon", "date": "2020-01-01", "value": 0.72, "quality": "ok" }
    ],
    "trendAnalysis": null
  }
}
```
