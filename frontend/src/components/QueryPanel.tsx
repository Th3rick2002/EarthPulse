import { lazy, Suspense, useEffect, useState } from 'react'
import { ApiError, asApiError, getVariableAvailability } from '../services/api'
import type { CompareSeriesQuery, SelectedArea, Variable, VariableAvailability } from '../types/api'

const RegionMap = lazy(() => import('./RegionMap'))

const VARIABLE_COPY: Record<string, { title: string; help: string }> = {
  ndvi: {
    title: 'Vegetación vista desde satélite',
    help: 'El satélite observa qué tan verde está la vegetación. Usamos el índice NDVI, con valores de −1 a 1.',
  },
  air_temperature: {
    title: 'Temperatura del aire',
    help: 'Revisamos cómo cambia la temperatura del aire cerca de la superficie.',
  },
  precipitation: {
    title: 'Lluvia acumulada',
    help: 'Sumamos la lluvia de cada mes para ver cómo cambia con los años.',
  },
}

const UNIT_NAMES: Record<string, string> = { index: 'índice' }

interface Props {
  variables: Variable[]
  areas: SelectedArea[]
  loading: boolean
  onAnalyze: (query: CompareSeriesQuery) => void
  onAreasChange: (areas: SelectedArea[]) => void
}

function lastFullMonth(): string {
  const d = new Date()
  let y = d.getFullYear()
  let m = d.getMonth()
  if (m === 0) {
    y -= 1
    m = 12
  }
  return `${y}-${String(m).padStart(2, '0')}`
}

function defaultRange() {
  const end = lastFullMonth()
  const [year, month] = end.split('-').map(Number)
  const start = new Date(Date.UTC(year, month - 1 - 11, 1))
  return {
    start: `${start.getUTCFullYear()}-${String(start.getUTCMonth() + 1).padStart(2, '0')}`,
    end,
  }
}

