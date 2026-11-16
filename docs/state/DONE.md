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
- Las consultas NDVI responden `202` y el frontend sondea el job sin mantener una petición HTTP abierta. La respuesta completa también se guarda 24 horas en caché SQLite.
- La consulta Meteomatics depende de que la cuenta tenga habilitados los productos históricos usados; Planetary Computer no requiere credenciales para este dataset público.
- FastAPI publica Swagger en `/docs` y OpenAPI en `/openapi.json`.
- Consulta real `ndvi/amazon`, 2021–2025, completada con el código final en 116.1 s: devolvió 60 meses, 56 observaciones `ok` y análisis de tendencia. Consulta real de un mes: 11.9 s; su repetición aprovechó la caché del proceso. El flujo completo respondió `202` mientras trabajaba y `200` al completar.

## Frontend

- Pantalla Explorador con consulta guiada, mapa Leaflet, gráficas, veredictos y estados de carga/error/sin datos.
- Cliente HTTP único (`src/services/api.ts`) y modelos TypeScript provisionales (`src/types/api.ts`).
- Catálogo inicial: NDVI, temperatura y precipitación; el mapa permite dibujar áreas adicionales con bbox y comparar hasta cuatro a la vez.
- Explorador rediseñado en español claro con consulta guiada, mapa Leaflet, mensajes de espera con tiempo transcurrido y explicación principal antes de los datos técnicos.
- Resumen de tendencias y errores localizados al español; estadísticas avanzadas quedan en un panel ampliable. Se añadieron controles accesibles, diseño adaptable y respeto a movimiento reducido.
- `docs/specs/ui-ux.md` actualizado para reflejar la experiencia implementada y aclarar que el mapa muestra el área agregada, no datos por píxel.
- Selector de zonas migrado a Leaflet con hasta cuatro rectángulos independientes; comparación de series por área mediante `POST /api/v1/series/compare`.
- Intervalos configurables entre 1 y 50 años; caché persistente SQLite de series completas con TTL de 24 horas, clave por variable/producto/bbox/periodo.
- Retiradas las dependencias Three.js sin uso; Leaflet y la gráfica se cargan de forma diferida.

## Pendiente de verificación

- Los tipos aún no se generan desde OpenAPI; `POST /api/v1/regions` y publicación de combinaciones válidas no están implementados.

## Verificación del frontend contra backend integrado

- Comparación acepta hasta cuatro áreas dibujadas y muestra una serie independiente por área.
- Mensaje de `trendAnalysis: null` contempla tanto años completos como cobertura observada mínima.
- README de frontend y backend actualizado para reflejar el estado real y comandos de arranque.
- `pnpm lint`, `pnpm build`, `compileall` de Python y `git diff --check` pasan. Vite aún avisa que un chunk supera 500 kB; el mapa y la gráfica se cargan en chunks diferidos.

## Scripts de desarrollo

- `scripts/dev.sh` inicia backend y frontend localmente.
- `scripts/dev-docker-backend.sh` inicia el backend en Docker y el frontend con Vite local.
- `scripts/README.md` documenta uso y requisitos.
- Script local probado con `/api/v1/health`, `/api/v1/variables` y Vite; Docker no está instalado en este entorno para probar el segundo script.

## Revisión de usabilidad y marca — 2026-11-15

- Se corrigió el veredicto para que solo afirme una dirección cuando la tendencia es significativa; los casos sin señal clara usan estilo neutro.
- La interfaz identifica NDVI, muestra su rango documentado (−1 a 1) y corrige la frase duplicada del selector.
- Se corrigió “1 año seleccionado”, se aclaró la cobertura de observaciones y se unificó el formato decimal español en valores y coordenadas.
- La gráfica omite periodos vacíos en sus extremos y conserva los huecos internos con una explicación; el mapa muestra un rectángulo de ejemplo, explica el máximo de cuatro zonas y etiqueta el zoom.
- La marca visible y el título de la pestaña ahora dicen EarthPulse. Se vinculó el mensaje de validación con el botón de consulta para tecnologías de asistencia.
- La lista de zonas del mapa se rediseñó como tarjetas responsivas, con nombre editable, coordenadas completas y botón de quitar mediante icono accesible.
- El control de quitar usa una X discreta sin fondo en la esquina superior derecha de cada tarjeta.

## Sincronización GitHub Project — 2026-11-15

- Se marcaron Done las historias de catálogo, DTO/OpenAPI, flujo frontend, proveedores NDVI y Meteomatics, análisis de tendencia y visualización con mapa/gráfica/veredicto.
- Se dejaron In Progress las rutas FastAPI (falta `POST /regions`), la caché (SQLite está implementada; falta persistencia compartida para producción) y despliegue GCP (avance externo por confirmar).
- La historia de tipos/client API está In Progress: el cliente funciona y falta generar los tipos OpenAPI. Permanecen Todo la configuración de Firestore y la persistencia de regiones custom en backend y frontend.
- Se actualizó la historia de visualización para reflejar el mapa Leaflet acordado en lugar del globo 3D anterior.
- El objetivo de despliegue se actualizó de GCP/Cloud Run a Render; la configuración real de producción sigue pendiente.
- FastAPI ahora carga `CORS_ORIGINS` desde el entorno, conserva localhost como default de desarrollo y documenta la configuración del origen Cloudflare Pages en Render.
