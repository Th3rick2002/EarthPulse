import type { TrendAnalysis, Variable } from '../types/api'

interface Props {
  trend: TrendAnalysis | null
  variable: Variable
}

const fmt = (n: number, digits = 3) =>
  n.toLocaleString('es', { maximumSignificantDigits: digits })

export default function VerdictCard({ trend, variable }: Props) {
  if (!trend) {
    return (
      <section className="card verdict neutral" aria-labelledby="verdict-title">
        <h2 id="verdict-title">Veredicto</h2>
        <span className="badge">● Cobertura insuficiente</span>
        <p>
          No hay suficientes observaciones válidas para calcular una tendencia.
          Se requieren al menos {variable.minYears} años de cobertura. Puedes
          ampliar el intervalo o probar con otra región.
        </p>
      </section>
    )
  }

  const direction =
    trend.slope > 0 ? 'creciente' : trend.slope < 0 ? 'decreciente' : 'sin cambio'
  const arrow = trend.slope > 0 ? '▲' : trend.slope < 0 ? '▼' : '■'
  const variant = trend.significant ? 'ok' : 'warn'
  const sign = trend.slope > 0 ? '+' : ''
  const pText = trend.pValue < 0.001 ? '< 0,001' : fmt(trend.pValue)

  return (
    <section className={`card verdict ${variant}`} aria-labelledby="verdict-title">
      <h2 id="verdict-title">Veredicto</h2>
      <span className="badge">
        {arrow}{' '}
        {trend.significant
          ? `Tendencia ${direction} significativa`
          : `Tendencia ${direction} no significativa`}
      </span>
      <p>{trend.interpretation}</p>

      <dl className="verdict-stats">
        <div>
          <dt>Pendiente</dt>
          <dd>
            {sign}
            {fmt(trend.slope)} {variable.unit} por año
          </dd>
        </div>
        <div>
          <dt>p-value (Mann-Kendall)</dt>
          <dd>{pText}</dd>
        </div>
        <div>
          <dt>Periodo</dt>
          <dd>
            {trend.startDate} a {trend.endDate}
          </dd>
        </div>
        <div>
          <dt>Umbral</dt>
          <dd>p &lt; 0,05</dd>
        </div>
      </dl>

      <p className="disclaimer">
        Significancia estadística indica evidencia de una tendencia lineal en
        estos datos; no implica causalidad.
      </p>
    </section>
  )
}