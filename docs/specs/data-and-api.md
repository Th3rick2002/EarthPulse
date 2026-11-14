# Datos, fuentes y API

## Contrato HTTP canónico (FE/BE)

Este documento define el contrato exacto entre frontend y backend. Los modelos Pydantic en `backend/app/schemas/contract.py` y la especificación OpenAPI en `/openapi.json` son la implementación de referencia.

### Convenciones globales

- **Prefijo API**: `/api/v1`
- **Envoltura de respuesta exitosa**: `{data: ...}`
- **Envoltura de error**: `{error: {code, message, details, requestId}}`
- **Nomenclatura JSON**: camelCase
- **Fechas**: ISO 8601 (`YYYY-MM-DD` para fechas, `date-time` para timestamps)
- **startDate/endDate**: Inclusivas, cubren meses completos (inicio día 1, fin último día del mes)
- **Caché**: Interna, no expuesta en DTO público

---

### Entidades JSON

#### Variable
```json
{
  "variableId": "string",
  "name": "string",
  "description": "string",
  "unit": "string",
  "source": "string",
  "category": "string",
  "minYears": "integer"
}
```

#### Region
```json
{
  "regionId": "string",
  "name": "string",
  "bbox": {"latMin": "number", "latMax": "number", "lonMin": "number", "lonMax": "number"},
  "description": "string",
  "type": "predefined | custom"
}
```

#### TimeSeries (punto mensual)
```json
{
  "seriesId": "string",
  "variableId": "string",
  "regionId": "string",
  "date": "YYYY-MM-DD",
  "value": "number | null",
  "quality": "ok | missing | interpolated"
}
```
> `value` es `null` solo si `quality === "missing"`. Cada `date` es el primer día del mes UTC.

#### TrendAnalysis
```json
{
  "analysisId": "string",
  "variableId": "string",
  "regionId": "string",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "slope": "number",
  "pValue": "number",
  "significant": "boolean",
  "interpretation": "string",
  "createdAt": "date-time"
}
```
> `slope` se expresa en unidad de Variable por año. Fechas inclusivas.

