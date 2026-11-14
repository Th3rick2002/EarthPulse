# UI/UX del MVP

## Objetivo de la experiencia

Guiar a la persona desde la selección de una variable y una región hasta la lectura de la serie y su tendencia, mostrando fuente, unidad, cobertura y límites estadísticos en el mismo flujo.

## Decisiones de producto

- La interfaz del MVP está en español.
- Hay una sola pantalla principal: **Explorador**. No se añade dashboard ni navegación entre módulos.
- El diseño usa tema claro y una estética científica sobria; se priorizan legibilidad y contraste sobre elementos decorativos.
- Los controles de consulta aparecen arriba y los resultados debajo.
- No se presentan métricas o tendencias antes de recibir una respuesta válida del backend.

## Estructura de la pantalla

1. **Barra superior:** marca TrendScope y nombre de la pantalla Explorador.
2. **Panel de consulta:** variable, región, intervalo mensual y acción **Analizar** en una franja compacta. Las opciones de región y variable se limitan a combinaciones disponibles en el catálogo.
3. **Resultados en escritorio/tablet:** globo 3D a la izquierda y veredicto a la derecha; gráfica temporal a todo el ancho debajo.
4. **Metadatos de la consulta:** fuente/producto, unidad, intervalo y cobertura se mantienen visibles junto a los resultados.

En pantallas angostas, el panel de consulta se apila y los resultados siguen este orden: globo, veredicto y gráfica. Los controles conservan sus etiquetas visibles y se pueden usar con teclado y pantalla táctil.

## Consulta

- El rango usa fechas ISO inclusivas y meses completos, según el contrato API.
- El frontend inicializa el intervalo con meses completos y al menos el `minYears` de la variable seleccionada; la persona puede cambiarlo si sigue siendo válido.
- **Analizar** permanece deshabilitado mientras haya campos requeridos vacíos o el rango no sea válido.
- Al enviar se consultan los endpoints del backend y se muestra estado de carga. No se simulan datos en la experiencia conectada.
- El catálogo limita las opciones a pares soportados; una variable no debe ofrecer regiones sin datos habilitados.

## Globo, gráfica y veredicto

- El globo 3D sitúa y resalta el bbox de la región elegida. Permite rotación y zoom básicos; la selección de la región sigue controlándose desde el panel.
- La gráfica representa `timeSeries` por fecha mensual, conserva huecos para valores null/missing y muestra valor y unidad al explorar un punto.
- El veredicto comunica la dirección, pendiente por año y unidad, significancia, p-value, periodo e interpretación de `trendAnalysis`.
- La significancia se explica como evidencia estadística, no como causalidad. El color nunca es la única forma de distinguir dirección o significancia.
- Si `trendAnalysis` es null, se muestra el motivo de cobertura insuficiente en vez de una tarjeta estadística vacía.

## Regiones personalizadas

- La acción **Agregar región** expande un formulario dentro del panel de consulta.
- El formulario solicita nombre, descripción y bbox mediante latitud/longitud mínima y máxima; no permite dibujar polígonos libremente.
- Se muestra una vista previa del bbox en el globo antes de guardar. El backend valida y asigna el ID.
- Tras una respuesta exitosa, la región aparece en el selector marcada como personalizada y puede consultarse como una predefinida.
- Los errores de validación se muestran junto al formulario y no crean una región local ficticia.

## Estados de interacción

- **Inicial:** controles disponibles y mensaje breve que invita a seleccionar datos; sin gráfica ni veredicto inventados.
- **Carga:** acción bloqueada para evitar duplicados y señal de progreso junto al área de resultados.
- **Resultado:** globo, veredicto, gráfica y metadatos corresponden a la misma respuesta e intervalo.
- **Cobertura insuficiente:** se conserva la serie disponible, se explica qué cobertura falta y se omite la tendencia.
- **Sin observaciones:** estado vacío explícito con opción de ajustar región o intervalo.
- **Error API/proveedor:** mensaje comprensible y acción para reintentar; no se reemplaza silenciosamente por datos sintéticos.
- **Error de formulario:** mensaje junto al campo inválido, conservando los valores ingresados.

## Criterio de aceptación UX

Una persona puede escoger un par soportado, solicitar un intervalo mensual válido y entender en una pantalla qué región y variable consultó, qué muestran los datos, cuál es la fuente y si existe evidencia estadística suficiente. La vista funciona en escritorio, tablet y móvil sin perder etiquetas, unidades ni estados de error/faltantes.
