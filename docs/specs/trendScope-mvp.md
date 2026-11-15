# TrendScope MVP

## Objetivo

Permitir que una persona elija una variable terrestre y una región, consulte su serie temporal mensual y entienda si presenta una tendencia lineal estadísticamente significativa.

## Recorrido principal

1. Elegir una variable, el intervalo mensual y una o varias zonas rectangulares en el mapa.
2. Consultar backend por variable, fechas y bbox de cada zona.
3. Mostrar un resultado independiente por rectángulo, con mapa, gráfico temporal y tarjeta de resultado.
4. Mostrar fuente, unidad, periodo, cobertura/calidad y mensaje claro si los datos no bastan.

## Responsabilidades

- **Frontend:** selector, globo, gráfico, veredicto, tooltips, estados de carga/error/sin datos y diseño adaptable a desktop/tablet.
- **Backend:** validar consulta y bbox, obtener datos, normalizar/resamplear mensualmente, evaluar cobertura, analizar tendencia y responder el contrato documentado.
- **Infra/integración:** configuración segura, despliegues, conectividad, CORS, observabilidad y coordinación del demo.

## Alcance MVP

- Zonas temporales dibujadas en el mapa; hasta cuatro rectángulos independientes por consulta, además del catálogo de regiones predefinidas.
- Periodos completos de 1 a 50 años; Mann-Kendall y pendiente lineal, umbral `p < 0.05`.
- Datos de Microsoft Planetary Computer y Meteomatics; validar producto, licencia, cobertura y método de acceso por variable antes de habilitarla.
- Caché con frescura objetivo de 24 horas.

## Fuera de alcance inicial

Tendencias no lineales, eliminación de ciclos estacionales, análisis estadísticos avanzados, autenticación compleja y zonas globales sin límite de tamaño.

## Aceptación

La experiencia de pantalla, el orden de los resultados y los estados del frontend se definen en [UI/UX del MVP](ui-ux.md).

- Consulta completa frontend-backend para un ejemplo soportado y datos identificados por fuente/producto.
- El gráfico y veredicto representan el mismo intervalo y serie; unidades y pendiente son explícitas.
- Menos de un año, más de cincuenta años o datos insuficientes producen un estado explicativo, sin fabricar un veredicto.
- Fallos de proveedor y ausencia de cobertura se muestran como errores recuperables, no como tendencia nula.
- Instrucciones locales existen en los README de ambas carpetas y configuración sensible queda fuera del repositorio.
