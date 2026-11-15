# UI/UX del MVP

## Objetivo de la experiencia

Guiar a niñas, niños y personas adultas desde una pregunta sobre la Tierra hasta una explicación comprensible de lo que muestran las mediciones. La interfaz enseña qué se consulta, cómo leer el resultado y cuáles son sus límites sin exigir conocimientos de estadística.

## Decisiones de producto

- Toda la experiencia visible está en español claro. Los términos científicos se explican cuando aparecen; los detalles técnicos quedan disponibles en secciones ampliables.
- Hay una sola pantalla principal: **Explorador de la Tierra**.
- El estilo es luminoso, amable y científico, con controles grandes, contraste suficiente y texto directo, sin lenguaje infantilizado.
- La consulta se presenta como tres preguntas: qué observar, durante qué periodo y qué lugares comparar.
- La conclusión en lenguaje cotidiano aparece antes de la gráfica y los detalles estadísticos.
- No se simulan datos, porcentajes de progreso, etapas completadas ni resultados.

## Estructura de la pantalla

1. **Encabezado:** marca TrendScope y nombre “Explorador de la Tierra”; enlace para saltar al contenido.
2. **Introducción:** explica que la plataforma compara mediciones de la Tierra para buscar patrones.
3. **Consulta guiada:** “¿Qué quieres explorar?”, “¿Qué periodo quieres comparar?” y “¿Qué lugares quieres comparar?”.
4. **Mapa Leaflet:** teselas OpenStreetMap con atribución visible; permite dibujar hasta cuatro rectángulos independientes.
5. **Resultados:** una tarjeta por zona con conclusión sencilla, cobertura y gráfica mensual. La procedencia, unidades, periodo y coordenadas aparecen en un aside a la derecha.

En escritorio, los resultados ocupan la columna principal y la ficha de consulta queda en un aside a la derecha. En pantallas angostas, el aside se apila después de los resultados.

## Consulta y fechas

- Mostrar nombres familiares primero: “Vegetación vista desde satélite”, “Temperatura del aire” y “Lluvia acumulada”.
- Cada tema explica qué mide y en qué unidad. Acrónimos y productos aparecen en la procedencia o en una ayuda secundaria.
- Las fechas se eligen por mes y año, en meses completos inclusivos. El periodo permitido es de 1 a 50 años.
- El botón se bloquea mientras la consulta está en curso, si faltan zonas o si el intervalo no es válido.
- Cada rectángulo es una consulta independiente. Las series y tendencias se presentan por zona y no se combinan en un promedio común.

## Mapa y zonas

- Leaflet proporciona navegación y zoom táctil sobre teselas OpenStreetMap. La atribución requerida permanece visible.
- Se dibujan rectángulos con dos clics/toques en esquinas opuestas. Cada zona se puede nombrar y quitar; máximo cuatro por consulta.
- Cada rectángulo puede medir hasta 35° de ancho por 25° de alto para mantener manejable el costo de datos. El backend vuelve a validar este límite.
- El mapa muestra el área consultada, no valores dentro de ella. Cada punto de la gráfica resume el rectángulo completo.
- Las zonas son temporales a la consulta; no se agregan automáticamente al catálogo ni se guardan en la base de regiones.
- Nombre y coordenadas permanecen como texto accesible fuera del mapa; instrucciones y errores aparecen junto a sus controles.

## Resultados y explicación científica

- El resumen indica si los datos muestran aumento, disminución o si no hay evidencia suficiente para reconocer una tendencia.
- La pendiente se expresa con unidad por año y se explica como cambio promedio estimado.
- La significancia se explica como evidencia estadística; no implica causalidad. El valor p y Mann-Kendall están en una sección ampliable.
- Cada gráfica mensual muestra fechas en español, unidad en el eje y valor al explorar un punto. Los huecos siguen visibles y se explican como meses sin datos.
- El aside indica proveedor/fuente, unidad, periodo, coordenadas y zonas comparadas.
- Si `trendAnalysis` es null, se explica la cobertura disponible y el mínimo de un año. Si no hay observaciones, se invita a intentar otro periodo.

## Retroalimentación y errores

- **Inicio:** invita a elegir tema, periodo y zonas, sin resultados inventados.
- **Carga:** indica tema, periodo y nombres de zonas; informa el tiempo transcurrido. La animación es indeterminada porque el backend no comunica porcentajes ni etapas internas.
- **Resultado:** cada tarjeta confirma qué tema y zona representa.
- **Error de proveedor o conexión:** mensaje en español, acción para reintentar e ID de solicitud cuando exista.
- **Error de formulario:** explicación junto a los controles y valores preservados.

## Accesibilidad

- Controles con etiquetas persistentes, orden de teclado y foco visible.
- Mensajes de estado anunciados; no depender solo del color.
- Áreas táctiles amplias, diseño adaptable, contraste y respeto a `prefers-reduced-motion`.
- La selección del mapa también se comunica mediante nombres y coordenadas en texto.

## Criterio de aceptación UX

Una persona puede escoger un tema, un periodo válido y varias zonas; sabe qué se está consultando y espera con retroalimentación honesta. Después entiende qué indica cada resultado, cuántos datos se usaron, de dónde vienen y qué no puede concluirse.