function monthsBetween(start: string, end: string): number {
  if (!start || !end) return 0
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

export default function QueryPanel({ variables, areas, loading, onAnalyze, onAreasChange }: Props) {
  const [variableId, setVariableId] = useState(variables[0]?.variableId ?? '')
  const [range, setRange] = useState(defaultRange)
  const [availability, setAvailability] = useState<
    | { variableId: string; status: 'loading' }
    | { variableId: string; status: 'ready'; dates: VariableAvailability }
    | { variableId: string; status: 'error'; error: ApiError }
  >({ variableId: '', status: 'loading' })
  const variable = variables.find((item) => item.variableId === variableId)
  const precipitation = variableId === 'precipitation'
  const currentAvailability = availability.variableId === variableId ? availability : null
  const availabilityLoading = precipitation && (!currentAvailability || currentAvailability.status === 'loading')
  const latestAvailableMonth = precipitation && currentAvailability?.status === 'ready'
    ? currentAvailability.dates.availableEndDate.slice(0, 7)
    : lastFullMonth()
  const earliestAvailableMonth = precipitation && currentAvailability?.status === 'ready'
    ? currentAvailability.dates.availableStartDate.slice(0, 7)
    : undefined
  const monthCount = monthsBetween(range.start, range.end)
  let error: string | null = null
  if (availabilityLoading) {
    error = 'Consultando hasta qué mes hay datos de lluvia…'
  } else if (precipitation && currentAvailability?.status === 'error') {
    error = 'No pudimos consultar la disponibilidad de lluvia. Inténtalo de nuevo en un momento.'
  } else if (!range.start || !range.end) {
    error = 'Elige el primer y el último mes del periodo.'
  } else if (monthCount < 12) {
    error = 'El periodo debe tener al menos 1 año para comparar los cambios.'
  } else if (monthCount > 600) {
    error = 'El periodo no puede superar los 50 años.'
  } else if (range.end > latestAvailableMonth) {
    error = precipitation
      ? `La lluvia está disponible hasta ${formatMonth(latestAvailableMonth)}. Elige un mes anterior.`
      : 'Elige un periodo que termine en un mes completo.'
  } else if (earliestAvailableMonth && range.start < earliestAvailableMonth) {
    error = `La lluvia está disponible desde ${formatMonth(earliestAvailableMonth)}.`
  } else if (areas.length === 0) {
    error = 'Dibuja al menos una zona en el mapa.'
  }

  const canSubmit = !loading && !error && variableId !== ''

  useEffect(() => {
    if (!precipitation) return

    let cancelled = false
    getVariableAvailability(variableId)
      .then((dates) => {
        if (cancelled) return
        setAvailability({ variableId, status: 'ready', dates })
        const maxMonth = dates.availableEndDate.slice(0, 7)
        setRange((current) => {
          if (current.end <= maxMonth) return current
          const adjustedStart = current.start > maxMonth
            ? shiftMonth(maxMonth, -11)
            : current.start
          return { start: adjustedStart, end: maxMonth }
        })
      })
      .catch((cause) => {
        if (!cancelled) setAvailability({ variableId, status: 'error', error: asApiError(cause) })
      })
    return () => { cancelled = true }
  }, [precipitation, variableId])

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!canSubmit) return
    onAnalyze({
      variableId,
      areas,
      startDate: toStartDate(range.start),
      endDate: toEndDate(range.end),
    })
  }

  function addArea(bbox: SelectedArea['bbox']) {
    const nextNumber = areas.length + 1
    onAreasChange([
      ...areas,
      { areaId: `zona-${crypto.randomUUID()}`, name: `Zona ${nextNumber}`, bbox },
    ])
  }

  function renameArea(areaId: string, name: string) {
    onAreasChange(areas.map((area) => area.areaId === areaId ? { ...area, name } : area))
  }

  return (
    <section className="card query-card" aria-labelledby="query-title">
      <div className="query-intro">
        <span className="eyebrow">EXPLORADOR DE LA TIERRA</span>
        <h1 id="query-title">Descubre cómo cambian distintos lugares</h1>
        <p>Elige qué observar, dibuja una o varias zonas y compara lo que cuentan las mediciones.</p>
      </div>
      <form className="query-form" onSubmit={handleSubmit}>
        <fieldset className="query-step">
          <legend><span className="step-number">1</span> ¿Qué quieres explorar?</legend>
          <div className="field">
            <label htmlFor="variable">Elige un tema de la Tierra</label>
            <select id="variable" value={variableId} disabled={loading} onChange={(event) => setVariableId(event.target.value)}>
              {variables.map((item) => (
                <option key={item.variableId} value={item.variableId}>
                  {VARIABLE_COPY[item.variableId]?.title ?? item.name}
                </option>
              ))}
            </select>
            {variable && (
              <span className="field-help">
                {VARIABLE_COPY[variable.variableId]?.help ?? `${variable.description} Se mide en ${UNIT_NAMES[variable.unit] ?? variable.unit}.`}
              </span>
            )}
          </div>
        </fieldset>

        <fieldset className="query-step query-step-period">
          <legend><span className="step-number">2</span> ¿Qué periodo quieres comparar?</legend>
          <p className="step-help">Elige entre 1 y 50 años. Comparamos meses completos y usamos el mismo periodo para todas las zonas.</p>
          {precipitation && currentAvailability?.status === 'ready' && (
            <p className="availability-note" role="status">
              Los datos de lluvia se publican con retraso. El último mes completo disponible es {formatMonth(latestAvailableMonth)}.
            </p>
          )}
          <div className="period-fields">
            <div className="field">
              <label htmlFor="start">Desde (mes y año)</label>
              <input id="start" type="month" value={range.start} min={earliestAvailableMonth} max={range.end || lastFullMonth()} disabled={loading} onChange={(event) => setRange((current) => ({ ...current, start: event.target.value }))} />
            </div>
            <div className="field">
              <label htmlFor="end">Hasta (mes y año)</label>
              <input id="end" type="month" value={range.end} min={range.start} max={precipitation ? latestAvailableMonth : lastFullMonth()} disabled={loading} onChange={(event) => setRange((current) => ({ ...current, end: event.target.value }))} />
            </div>
          </div>
          <p className="period-count" aria-live="polite">
            {monthCount > 0 ? `${(monthCount / 12).toLocaleString('es-SV', { maximumFractionDigits: 1 })} ${monthCount === 12 ? 'año seleccionado' : 'años seleccionados'}` : 'Selecciona ambos meses'}
          </p>
        </fieldset>

        <fieldset className="query-step map-step">
          <legend><span className="step-number">3</span> ¿Qué lugares quieres comparar?</legend>
          <Suspense fallback={<div className="leaflet-map-shell map-loading" role="status">Cargando el mapa…</div>}>
            <RegionMap
              areas={areas}
              onAddArea={addArea}
              onRemoveArea={(areaId) => onAreasChange(areas.filter((area) => area.areaId !== areaId))}
              onRenameArea={renameArea}
              disabled={loading}
            />
          </Suspense>
        </fieldset>

        <div className="query-action">
          <button className="btn" type="submit" disabled={!canSubmit} aria-describedby={error ? 'query-form-error' : undefined}>
            {loading ? 'Buscando datos…' : areas.length > 1 ? 'Comparar zonas' : 'Ver qué ha cambiado'}
          </button>
          <span>Analizamos cada zona por separado, sin mezclar sus mediciones.</span>
        </div>
        {error && <p id="query-form-error" className="form-error" role="alert">{error}</p>}
      </form>
    </section>
  )
}

function formatMonth(value: string) {
  return new Intl.DateTimeFormat('es-SV', { month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(`${value}-01T00:00:00Z`))
}

function shiftMonth(value: string, offset: number) {
  const [year, month] = value.split('-').map(Number)
  const shifted = new Date(Date.UTC(year, month - 1 + offset, 1))
  return `${shifted.getUTCFullYear()}-${String(shifted.getUTCMonth() + 1).padStart(2, '0')}`
}
