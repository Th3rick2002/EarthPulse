# TrendScope MVP

## Objetivo

Permitir que una persona elija una variable terrestre y una región, consulte su serie temporal mensual y entienda si presenta una tendencia lineal estadísticamente significativa.

## Recorrido principal

1. Elegir variable y región predefinidas; ofrecer un caso de demostración.
2. Consultar backend con variable, región y, cuando se habilite, intervalo temporal.
3. Mostrar globo 3D con la región, gráfico temporal y tarjeta de resultado.
4. Mostrar fuente, unidad, periodo, cobertura/calidad y mensaje claro si los datos no bastan.

## Responsabilidades

- **Frontend:** selector, globo, gráfico, veredicto, tooltips, estados de carga/error/sin datos y diseño adaptable a desktop/tablet.
- **Backend:** validar consulta y bbox, obtener datos, normalizar/resamplear mensualmente, evaluar cobertura, analizar tendencia y responder el contrato documentado.
- **Infra/integración:** configuración segura, despliegues, conectividad, CORS, observabilidad y coordinación del demo.

## Alcance MVP

- Hasta cinco regiones predefinidas y cuatro o cinco variables, priorizadas por disponibilidad de datos comprobada.
- Mínimo de cinco años para análisis; Mann-Kendall y pendiente lineal, umbral `p < 0.05`.
- Datos de Microsoft Planetary Computer y Meteomatics; validar producto, licencia, cobertura y método de acceso por variable antes de habilitarla.
- Caché con frescura objetivo de 24 horas.

## Fuera de alcance inicial

Tendencias no lineales, eliminación de ciclos estacionales, análisis estadísticos avanzados, autenticación compleja y regiones globales dibujadas libremente.

## Aceptación

La experiencia de pantalla, el orden de los resultados y los estados del frontend se definen en [UI/UX del MVP](ui-ux.md).

- Consulta completa frontend-backend para un ejemplo soportado y datos identificados por fuente/producto.
- El gráfico y veredicto representan el mismo intervalo y serie; unidades y pendiente son explícitas.
- Menos de cinco años o datos insuficientes producen un estado explicativo, sin fabricar un veredicto.
- Fallos de proveedor y ausencia de cobertura se muestran como errores recuperables, no como tendencia nula.
- Instrucciones locales existen en los README de ambas carpetas y configuración sensible queda fuera del repositorio.
