import { useState } from 'react'
import type { Region, SeriesQuery, Variable } from '../types/api'

// The v1 catalog does not expose supported variable/region pairs yet.
// Keep the MVP allowlist aligned with backend/app/data/catalog.py.
const MVP_REGION_IDS_BY_VARIABLE: Record<string, string[]> = {
  ndvi: ['amazon'],
  air_temperature: ['arctic'],
  precipitation: ['amazon'],
}

interface Props {
  variables: Variable[]
  regions: Region[]
  loading: boolean
  onAnalyze: (query: SeriesQuery) => void
  onRegionChange: (regionId: string) => void
}

function lastFullMonth(): string {
  const d = new Date()
  let y = d.getFullYear()
  let m = d.getMonth() // 0-based = mes anterior en 1-based
  if (m === 0) {
    y -= 1
    m = 12
  }
  return `${y}-${String(m).padStart(2, '0')}`
}

function defaultRange(minYears: number) {
  const endYear = new Date().getFullYear() - 1
  return { start: `${endYear - minYears + 1}-01`, end: `${endYear}-12` }
}

function monthsBetween(start: string, end: string): number {
  const [sy, sm] = start.split('-').map(Number)
  const [ey, em] = end.split('-').map(Number)
  return (ey - sy) * 12 + (em - sm) + 1
}

const toStartDate = (month: string) => `${month}-01`

function toEndDate(month: string): string {
  const [y, m] = month.split('-').map(Number)
  const last = new Date(Date.UTC(y, m, 0)).getUTCDate()
  return `${month}-${String(last).padStart(2, '0')}`
}

export default function QueryPanel({
  variables,
  regions,
  loading,
  onAnalyze,
  onRegionChange,
}: Props) {
  const [variableId, setVariableId] = useState(variables[0]?.variableId ?? '')
  const [regionId, setRegionId] = useState(() => {
    const allowedIds = MVP_REGION_IDS_BY_VARIABLE[variables[0]?.variableId ?? ''] ?? []
    return regions.find((region) => allowedIds.includes(region.regionId))?.regionId ?? ''
  })
  const [range, setRange] = useState(() =>
    defaultRange(variables[0]?.minYears ?? 5),
  )

  const variable = variables.find((v) => v.variableId === variableId)
  const supportedRegionIds = MVP_REGION_IDS_BY_VARIABLE[variableId] ?? []
  const availableRegions = regions.filter((region) =>
    supportedRegionIds.includes(region.regionId),
  )
  const minYears = variable?.minYears ?? 5

  let error: string | null = null
  if (!range.start || !range.end) {
    error = 'Selecciona el mes de inicio y de fin.'
  } else if (monthsBetween(range.start, range.end) <= 0) {
    error = 'El mes de inicio debe ser anterior al mes de fin.'
  } else if (monthsBetween(range.start, range.end) < minYears * 12) {
    error = `Esta variable requiere al menos ${minYears} años de datos.`
  }

  const canSubmit = !loading && !error && variableId !== '' && regionId !== ''

  function handleVariableChange(id: string) {
    setVariableId(id)
    const nextRegionIds = MVP_REGION_IDS_BY_VARIABLE[id] ?? []
    const nextRegions = regions.filter((region) =>
      nextRegionIds.includes(region.regionId),
    )
    const nextRegionId = nextRegions.some((region) => region.regionId === regionId)
      ? regionId
      : (nextRegions[0]?.regionId ?? '')
    setRegionId(nextRegionId)
    onRegionChange(nextRegionId)
    const next = variables.find((v) => v.variableId === id)
    const nextMin = next?.minYears ?? 5
    if (
      range.start &&
      range.end &&
      monthsBetween(range.start, range.end) < nextMin * 12
    ) {
      setRange(defaultRange(nextMin))
    }
  }

  function handleRegionChange(id: string) {
    setRegionId(id)
    onRegionChange(id)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!canSubmit) return
    onAnalyze({
      variableId,
      regionId,
      startDate: toStartDate(range.start),
      endDate: toEndDate(range.end),
    })
  }

  return (
    <section className="card" aria-labelledby="query-title">
      <h2 id="query-title">Consulta</h2>
      <form className="query-form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="variable">Variable</label>
          <select
            id="variable"
            value={variableId}
            onChange={(e) => handleVariableChange(e.target.value)}
          >
            {variables.map((v) => (
              <option key={v.variableId} value={v.variableId}>
                {v.name}
              </option>
            ))}
          </select>
          {variable && (
            <span className="field-help">
              {variable.description} ({variable.unit})
            </span>
          )}
        </div>

        <div className="field">
          <label htmlFor="region">Región</label>
          <select
            id="region"
            value={regionId}
            onChange={(e) => handleRegionChange(e.target.value)}
          >
            {availableRegions.map((r) => (
              <option key={r.regionId} value={r.regionId}>
                {r.name}
                {r.type === 'custom' ? ' (personalizada)' : ''}
              </option>
            ))}
          </select>
        </div>

        <div className="field">
          <label htmlFor="start">Desde (mes)</label>
          <input
            id="start"
            type="month"
            value={range.start}
            max={lastFullMonth()}
            onChange={(e) =>
              setRange((r) => ({ ...r, start: e.target.value }))
            }
          />
        </div>

        <div className="field">
          <label htmlFor="end">Hasta (mes)</label>
          <input
            id="end"
            type="month"
            value={range.end}
            max={lastFullMonth()}
            onChange={(e) => setRange((r) => ({ ...r, end: e.target.value }))}
          />
        </div>

        <button className="btn" type="submit" disabled={!canSubmit}>
          {loading ? 'Analizando…' : 'Analizar'}
        </button>

        {error && (
          <p className="form-error" role="alert">
            {error}
          </p>
        )}
      </form>
    </section>
  )
}
