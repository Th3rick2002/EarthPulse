# TODO

Las historias con requerimientos y criterios de terminado se gestionan en el [GitHub Project TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4). Esta lista resume el orden de trabajo; no reemplaza las tarjetas.

## Prioridad alta

### Backend / datos

- [ ] Confirmar cuenta Meteomatics y disponibilidad de CHIRPS `precip_24h:mm`.
- [ ] Implementar `MeteomaticsClient.fetch_monthly()` con autenticación, agregación, timeout y manejo de rate limits.
- [ ] Implementar Planetary Computer STAC para MODIS NDVI: búsqueda por bbox/fecha, QA, escala y agregación espacial/temporal.
- [ ] Añadir cache TTL de 24 h a `GET /api/v1/series` usando el esquema acordado.
- [ ] Completar integración Firestore si será el almacenamiento de despliegue.

### Frontend

- [ ] Generar tipos TypeScript desde `/openapi.json` y consumir `/api/v1/*`.
- [ ] Integrar selector variable/región, globo, serie temporal y tarjeta de tendencia.
- [ ] Cubrir loading, error, sin observaciones y `trendAnalysis: null` según `docs/specs/ui-ux.md`.

## Prioridad media

- [ ] Validar fechas futuras y reglas de bbox para regiones personalizadas.
- [ ] Añadir logging estructurado y métricas por endpoint/proveedor.
- [ ] Revisar health check y operación ante indisponibilidad de proveedores.

## Prioridad baja

- [ ] Añadir LST MODIS solo cuando el MVP tenga necesidad y proveedor validados.
- [ ] Evaluar regiones adicionales y análisis estacional/intervalos de confianza.
- [ ] Agregar detección de outliers si lo requiere el producto.

## Equipo e infraestructura

- [ ] Dar acceso al GitHub Project privado a los otros dos devs.
- [ ] Definir hosting frontend antes de crear la tarea de despliegue.
- [ ] Configurar credenciales como secretos en el entorno de despliegue.
