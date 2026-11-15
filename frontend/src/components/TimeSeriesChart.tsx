import { useId } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { TimeSeriesPoint } from '../types/api'

interface Props {
  points: TimeSeriesPoint[]
  unit: string
  variableName: string
  areaName?: string
}

export default function TimeSeriesChart({ points, unit, variableName, areaName }: Props) {
  const chartTitleId = useId()
  const data = points.map((p) => ({
    date: formatMonth(p.date),
    value: p.quality === 'missing' ? null : p.value,
  }))

  return (
    <section className="card chart-card" aria-labelledby={chartTitleId}>
      <span className="eyebrow">MES A MES</span>
      <h2 id={chartTitleId}>Así cambió {variableName.toLowerCase()}{areaName ? ` en ${areaName}` : ''}</h2>
      <p className="chart-intro">Cada punto resume las mediciones de un mes en la región elegida. Toca o apunta a un punto para ver su valor.</p>
      <div
        role="img"
        aria-label={`Gráfica de ${variableName} por mes, en ${unit}`}
        style={{ width: '100%', height: 320 }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e9ef" />
            <XAxis dataKey="date" minTickGap={40} tick={{ fontSize: 12 }} />
            <YAxis
              width={64}
              tick={{ fontSize: 12 }}
              label={{
                value: unit,
                angle: -90,
                position: 'insideLeft',
                style: { textAnchor: 'middle' },
              }}
            />
            <Tooltip
              formatter={(v) =>
                typeof v === 'number' ? `${v.toFixed(3)} ${unit}` : 'sin dato'
              }
              labelFormatter={(l) => `Mes: ${String(l)}`}
            />
            <Line
              type="monotone"
              dataKey="value"
              name={variableName}
              stroke="#0b5fa5"
              strokeWidth={2}
              dot={false}
              connectNulls={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="caption">Un espacio en la línea significa que no encontramos datos para ese mes. El eje vertical muestra {unit}.</p>
    </section>
  )
}

function formatMonth(value: string) {
  return new Intl.DateTimeFormat('es-SV', { month: 'short', year: '2-digit', timeZone: 'UTC' })
    .format(new Date(`${value.slice(0, 7)}-01T00:00:00Z`))
}
