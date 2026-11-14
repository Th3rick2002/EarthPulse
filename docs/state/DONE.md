# DONE

## Estructura y coordinación

- Documentación compartida en `/docs`, reglas y especificaciones del MVP.
- GitHub Project con historias por Backend, Frontend e Infra.
- Instrucciones de desarrollo para frontend y backend documentadas en sus README.

## Backend

- Integrado el PR #1 con DTOs canónicos y rutas `/api/v1/variables`, `/api/v1/regions`, `/api/v1/series` y `/api/v1/health`.
- Validación de rangos mensuales, DTOs y errores comunes con `requestId`.
- Cobertura de tendencia: mínimo `minYears`, tres observaciones y 50% de meses con calidad `ok`.
- Fallos de proveedor explícitos; adaptadores Meteomatics y Planetary Computer siguen pendientes.
- FastAPI publica Swagger en `/docs` y OpenAPI en `/openapi.json`.

## Frontend

- Pantalla Explorador con consulta, globo 3D, gráfica, veredicto y estados de carga/error/sin datos.
- Cliente HTTP único (`src/services/api.ts`) y modelos TypeScript provisionales (`src/types/api.ts`).
- Compatibilidad de MVP limitada a NDVI/Amazonía, temperatura/Ártico y precipitación/Amazonía.

## Pendiente de verificación

- Terminar rebase de `feat/frontend-explorer` sobre `dev`.
- Ejecutar lint y build después de los ajustes de compatibilidad.
- Los tipos aún no se generan desde OpenAPI; `POST /api/v1/regions` y publicación de combinaciones válidas no están implementados.
