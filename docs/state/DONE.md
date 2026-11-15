# DONE

## Estructura y coordinación

- Documentación compartida en `/docs`, reglas y especificaciones del MVP.
- GitHub Project con historias por Backend, Frontend e Infra.
- Instrucciones de desarrollo para frontend y backend documentadas en sus README.

## Backend

- Integrado el PR #1 con DTOs canónicos y rutas `/api/v1/variables`, `/api/v1/regions`, `/api/v1/series` y `/api/v1/health`.
- Validación de rangos mensuales, DTOs y errores comunes con `requestId`.
- Cobertura de tendencia: mínimo `minYears`, tres observaciones y 50% de meses con calidad `ok`.
- Meteomatics implementado para temperatura ERA5 y precipitación CHIRPS: consulta agregados diarios del área y forma puntos mensuales; maneja faltantes, timeouts y cierre de sesión HTTP.
- Planetary Computer para NDVI MODIS: STAC selecciona el compuesto más cercano a mitad de mes por tile; el Data API devuelve NDVI+QA recortados en GeoTIFF para filtrar y agregar. Aplica calidad MODIS, escala `0.0001` y ponderación geográfica aproximada.
- Las consultas NDVI responden `202` y el frontend sondea el job sin mantener una petición HTTP abierta. Resultados completados se reutilizan 24 horas en memoria del proceso.
- La consulta Meteomatics depende de que la cuenta tenga habilitados los productos históricos usados; Planetary Computer no requiere credenciales para este dataset público.
- FastAPI publica Swagger en `/docs` y OpenAPI en `/openapi.json`.
- Consulta real `ndvi/amazon`, 2021–2025, completada con el código final en 116.1 s: devolvió 60 meses, 56 observaciones `ok` y análisis de tendencia. Consulta real de un mes: 11.9 s; su repetición aprovechó la caché del proceso. El flujo completo respondió `202` mientras trabajaba y `200` al completar.

## Frontend

- Pantalla Explorador con consulta, globo 3D, gráfica, veredicto y estados de carga/error/sin datos.
- Cliente HTTP único (`src/services/api.ts`) y modelos TypeScript provisionales (`src/types/api.ts`).
- Compatibilidad de MVP limitada a NDVI/Amazonía, temperatura/Ártico y precipitación/Amazonía.

## Pendiente de verificación

- Los tipos aún no se generan desde OpenAPI; `POST /api/v1/regions` y publicación de combinaciones válidas no están implementados.

## Verificación del frontend contra backend integrado

- Selector limita pares al catálogo MVP aceptado por backend.
- Mensaje de `trendAnalysis: null` contempla tanto años completos como cobertura observada mínima.
- README de frontend y backend actualizado para reflejar el estado real y comandos de arranque.
- `pnpm lint` y `pnpm build` pasan; build muestra advertencia de chunk JS mayor a 500 kB.

## Scripts de desarrollo

- `scripts/dev.sh` inicia backend y frontend localmente.
- `scripts/dev-docker-backend.sh` inicia el backend en Docker y el frontend con Vite local.
- `scripts/README.md` documenta uso y requisitos.
- Script local probado con `/api/v1/health`, `/api/v1/variables` y Vite; Docker no está instalado en este entorno para probar el segundo script.
