import type { TrendAnalysis, Variable } from '../types/api'

interface Props {
  trend: TrendAnalysis | null
  variable: Variable
  observed: number
  interpolated: number
  total: number
}

const fmt = (n: number, digits = 3) =>
  n.toLocaleString('es-SV', { maximumSignificantDigits: digits })

export default function VerdictCard({ trend, variable, observed, interpolated, total }: Props) {
  const coverage = total === 0 ? 0 : Math.round((observed / total) * 100)
  const direction = !trend || trend.slope === 0 ? 'sin un cambio claro' : trend.slope > 0 ? 'ha aumentado' : 'ha disminuido'
  const subject = variable.variableId === 'ndvi'
    ? 'La vegetación'
    : variable.variableId === 'air_temperature'
      ? 'La temperatura del aire'
      : variable.variableId === 'precipitation'
        ? 'La lluvia'
        : variable.name
  const unit = variable.unit === 'index' ? (variable.variableId === 'ndvi' ? 'índice NDVI' : 'índice') : variable.unit
  const title = trend?.significant
    ? `${subject} ${direction}`
    : trend
      ? `Sin señal clara de cambio en ${subject.toLocaleLowerCase('es-SV')}`
      : 'Aún no hay suficientes datos para descubrir una tendencia'

  return (
    <section className={`card verdict ${trend?.significant ? 'ok' : 'neutral'}`} aria-labelledby="verdict-title">
      <span className="eyebrow">LO QUE NOS CUENTAN LOS DATOS</span>
      <h2 id="verdict-title">
        {title}
      </h2>
      {trend ? (
        <>
          <p className="verdict-summary">
            {trend.significant
              ? 'El patrón es suficientemente claro en este periodo según la prueba estadística.'
              : 'Los datos no muestran una señal suficientemente clara para confirmar una tendencia. Eso no demuestra que nada haya cambiado.'}
          </p>
          <p className="verdict-slope">
            {trend.slope > 0 ? '+' : ''}{fmt(trend.slope)} {unit} por año
            <span> es el cambio promedio estimado.</span>
          </p>
          <details className="technical-details">
            <summary>¿Cómo sabemos si la tendencia es clara?</summary>
            <p>
              Comparamos el orden de las mediciones con la prueba Mann-Kendall.
              El valor p es {trend.pValue < 0.001 ? 'menor que 0,001' : fmt(trend.pValue)};
              consideramos que hay evidencia estadística cuando es menor que 0,05.
              Esto ayuda a detectar patrones, pero no explica por qué ocurren.
            </p>
            <dl className="verdict-stats">
              <div><dt>Periodo</dt><dd>{formatDate(trend.startDate)} a {formatDate(trend.endDate)}</dd></div>
              <div><dt>Meses con datos</dt><dd>{observed} de {total} meses con observaciones válidas ({coverage}%)</dd></div>
              {interpolated > 0 && <div><dt>Meses estimados</dt><dd>{interpolated}</dd></div>}
              <div><dt>Prueba</dt><dd>Mann-Kendall</dd></div>
            </dl>
            <p className="disclaimer">Una tendencia muestra un patrón en los datos; por sí sola no demuestra qué lo causó.</p>
          </details>
        </>
      ) : (
        <>
          <p className="verdict-summary">
            Encontramos mediciones para {observed} de {total} meses ({coverage}%).
            Para analizar una tendencia necesitamos al menos {variable.minYears} años y datos suficientes a lo largo del periodo.
          </p>
          <p className="field-help">Prueba a ampliar las fechas o elegir otra región.</p>
        </>
      )}
    </section>
  )
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-SV', { month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(`${value.slice(0, 7)}-01T00:00:00Z`))
}
