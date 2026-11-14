# Datos, fuentes y API

## Revisión del esquema propuesto

El esquema separa bien catálogo, regiones, observaciones, análisis y caché. Para hacerlo implementable:

- Usar claves estables y unicidad para variable/región/fecha/fuente; un `seriesId` por observación duplica identidad sin aportar mucho.
- Guardar en `variables` la definición y unidad canónica, y en una relación de fuentes/productos (o metadatos equivalentes) el proveedor, colección/producto, identificador de variable y unidad nativa. “Giovanni” es una plataforma de acceso/visualización, no identifica por sí sola el producto científico.
- Guardar bbox como cuatro campos validados y especificar CRS/orden. El bbox del Ártico cruza los límites de longitud; las consultas pueden requerir dos ventanas o una representación normalizada.
- El registro temporal debe identificar variable, región, fecha de periodo mensual, producto/fuente y valor. Definir cómo se agrega cada variable (media, suma u otra regla); no usar una agregación común a precipitación, temperatura y NDVI.
- No almacenar “missing” como si fuera un valor. Conservar estado de calidad junto a observaciones reales/interpoladas, e informar cobertura faltante por separado.
- Un análisis debe registrar intervalo, frecuencia, método/versión, número de observaciones, pendiente y unidad de pendiente, p-value, significancia y fecha de cálculo. Debe poder rastrearse a la serie/producto analizado.
- La clave de caché debe incluir fuente/producto, resolución/frecuencia, bbox o región, intervalo y versión de transformación. `ttl: 24h` es una duración; persistir `expiresAt`/`fetchedAt` y purgar o ignorar entradas vencidas.

## Persistencia sugerida

El plan original propone Firestore opcional para caché y despliega backend en Cloud Run. Firestore encaja mejor como persistencia compartida del MVP desplegado porque el disco local de Cloud Run no es persistente y puede haber varias instancias. SQLite sirve para desarrollo/local o una primera prueba de concepto; en producción requiere almacenamiento persistente y estrategia de concurrencia/backups. Mantener una capa de repositorio para que el motor analítico no dependa del almacén.

No hace falta guardar cada observación indefinidamente en una base si la fuente es reproducible y la política/licencia lo desaconseja: la serie puede vivir en caché con procedencia y caducidad. Aclarar esta política por dataset antes de persistir datos externos.

## Entidades recomendadas

- **Variable:** `id`, nombre, definición, categoría, unidad canónica, `minYears`, frecuencia objetivo.
- **Fuente/producto:** `id`, proveedor (Microsoft Planetary Computer o Meteomatics), colección/producto, variable nativa, unidad nativa, resolución, cobertura y método de acceso.
- **Región:** `id`, nombre, descripción, tipo (`predefined`/`custom`), bbox validado y CRS.
- **Observación:** `variableId`, `regionId`, `sourceProductId`, `periodStart`, `periodEnd`, `value`, `unit`, `quality`; clave única según esos identificadores y periodo.
- **Análisis:** `id`, referencias a variable/región/producto, intervalo, frecuencia, método y versión, `nObservations`, slope y unidad, p-value, significant, interpretación y `createdAt`.
- **Caché:** `cacheKey`, proveedor/producto, consulta normalizada, payload o referencia a observaciones, `fetchedAt`, `expiresAt` y versión del procesamiento.

En Firestore estas relaciones son IDs validados por la aplicación, no claves foráneas. En SQL conviene usar claves foráneas e índices por variable/región/fecha y clave de caché.

## Fuentes y catálogo inicial

- **Meteomatics:** considerar temperatura y precipitación; confirmar variables, unidades, frecuencia, disponibilidad histórica, autenticación y límites del plan contratado.
- **Microsoft Planetary Computer:** candidato para NDVI/productos MODIS; registrar Collection/STAC item, banda, escala, resolución y agregación espacial/temporal.
- **Giovanni:** mantener como posible vía de descubrimiento/consulta de productos NASA, no como fuente intercambiable hasta verificar API y términos. La propuesta de CO₂ requiere identificar dataset y endpoint concretos; no asumir que está disponible por el proveedor citado.

No presentar estos candidatos como integraciones terminadas. Habilitar una variable solo después de validar producto, cobertura mínima, licencia, transformaciones y unidad.

## Contrato HTTP propuesto

`GET /series?variableId=...&regionId=...&startDate=YYYY-MM-DD&endDate=YYYY-MM-DD`

Respuesta conceptual: `variable`, `region`, `source`, `unit`, `frequency`, `coverage`, `observations: [{date, value, quality}]`, `analysis: {method, slope, slopeUnit, pValue, significant, nObservations, interpretation}`. El API puede devolver análisis ausente con motivo cuando no se alcanza cobertura; no debe inventar puntos ni combinar fuentes sin declararlo.
