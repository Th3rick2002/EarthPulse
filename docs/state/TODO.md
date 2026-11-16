# TODO

Las historias y criterios de terminado se gestionan en el [GitHub Project TrendScope — MVP](https://github.com/users/Th3rick2002/projects/4). Esta lista resume los siguientes pasos.

## Prioridad alta

### Frontend

- [ ] Generar tipos TypeScript desde `/openapi.json`; el cliente API existe, pero `src/types/api.ts` aún es manual.
- [ ] Hacer revisión manual responsive en escritorio, tablet y móvil, incluidos mapa, tarjetas de zona, veredicto y gráfica.

### Backend / datos

- [ ] Publicar en catálogo las combinaciones variable-región válidas.
- [ ] Terminar `POST /api/v1/regions` y el formulario frontend para regiones guardadas; hoy las zonas dibujadas son temporales a una comparación.
- [ ] Persistir jobs y compartirlos entre instancias; ahora los jobs asíncronos viven en memoria.
- [ ] Configurar persistencia de caché para producción en Render según el almacenamiento elegido; SQLite requiere disco persistente y una sola instancia, mientras que el escalado horizontal necesita un datastore compartido.

## Prioridad media

- [ ] Confirmar disponibilidad de CHIRPS y ERA5 histórico en el plan Meteomatics y probar consultas reales en el despliegue.
- [ ] Validar cobertura temporal histórica y límites de resolución en las cuatro zonas soportadas.
- [ ] Añadir logging estructurado, métricas y health checks de proveedor.
- [x] Configurar `CORS_ORIGINS` en Render con el origen exacto de Cloudflare Pages; el frontend publicado ya se comunica con el backend.
- [ ] Desplegar el log de diagnóstico del proveedor, repetir la consulta NDVI y revisar el stack trace de Render para identificar la excepción de Planetary Computer.
- [ ] Completar despliegue de backend en Render; usar `PORT`, CORS y variables secretas del servicio.
- [ ] Configurar Firestore si se mantiene como caché compartida de producción.

## Infraestructura y equipo

- [ ] Verificar que los otros dos devs tengan permisos de edición en el GitHub Project (el proyecto es público, pero eso no garantiza permisos de edición).
- [ ] Definir hosting frontend y configurar credenciales como secretos.
