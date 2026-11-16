# HANDOFF

## Estado actual

El backend PR #1 está integrado en `dev`. La rama `feat/integration-external-api` está publicada en `origin` con el commit `24871eb` (`feat: integra consultas y mejora EarthPulse`). El único elemento sin seguimiento en la copia local es `backend/backend/data/trendscope.db`, una base runtime que no debe agregarse al repositorio.

- API canónica `/api/v1`: catálogo, `GET /series`, `POST /series/compare` para 1–4 áreas bbox y `GET /series/jobs/{jobId}`; Swagger `/docs`.
- Catálogo MVP: NDVI/Amazonía, temperatura del aire/Ártico y precipitación/Amazonía.
- El frontend consume camelCase con `src/services/api.ts`; los tipos siguen siendo manuales.
- El mapa Leaflet permite dibujar y nombrar hasta cuatro rectángulos independientes de hasta 35°×25°; cada uno se procesa por separado.
- Commit `397170c` registra el rediseño Leaflet, las consultas independientes por rectángulo y la caché SQLite. El commit `24871eb` integra consulta adaptativa de lluvia, disponibilidad dinámica, modalidad de carga y refinamientos de EarthPulse.
- Para lluvia CHIRPS, Meteomatics usa `adaptive_grid`; ERA5 conserva `model_grid`. Se verificó una consulta backend real para enero de 2025 en un rectángulo de 1° en Amazonía, con precipitación observada. Falta reproducir el HTTP 400 original con sus fechas y bbox; la respuesta ahora conserva `upstreamStatus` y `upstreamMessage` en `error.details` para identificarlo si persiste.
- La causa del error más reciente quedó identificada: UI permitía octubre de 2026, pero el `get_time_range` autenticado de Meteomatics reportó CHIRPS disponible hasta `2026-10-01T00:00:00Z`, límite derecho que representa hasta el 30 de septiembre. `GET /api/v1/availability?variableId=precipitation`, la caché del metadato por 6h, el límite dinámico del selector y la validación backend están implementados en `24871eb`.
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
- La producción se desplegará en Render. El filesystem es efímero por defecto; SQLite requiere un disco persistente en servicio pago y ese servicio queda limitado a una instancia. Para escalar horizontalmente, jobs y caché requieren almacenamiento compartido. En Docker local se debe montar `backend/data` para conservar SQLite.
- CORS de FastAPI lee `CORS_ORIGINS` desde el entorno. El frontend publicado ya llega al backend Render y recibe `Access-Control-Allow-Origin` para `https://earthpulse.3rick694.workers.dev`.
- El problema activo es un `502` al consultar el job `cc6dd00d849a4a3b8b49dc188cb7b91d`. El cuerpo recuperado identifica `provider: planetary-computer`, pero no trae estado ni mensaje upstream: el backend desplegado está ocultando una excepción inesperada durante la consulta STAC/raster. Se agregó registro de la excepción con stack trace en `backend/app/services/providers.py`; aún falta desplegarlo y revisar el log del siguiente intento para encontrar la causa concreta. El request de polling recuperado tuvo ID `7d9faaa753cc4deead14a96957ff29fd`.
- UI rediseñada: mapa Leaflet/OpenStreetMap, rectángulos múltiples, formulario guiado, fechas mes/año, resumen explicativo y ficha de fuente a la derecha. Especificación actualizada en `docs/specs/ui-ux.md`.
- Revisión de usabilidad aplicada el 2026-11-15 e integrada en `24871eb`: EarthPulse como marca visible y título del navegador; veredictos no significativos sin afirmar dirección; NDVI identificado con rango −1 a 1; pluralización y formato decimal español; gráfica recortada a meses con datos en los extremos; ayudas accesibles y guía visual del mapa. Pendiente revisión visual manual.
- Las zonas dibujadas se muestran debajo del mapa en tarjetas adaptables: nombre editable, bbox completo y botón de quitar con icono neutral y etiqueta accesible.
- El control para quitar cada tarjeta es una X discreta sin fondo, ubicada en la esquina superior derecha.
- GitHub Project sincronizado el 2026-11-15: siete historias Done, cuatro In Progress y tres Todo. La historia de despliegue ahora apunta a Render. Quedan abiertas la generación de tipos, despliegue/secretos, persistencia de caché para producción y el alcance de regiones guardadas.
- Scripts de desarrollo: `scripts/dev.sh` (API y Vite locales) y `scripts/dev-docker-backend.sh` (API Docker y Vite local); guía en `scripts/README.md`.
- `scripts/dev.sh` fue ejecutado: `/api/v1/health`, `/api/v1/variables` y Vite respondieron. Docker no está instalado en este entorno, así que no se ejecutó la variante Docker.
- Los logs `GET /api/v1/series/jobs/{jobId}` con `202` durante el sondeo y `200` al terminar son el flujo normal. `scripts/dev.sh` no solicita `/health`; la ruta canónica es `/api/v1/health`. Los `404` a `/health` provienen de otro sondeador local no identificado en el repositorio y no afectan la consulta.

## Siguiente acción

1. Generar tipos TypeScript desde `/openapi.json` y retirar los tipos manuales.
2. Revisar visualmente EarthPulse en escritorio y móvil, incluidos veredicto, mapa, tarjetas de zonas y gráficas.
3. Completar `POST /api/v1/regions` y el formulario frontend solo si se mantiene la función de regiones guardadas; las zonas dibujadas actuales son temporales por consulta.
4. Confirmar si producción usará SQLite en un disco persistente de Render con una sola instancia o un datastore compartido para escalar; luego configurar caché/jobs.
5. Desplegar el log de diagnóstico del proveedor, repetir la misma consulta NDVI y revisar en Render el stack trace; corregir la causa concreta que aparezca.

## Entorno y documentos

- `frontend/` usa pnpm; respetar `pnpm-lock.yaml`.
- Backend fija Python 3.11 en Docker.
- No versionar credenciales ni `.env`; no editar `frontend/node_modules/` o `backend/venv/`.
- Reglas: `docs/rules/coding.md`, `docs/rules/domain.md`.
- Contrato: `docs/specs/data-and-api.md`; UX: `docs/specs/ui-ux.md`.
- Project: [TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4).
- Inicio: `frontend/README.md`, `backend/README.md`.