#### ApiError
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object",
    "requestId": "string"
  }
}
```

---

### Rutas y envolturas

| Método | Ruta | Respuesta exitosa |
|--------|------|-------------------|
| GET | `/api/v1/variables` | `{data: Variable[]}` |
| GET | `/api/v1/regions` | `{data: Region[]}` |
| GET | `/api/v1/series?variableId=...&regionId=...&startDate=...&endDate=...` | `{data: {variable: Variable, region: Region, timeSeries: TimeSeries[], trendAnalysis: TrendAnalysis|null}}` |
| GET | `/api/v1/health` | `HealthResponse` |

---

### Códigos de error

| Código HTTP | Error code | Cuándo |
|-------------|------------|--------|
| 400 | `INVALID_PARAMS` | Fechas inválidas, bbox inválido, combinación variable-región no soportada, startDate ≥ endDate |
| 404 | `NOT_FOUND` | Variable o región no existe en catálogo |
| 422 | `VALIDATION_ERROR` | Error de validación de parámetros (FastAPI) |
| 500 | `INTERNAL_ERROR` | Error interno del servidor |

---

## Catálogo MVP implementado

### Variables

| variableId | name | category | unit | source | minYears | Regiones soportadas |
|------------|------|----------|------|--------|----------|---------------------|
| `ndvi` | NDVI (Normalized Difference Vegetation Index) | vegetation | index | planetary-computer:modis-13Q1-061:250m_16_days_NDVI | 5 | amazon |
| `air_temperature` | Air Temperature (2m) | temperature | °C | meteomatics:ecmwf-era5:t_2m:C | 5 | arctic |
| `precipitation` | Precipitation | precipitation | mm | meteomatics:chc-chirps3:precip_24h:mm | 5 | amazon |

> `land_surface_temperature` dejado para después (MODIS 11A2 no equivale a temperatura del aire).

### Regiones

| regionId | name | type | bbox (latMin, latMax, lonMin, lonMax) | Variables |
|----------|------|------|----------------------------------------|-----------|
| `amazon` | Amazon Basin | predefined | (-20.0, 5.0, -80.0, -50.0) | ndvi, precipitation |
| `arctic` | Arctic Circle | predefined | (66.5, 90.0, -180.0, 180.0) | air_temperature |

> El bbox del Ártico usa rango longitudinal completo (-180, 180) para cruzar el antimeridiano.

---

## Ejemplos de respuesta

### GET /api/v1/variables
```json
{
  "data": [
    {
      "variableId": "ndvi",
      "name": "NDVI (Normalized Difference Vegetation Index)",
      "description": "Vegetation health index from MODIS surface reflectance. Values range -1 to 1; higher = greener.",
      "unit": "index",
      "source": "planetary-computer:modis-13Q1-061:250m_16_days_NDVI",
      "category": "vegetation",
      "minYears": 5
    },
    ...
  ]
}
```

### GET /api/v1/regions
```json
{
  "data": [
    {
      "regionId": "amazon",
      "name": "Amazon Basin",
      "bbox": {"latMin": -20.0, "latMax": 5.0, "lonMin": -80.0, "lonMax": -50.0},
      "description": "Amazon rainforest extent for vegetation and precipitation monitoring.",
      "type": "predefined"
    },
    ...
  ]
}
```

### GET /api/v1/series (con tendencia)
```json
{
  "data": {
    "variable": { ... },
    "region": { ... },
    "timeSeries": [
      {"seriesId": "ndvi:amazon:2018-01-01", "variableId": "ndvi", "regionId": "amazon", "date": "2018-01-01", "value": 0.6548, "quality": "ok"},
      {"seriesId": "ndvi:amazon:2018-02-01", "variableId": "ndvi", "regionId": "amazon", "date": "2018-02-01", "value": 0.6182, "quality": "ok"}
    ],
    "trendAnalysis": {
      "analysisId": "ndvi:amazon:2018-01-01:2023-12-31",
      "variableId": "ndvi",
      "regionId": "amazon",
      "startDate": "2018-01-01",
      "endDate": "2023-12-31",
      "slope": -0.00097,
      "pValue": 0.7743,
      "significant": false,
      "interpretation": "The monthly index shows a decreasing trend (-0.0010 index/year), which is not statistically significant (Mann-Kendall p = 0.7743). Note: significance does not imply causation.",
      "createdAt": "2026-11-14T19:16:28.854059"
    }
  }
}
```

### GET /api/v1/series (cobertura insuficiente - sin análisis)
```json
{
  "data": {
    "variable": { ... },
    "region": { ... },
    "timeSeries": [ ... ],
    "trendAnalysis": null
  }
}
```

### Error response
```json
{
  "error": {
    "code": "INVALID_PARAMS",
    "message": "Variable 'ndvi' not supported in region 'arctic'",
    "details": {},
    "requestId": "req-003"
  }
}
```

---

## Conversión de bbox por proveedor (interno)

- **Planetary Computer (STAC)**: `[lonMin, latMin, lonMax, latMax]`
- **Meteomatics**: `{latMin, latMax, lonMin, lonMax}`

El contrato expone bbox como objeto `{latMin, latMax, lonMin, lonMax}` (WGS84/EPSG:4326).

---

## Análisis de tendencia (interno)

- **Método**: Mann-Kendall test + Sen's slope (Theil-Sen estimator)
- **Significancia**: `p < 0.05`
- **Pendiente**: Expresada en unidad de variable por año (convertida desde mensual × 12)
- **Interpretación**: Texto en lenguaje natural indicando dirección, significancia y advertencia de causalidad
- **Mínimo observaciones**: 3 puntos válidos (quality="ok") para ejecutar test; 5 años de cobertura para análisis válido