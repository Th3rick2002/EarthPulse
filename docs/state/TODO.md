# TODO

## Prioridad alta

### [P0] Dev 1 + Dev 3 - Integración real Meteomatics
- [ ] Confirmar acceso contratado a Meteomatics (Dev 3)
- [ ] Verificar que CHIRPS (precip_24h:mm) está habilitado en la cuenta
- [ ] Implementar `MeteomaticsClient.fetch_monthly()` con autenticación y paginación
- [ ] Manejar rate limits, timeouts, y errores de proveedor
- [ ] Añadir variables de entorno `METEOMATICS_USERNAME`, `METEOMATICS_PASSWORD` a `.env.example`

### [P0] Dev 1 - Integración real Planetary Computer
- [ ] Implementar `PlanetaryComputerClient.fetch_monthly()` usando STAC + rasterio/rioxarray
- [ ] Búsqueda STAC por colección `modis-13Q1-061`, bbox, rango temporal
- [ ] Lectura banda NDVI, escala 0.0001, agregación espacial (mean) y temporal (mensual)
- [ ] Manejar Cloud Optimized GeoTIFFs y signed URLs

### [P0] Dev 2 - Frontend integra API
- [ ] Generar tipos TypeScript desde OpenAPI spec (`openapi-typescript` o similar)
- [ ] Implementar hooks/servicios para `/variables`, `/regions`, `/series`
- [ ] UI: selector variable/región, gráfico temporal, tarjeta veredicto
- [ ] Estados: loading, error, sin datos, cobertura insuficiente

## Prioridad media

### [P1] Dev 1 - Caché con TTL 24h
- [ ] Integrar `SQLiteCacheRepository` en `GET /series`
- [ ] Clave de caché: `variableId:regionId:startDate:endDate:provider:product`
- [ ] Invalidar/actualizar según TTL
- [ ] Métricas: hit/miss ratio en logs

### [P1] Dev 1 - Validaciones adicionales
- [ ] Validar que `startDate`/`endDate` no sean futuras
- [ ] Validar bbox custom (área máxima, antimeridiano)
- [ ] Rate limiting básico en API

### [P1] Dev 1 - Métricas y observabilidad
- [ ] Logging estructurado (JSON) para requests/responses
- [ ] Métricas de latencia por endpoint
- [ ] Health check incluye conectividad a proveedores

## Prioridad baja

### [P2] Dev 1 - Variables/regiones adicionales
- [ ] `land_surface_temperature` (MODIS 11A2) cuando sea relevante
- [ ] Regiones adicionales: Congo, Boreal, etc.
- [ ] Regiones custom dibujadas por usuario (validación backend)

### [P2] Dev 1 - Mejoras análisis
- [ ] Test de estacionalidad (Mann-Kendall estacional)
- [ ] Intervalo de confianza para pendiente
- [ ] Detección de outliers en observaciones

---

## Notas de implementación

- **Rama actual**: `feat/backend-catalog-and-series` → PR a `dev`
- **Commits sugeridos**:
  1. `feat: catálogo variables/regiones + endpoints /variables /regions`
  2. `feat: endpoint /series con validación y análisis Mann-Kendall`
  3. `feat: esquemas Pydantic, servicios análisis, clientes proveedores mock`
  4. `feat: capa repositorio SQLite/Firestore`
  5. `docs: actualizar data-and-api.md con contratos finales`
- **Separar código de docs** en PRs distintos si el diff es grande