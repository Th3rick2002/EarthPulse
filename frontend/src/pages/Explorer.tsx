import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import QueryPanel from '../components/QueryPanel'
import VerdictCard from '../components/VerdictCard'
import { ApiError, asApiError, compareAreas, getVariables } from '../services/api'
import type { AreaSeriesResult, CompareSeriesQuery, Variable } from '../types/api'

const TimeSeriesChart = lazy(() => import('../components/TimeSeriesChart'))

type Catalog =
  | { status: 'loading' }
  | { status: 'error'; error: ApiError }
  | { status: 'ready'; variables: Variable[] }

type View =
  | { kind: 'idle' }
  | { kind: 'loading'; query: CompareSeriesQuery; startedAt: number }
  | { kind: 'error'; error: ApiError; query: CompareSeriesQuery }
  | { kind: 'ready'; results: AreaSeriesResult[]; query: CompareSeriesQuery }

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
      {error.diagnostic && (
        <details className="technical-details">
          <summary>Ver detalle técnico</summary>
          <p>{error.diagnostic}</p>
        </details>
      )}
      <button className="btn secondary" type="button" onClick={onRetry}>Intentar de nuevo</button>
    </div>
  )
}

export default function Explorer() {
  const [catalog, setCatalog] = useState<Catalog>({ status: 'loading' })
  const [reloadKey, setReloadKey] = useState(0)
  const [view, setView] = useState<View>({ kind: 'idle' })
  const [areas, setAreas] = useState<CompareSeriesQuery['areas']>([])
  const [elapsedSeconds, setElapsedSeconds] = useState(0)
  const modalRef = useRef<HTMLElement | null>(null)

  useEffect(() => {
    let cancelled = false
    getVariables()
      .then((variables) => {
        if (!cancelled) setCatalog({ status: 'ready', variables })
      })
      .catch((error) => {
        if (!cancelled) setCatalog({ status: 'error', error: asApiError(error) })
      })
    return () => { cancelled = true }
  }, [reloadKey])

  useEffect(() => {
    if (view.kind !== 'loading') return
    const update = () => setElapsedSeconds(Math.floor((Date.now() - view.startedAt) / 1000))
    update()
    const timer = window.setInterval(update, 1000)
    return () => window.clearInterval(timer)
  }, [view])

  useEffect(() => {
    if (view.kind !== 'loading') return
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    modalRef.current?.focus()
    return () => { document.body.style.overflow = previousOverflow }
  }, [view.kind])

  function retryCatalog() {
    setCatalog({ status: 'loading' })
    setReloadKey((key) => key + 1)
  }

  async function runQuery(query: CompareSeriesQuery) {
    setView({ kind: 'loading', query, startedAt: Date.now() })
    try {
      const results = await compareAreas(query)
      setView({ kind: 'ready', results, query })
    } catch (error) {
      setView({ kind: 'error', error: asApiError(error), query })
    }
  }

  if (catalog.status === 'loading') {
    return <div className="card state-box" role="status">Preparando el explorador…</div>
  }
  if (catalog.status === 'error') {
    return (
      <ErrorBox
        title="No pudimos preparar el catálogo"
        error={catalog.error}
        onRetry={retryCatalog}
      />
    )
  }
  if (catalog.variables.length === 0) {
    return <div className="card state-box"><h2>No hay temas disponibles</h2></div>
  }

  return (
    <>
      <QueryPanel
        variables={catalog.variables}
        areas={areas}
        loading={view.kind === 'loading'}
        onAnalyze={runQuery}
        onAreasChange={setAreas}
      />
      <div aria-live="polite" aria-atomic="false">
        {view.kind === 'idle' && (
          <div className="card state-box">
            <span className="state-illustration" aria-hidden="true">🌱</span>
            <h2>Compara lugares y descubre sus cambios</h2>
            <p>Después de dibujar las zonas y elegir un periodo, te mostraremos los datos de cada una por separado.</p>
          </div>
        )}
        {view.kind === 'error' && (
          <ErrorBox title="No pudimos completar la comparación" error={view.error} onRetry={() => runQuery(view.query)} />
        )}
        {view.kind === 'ready' && <ComparisonResults results={view.results} query={view.query} />}
      </div>
      {view.kind === 'loading' && (
        <div className="query-modal-backdrop">
          <section
            className="query-modal card"
            ref={modalRef}
            tabIndex={-1}
            role="dialog"
            aria-modal="true"
            aria-labelledby="query-progress-title"
            aria-describedby="query-progress-description"
            aria-live="polite"
            onKeyDown={(event) => {
              if (event.key === 'Tab') event.preventDefault()
            }}
          >
            <span className="loading-orbit" aria-hidden="true">🌎</span>
            <span className="eyebrow">COMPARACIÓN EN CURSO</span>
            <h2 id="query-progress-title">Buscando datos para {view.query.areas.length} {view.query.areas.length === 1 ? 'zona' : 'zonas'}</h2>
            <p><strong>{friendlyVariable(view.query.variableId)}</strong> · {formatDate(view.query.startDate)} a {formatDate(view.query.endDate)}</p>
            <p className="area-names-loading">{view.query.areas.map((area) => area.name).join(' · ')}</p>
            <p id="query-progress-description">Reunimos mediciones científicas para cada zona y luego comparamos los meses para buscar patrones.</p>
            <p className="progress-time">Tiempo transcurrido: {formatElapsed(elapsedSeconds)}</p>
            <p className="field-help">Las consultas largas pueden tardar un poco. Puedes esperar aquí; no hace falta volver a pulsar.</p>
            <div className="progress-track" aria-hidden="true"><span /></div>
          </section>
        </div>
      )}
    </>
  )
}

