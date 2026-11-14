import { useEffect, useState } from 'react'
import Globe3D from '../components/Globe3D'
import QueryPanel from '../components/QueryPanel'
import TimeSeriesChart from '../components/TimeSeriesChart'
import VerdictCard from '../components/VerdictCard'
import { ApiError, asApiError, getRegions, getSeries, getVariables } from '../services/api'
import type { Region, SeriesData, SeriesQuery, Variable } from '../types/api'

type Catalog =
  | { status: 'loading' }
  | { status: 'error'; error: ApiError }
  | { status: 'ready'; variables: Variable[]; regions: Region[] }

type View =
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'error'; error: ApiError; query: SeriesQuery }
  | { kind: 'ready'; data: SeriesData; query: SeriesQuery }

function ErrorBox({
  title,
  error,
  onRetry,
}: {
  title: string
  error: ApiError
  onRetry: () => void
}) {
  return (
    <div className="card state-box error" role="alert">
      <h2>{title}</h2>
      <p>{error.message}</p>
      {error.requestId && <p className="caption">ID de solicitud: {error.requestId}</p>}
      <button className="btn secondary" type="button" onClick={onRetry}>
        Reintentar
      </button>
    </div>
  )
}

export default function Explorer() {
  const [catalog, setCatalog] = useState<Catalog>({ status: 'loading' })
  const [reloadKey, setReloadKey] = useState(0)
  const [view, setView] = useState<View>({ kind: 'idle' })
  const [previewRegionId, setPreviewRegionId] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([getVariables(), getRegions()])
      .then(([variables, regions]) => {
        if (!cancelled) setCatalog({ status: 'ready', variables, regions })
      })
      .catch((e) => {
        if (!cancelled) setCatalog({ status: 'error', error: asApiError(e) })
      })
    return () => {
      cancelled = true
    }
  }, [reloadKey])

  function retryCatalog() {
    setCatalog({ status: 'loading' })
    setReloadKey((k) => k + 1)
  }

  async function runQuery(query: SeriesQuery) {
    setView({ kind: 'loading' })
    try {
      const data = await getSeries(query)
      setView({ kind: 'ready', data, query })
    } catch (e) {
      setView({ kind: 'error', error: asApiError(e), query })
    }
  }

  if (catalog.status === 'loading') {
    return (
      <div className="card state-box" role="status">
        Cargando catálogo…
      </div>
    )
  }
  if (catalog.status === 'error') {
    return (
      <ErrorBox
        title="No se pudo cargar el catálogo"
        error={catalog.error}
        onRetry={retryCatalog}
      />
    )
  }
  if (catalog.variables.length === 0 || catalog.regions.length === 0) {
    return (
      <div className="card state-box">
        <h2>Catálogo vacío</h2>
        <p>El backend no devolvió variables o regiones disponibles.</p>
      </div>
    )
  }

  const { variables, regions } = catalog
  const previewRegion =
    regions.find((r) => r.regionId === previewRegionId) ?? regions[0]
  // Con resultado, el globo muestra la región de esa misma respuesta.
  const globeRegion = view.kind === 'ready' ? view.data.region : previewRegion

  return (
    <>
      <QueryPanel
        variables={variables}
        regions={regions}
        loading={view.kind === 'loading'}
        onAnalyze={runQuery}
        onRegionChange={setPreviewRegionId}
      />

      <div aria-live="polite">
        {view.kind === 'idle' && (
          <div className="card state-box">
            <h2>Elige una variable y una región</h2>
            <p>Luego pulsa «Analizar» para ver la serie y su tendencia.</p>
          </div>
        )}

        {view.kind === 'loading' && (
          <div className="card state-box" role="status">
            <h2>Analizando…</h2>
            <p>Consultando datos y calculando la tendencia. Puede tardar unos segundos.</p>
          </div>
        )}

        {view.kind === 'error' && (
          <ErrorBox
            title="No se pudo completar la consulta"
            error={view.error}
            onRetry={() => runQuery(view.query)}
          />
        )}

        {view.kind === 'ready' && <Results data={view.data} query={view.query} />}
      </div>

      {view.kind !== 'ready' && (
        <div className="results-grid">
          <Globe3D region={globeRegion} />
        </div>
      )}
    </>
  )
}

function Results({ data, query }: { data: SeriesData; query: SeriesQuery }) {
  const { variable, region, timeSeries, trendAnalysis } = data
  const total = timeSeries.length
  const ok = timeSeries.filter((p) => p.quality === 'ok').length
  const interpolated = timeSeries.filter((p) => p.quality === 'interpolated').length

  if (ok + interpolated === 0) {
    return (
      <div className="card state-box">
        <h2>Sin observaciones</h2>
        <p>
          No hay datos para {variable.name} en {region.name} durante este
          intervalo. Prueba con otra región o ajusta las fechas.
        </p>
      </div>
    )
  }

  return (
    <div className="results-grid">
      <Globe3D region={region} />
      <VerdictCard trend={trendAnalysis} variable={variable} />
      <TimeSeriesChart
        points={timeSeries}
        unit={variable.unit}
        variableName={variable.name}
      />
      <section className="card wide" aria-labelledby="meta-title">
        <h2 id="meta-title">Datos de la consulta</h2>
        <dl className="meta">
          <div>
            <dt>Fuente</dt>
            <dd>{variable.source}</dd>
          </div>
          <div>
            <dt>Unidad</dt>
            <dd>{variable.unit}</dd>
          </div>
          <div>
            <dt>Intervalo</dt>
            <dd>
              {query.startDate} a {query.endDate}
            </dd>
          </div>
          <div>
            <dt>Cobertura</dt>
            <dd>
              {ok} de {total} meses con dato observado
              {interpolated > 0 ? ` (+${interpolated} interpolados)` : ''}
            </dd>
          </div>
        </dl>
      </section>
    </div>
  )
}
