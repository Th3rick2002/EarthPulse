# HANDOFF

## Estado actual

El backend PR #1 está integrado en `dev`. La rama local `feat/frontend-explorer` ya fue rebasada sobre ese `dev`; resolución y cambios de compatibilidad están en la copia de trabajo.

- API canónica `/api/v1`: catálogo, `GET /series`, `POST /series/compare` para 1–4 áreas bbox y `GET /series/jobs/{jobId}`; Swagger `/docs`.
- Catálogo MVP: NDVI/Amazonía, temperatura del aire/Ártico y precipitación/Amazonía.
- El frontend consume camelCase con `src/services/api.ts`; los tipos siguen siendo manuales.
- El mapa Leaflet permite dibujar y nombrar hasta cuatro rectángulos independientes de hasta 35°×25°; cada uno se procesa por separado.
- Commit `397170c` registra el rediseño Leaflet, las consultas independientes por rectángulo y la caché SQLite. Después de ese commit hay cambios locales pendientes para la consulta CHIRPS y el modal de carga.
- Para lluvia CHIRPS, Meteomatics usa `adaptive_grid`; ERA5 conserva `model_grid`. Se verificó una consulta backend real para enero de 2025 en un rectángulo de 1° en Amazonía, con precipitación observada. Falta reproducir el HTTP 400 original con sus fechas y bbox; la respuesta ahora conserva `upstreamStatus` y `upstreamMessage` en `error.details` para identificarlo si persiste.
- La causa del error más reciente quedó identificada: UI permitía octubre de 2026, pero el `get_time_range` autenticado de Meteomatics reportó CHIRPS disponible hasta `2026-10-01T00:00:00Z`, límite derecho que representa hasta el 30 de septiembre. Implementado `GET /api/v1/availability?variableId=precipitation`, caché del metadato por 6h, límite dinámico en el selector y validación equivalente en backend. Cambios todavía sin commit.
- El estado de búsqueda ahora se presenta en un diálogo modal accesible, con foco y scroll del fondo bloqueados.
- El intervalo de frontend y backend permite 1–50 años completos. `minYears=1` para las variables MVP; la disponibilidad histórica real depende de cada proveedor.
- El backend valida las áreas, procesa hasta dos en paralelo por tanda y cachea cada respuesta completa en SQLite durante 24h por variable/producto/bbox/periodo. La caché local persiste entre reinicios; los jobs asíncronos aún viven en memoria.
- El backend aún no tiene `POST /api/v1/regions`; zonas dibujadas son temporales a la comparación, no elementos persistidos del catálogo.
- Meteomatics ahora consulta ERA5 (media diaria de temperatura) y CHIRPS (precipitación diaria) por polígono y los agrega a meses; verificar disponibilidad histórica en la cuenta con una petición real.
- Planetary Computer/NDVI busca páginas STAC de hasta 1000 elementos y selecciona el compuesto Terra más cercano a mitad de mes por tile. El Data API sirve NDVI+QA recortados juntos en GeoTIFF de 256×256; se filtra QA, se escala `0.0001` y se pondera el promedio por área aproximada.
- NDVI de rangos largos corre como job asíncrono (`202` + polling); la UI espera el job sin mantener una petición larga abierta. Resultados terminados se reutilizan 24 horas en memoria del proceso.
- Dependencias geoespaciales disponibles en `backend/venv` (Python 3.14.9 en esta máquina); la imagen Docker fija Python 3.11.
- El error `The planetary-computer integration is not implemented yet` solo puede venir de un backend levantado con código anterior: ese texto ahora existe únicamente en el mapeo de compatibilidad para clientes antiguos que lancen `NotImplementedError`. Reiniciar el backend local o reconstruir la imagen Docker carga el código actualizado.
- Consulta real NDVI/Amazonía del 2021-01 al 2025-12 completada con el código final por el flujo de job en 116.1 s: 60 meses, 56 observaciones válidas y tendencia generada. Una consulta real de un mes respondió en 11.9 s y la repetición usó caché.
- Para despliegues multiinstancia, jobs y caché requieren almacenamiento compartido; Docker necesita montar `backend/data` para conservar SQLite al recrear el contenedor.
- UI rediseñada: mapa Leaflet/OpenStreetMap, rectángulos múltiples, formulario guiado, fechas mes/año, resumen explicativo y ficha de fuente a la derecha. Especificación actualizada en `docs/specs/ui-ux.md`.
- Revisión de usabilidad aplicada el 2026-11-15: EarthPulse como marca visible y título del navegador; veredictos no significativos sin afirmar dirección; NDVI identificado con rango −1 a 1; pluralización y formato decimal español; gráfica recortada a meses con datos en los extremos; ayudas accesibles y guía visual del mapa. Cambios locales sin verificar visualmente.
- Las zonas dibujadas se muestran debajo del mapa en tarjetas adaptables: nombre editable, bbox completo y botón de quitar con icono neutral y etiqueta accesible.
- El control para quitar cada tarjeta es una X discreta sin fondo, ubicada en la esquina superior derecha.
- Scripts de desarrollo: `scripts/dev.sh` (API y Vite locales) y `scripts/dev-docker-backend.sh` (API Docker y Vite local); guía en `scripts/README.md`.
- `scripts/dev.sh` fue ejecutado: `/api/v1/health`, `/api/v1/variables` y Vite respondieron. Docker no está instalado en este entorno, así que no se ejecutó la variante Docker.
- Los logs `GET /api/v1/series/jobs/{jobId}` con `202` durante el sondeo y `200` al terminar son el flujo normal. `scripts/dev.sh` no solicita `/health`; la ruta canónica es `/api/v1/health`. Los `404` a `/health` provienen de otro sondeador local no identificado en el repositorio y no afectan la consulta.

## Siguiente acción

1. Revisar visualmente EarthPulse en escritorio y móvil, incluidos los nuevos estados del veredicto, el mapa y la gráfica.
2. Verificar la interfaz con lluvia: al seleccionarla debe ajustar el fin a septiembre de 2026 (según disponibilidad capturada el 2026-11-15) y el backend debe rechazar meses posteriores con límite claro.
3. Generar tipos desde `/openapi.json` y quitar los tipos manuales.
4. Verificar históricamente los intervalos elegidos frente a cobertura de cada fuente y permisos Meteomatics ERA5/CHIRPS.
5. Configurar volumen `backend/data` en Docker y hacer revisión manual responsive de las consultas multizona.

## Entorno y documentos

- `frontend/` usa pnpm; respetar `pnpm-lock.yaml`.
- Backend fija Python 3.11 en Docker.
- No versionar credenciales ni `.env`; no editar `frontend/node_modules/` o `backend/venv/`.
- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Contrato: `docs/specs/data-and-api.md`; UX: `docs/specs/ui-ux.md`.
- Project: [TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4).
- Inicio: `frontend/README.md`, `backend/README.md`.
