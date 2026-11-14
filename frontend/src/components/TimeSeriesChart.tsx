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
}

export default function TimeSeriesChart({ points, unit, variableName }: Props) {
  const data = points.map((p) => ({
    date: p.date.slice(0, 7),
    value: p.quality === 'missing' ? null : p.value,
  }))

  return (
    <section className="card wide" aria-labelledby="chart-title">
      <h2 id="chart-title">Serie temporal mensual: {variableName}</h2>
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
      <p className="caption">Los huecos en la línea indican meses sin dato.</p>
    </section>
  )
}