function ComparisonResults({ results, query }: { results: AreaSeriesResult[]; query: CompareSeriesQuery }) {
  const first = results[0]?.series
  if (!first) return <div className="card state-box"><h2>No recibimos resultados</h2><p>Intenta de nuevo con las mismas zonas.</p></div>

  const variable = first.variable
  return (
    <section className="comparison-layout" aria-labelledby="comparison-title">
      <div className="comparison-main">
        <div className="comparison-heading">
          <span className="eyebrow">RESULTADOS DE TU EXPLORACIÓN</span>
          <h2 id="comparison-title">{friendlyVariable(variable.variableId)} en {results.length} {results.length === 1 ? 'zona' : 'zonas'}</h2>
          <p>Revisamos cada rectángulo por separado, del {formatDate(query.startDate)} al {formatDate(query.endDate)}.</p>
        </div>
        {results.map((result, index) => (
          <AreaResult key={result.areaId} result={result} index={index} />
        ))}
      </div>
      <DataAside results={results} query={query} />
    </section>
  )
}

function AreaResult({ result, index }: { result: AreaSeriesResult; index: number }) {
  const { series } = result
  const observed = series.timeSeries.filter((point) => point.quality === 'ok').length
  const interpolated = series.timeSeries.filter((point) => point.quality === 'interpolated').length
  return (
    <article className="area-result">
      <div className="area-result-heading">
        <span className={`result-dot result-dot-${index % 4}`} aria-hidden="true" />
        <h3>{result.name}</h3>
      </div>
      {observed + interpolated === 0 ? (
        <div className="no-area-data">
          <h4>No encontramos mediciones en esta zona</h4>
          <p>Prueba con un rectángulo más pequeño o con otro periodo.</p>
        </div>
      ) : (
        <>
          <VerdictCard trend={series.trendAnalysis} variable={series.variable} observed={observed} interpolated={interpolated} total={series.timeSeries.length} />
          <Suspense fallback={<div className="chart-card card" role="status">Preparando la gráfica…</div>}>
            <TimeSeriesChart
              points={series.timeSeries}
              unit={friendlyUnit(series.variable.unit)}
              variableName={friendlyVariable(series.variable.variableId)}
              areaName={result.name}
            />
          </Suspense>
        </>
      )}
    </article>
  )
}

function DataAside({ results, query }: { results: AreaSeriesResult[]; query: CompareSeriesQuery }) {
  const variable = results[0].series.variable
  return (
    <aside className="data-aside card" aria-labelledby="data-aside-title">
      <span className="eyebrow">FICHA DE LA CONSULTA</span>
      <h2 id="data-aside-title">¿De dónde vienen los datos?</h2>
      <p className="metadata-intro">La plataforma reúne mediciones científicas y calcula un valor mensual para cada zona.</p>
      <dl className="meta meta-aside">
        <div><dt>Tema</dt><dd>{friendlyVariable(variable.variableId)}</dd></div>
        <div><dt>Fuente</dt><dd>{friendlySource(variable.source)}</dd></div>
        <div><dt>Unidad</dt><dd>{friendlyUnit(variable.unit)}</dd></div>
        <div><dt>Periodo</dt><dd>{formatDate(query.startDate)} a {formatDate(query.endDate)}</dd></div>
      </dl>
      <h3 className="aside-subtitle">Zonas comparadas</h3>
      <ul className="aside-area-list">
        {results.map((result) => (
          <li key={result.areaId}>
            <strong>{result.name}</strong>
            <span>{formatBBox(result.series.region.bbox)}</span>
          </li>
        ))}
      </ul>
      <p className="aside-note">Cada resultado resume su rectángulo completo. El mapa no representa diferencias dentro de esa zona.</p>
    </aside>
  )
}

function formatBBox(bbox: AreaSeriesResult['series']['region']['bbox']) {
  const coordinate = (value: number) => value.toLocaleString('es-SV', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
  return `${coordinate(bbox.latMin)}°–${coordinate(bbox.latMax)}° lat. · ${coordinate(bbox.lonMin)}°–${coordinate(bbox.lonMax)}° lon.`
}

function friendlyVariable(id: string) {
  return ({ ndvi: 'Vegetación (NDVI)', air_temperature: 'Temperatura del aire', precipitation: 'Lluvia' } as Record<string, string>)[id] ?? id
}

function friendlyUnit(unit: string) {
  return unit === 'index' ? 'índice NDVI' : unit
}

function friendlySource(source: string) {
  if (source.toLowerCase().includes('planetary')) return 'Satélite MODIS, disponible en Microsoft Planetary Computer'
  if (source.toLowerCase().includes('meteomatics')) return 'Meteomatics (datos meteorológicos y de lluvia)'
  return source
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-SV', { month: 'long', year: 'numeric', timeZone: 'UTC' })
    .format(new Date(`${value.slice(0, 7)}-01T00:00:00Z`))
}

function formatElapsed(seconds: number) {
  const minutes = Math.floor(seconds / 60)
  const remaining = seconds % 60
  return minutes > 0 ? `${minutes} min ${String(remaining).padStart(2, '0')} s` : `${remaining} s`
}
