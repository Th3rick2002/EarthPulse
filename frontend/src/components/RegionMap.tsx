import { useState } from 'react'
import { CircleMarker, MapContainer, Rectangle, TileLayer, Tooltip, useMapEvents } from 'react-leaflet'
import type { LatLngTuple } from 'leaflet'
import type { BBox, SelectedArea } from '../types/api'

const MAX_AREAS = 4
const COLORS = ['#6b45a2', '#167c70', '#c26d28', '#2674a8']

interface Props {
  areas: SelectedArea[]
  onAddArea: (bbox: BBox) => void
  onRemoveArea: (areaId: string) => void
  onRenameArea: (areaId: string, name: string) => void
  disabled?: boolean
}

function RectangleDrawer({
  enabled,
  onComplete,
}: {
  enabled: boolean
  onComplete: (bbox: BBox) => void
}) {
  const [firstCorner, setFirstCorner] = useState<LatLngTuple | null>(null)
  const map = useMapEvents({
    click(event) {
      if (!enabled) {
        setFirstCorner(null)
        return
      }
      const point: LatLngTuple = [event.latlng.lat, event.latlng.lng]
      if (!firstCorner) {
        setFirstCorner(point)
        return
      }

      const [firstLat, firstLon] = firstCorner
      const bbox = {
        latMin: Math.min(firstLat, point[0]),
        latMax: Math.max(firstLat, point[0]),
        lonMin: Math.min(firstLon, point[1]),
        lonMax: Math.max(firstLon, point[1]),
      }
      if (Math.abs(firstLon - point[1]) < 0.1 || Math.abs(firstLat - point[0]) < 0.1) {
        return
      }
      onComplete(bbox)
      setFirstCorner(null)
      map.getContainer().focus()
    },
  })

  return firstCorner ? (
    <CircleMarker center={firstCorner} radius={7} pathOptions={{ color: '#603d91', fillColor: '#fff', fillOpacity: 1 }} />
  ) : null
}

export default function RegionMap({ areas, onAddArea, onRemoveArea, onRenameArea, disabled = false }: Props) {
  const [drawing, setDrawing] = useState(false)
  const [drawError, setDrawError] = useState('')

  function completeRectangle(bbox: BBox) {
    if (areas.length >= MAX_AREAS) {
      setDrawError(`Puedes comparar hasta ${MAX_AREAS} zonas a la vez.`)
      setDrawing(false)
      return
    }
    if (bbox.lonMax - bbox.lonMin > 35 || bbox.latMax - bbox.latMin > 25) {
      setDrawError('El rectángulo es muy grande. Acércate al mapa y dibuja una zona de hasta 35° de ancho y 25° de alto.')
      return
    }
    setDrawError('')
    onAddArea(bbox)
    setDrawing(false)
  }

  return (
    <section className="card map-card" aria-labelledby="map-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">ELIGE LOS LUGARES</span>
          <h2 id="map-title">Dibuja una o varias zonas</h2>
        </div>
        <button
          className={`btn map-draw-button${drawing ? ' drawing' : ''}`}
          type="button"
          onClick={() => {
            setDrawError('')
            setDrawing((active) => !active)
          }}
          disabled={disabled || (!drawing && areas.length >= MAX_AREAS)}
        >
          {drawing ? 'Cancelar' : '＋ Dibujar zona'}
        </button>
      </div>
      <p className="map-instructions" role={drawing ? 'status' : undefined}>
        {drawing
          ? 'Haz clic en dos esquinas opuestas del mapa para marcar un rectángulo.'
          : `Agrega hasta ${MAX_AREAS} zonas y compararemos cada una por separado. Acércate al mapa para elegir un área pequeña.`}
      </p>
      <div className={`leaflet-map-shell${drawing ? ' is-drawing' : ''}`}>
        <MapContainer
          center={[15, -25]}
          zoom={2}
          minZoom={2}
          maxZoom={14}
          scrollWheelZoom
          worldCopyJump
          aria-label="Mapa para seleccionar las zonas que quieres comparar"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            maxZoom={19}
          />
          {areas.map((area, index) => (
            <Rectangle
              key={area.areaId}
              bounds={[[area.bbox.latMin, area.bbox.lonMin], [area.bbox.latMax, area.bbox.lonMax]]}
              pathOptions={{ color: COLORS[index % COLORS.length], weight: 3, fillOpacity: 0.16 }}
            >
              <Tooltip sticky>{area.name}</Tooltip>
            </Rectangle>
          ))}
          <RectangleDrawer key={drawing ? 'draw-on' : 'draw-off'} enabled={drawing && !disabled} onComplete={completeRectangle} />
        </MapContainer>
      </div>
      <p className="map-caption">Mapa © OpenStreetMap contributors. La selección es rectangular y cada resultado representa el promedio de toda su zona.</p>
      {drawError && <p className="form-error" role="alert">{drawError}</p>}
      {areas.length > 0 ? (
        <div className="area-list" aria-label="Zonas elegidas">
          {areas.map((area, index) => (
            <div className="area-item" key={area.areaId}>
              <span className="area-swatch" style={{ backgroundColor: COLORS[index % COLORS.length] }} aria-hidden="true" />
              <label className="sr-only" htmlFor={`area-name-${area.areaId}`}>Nombre de la zona {index + 1}</label>
              <input
                id={`area-name-${area.areaId}`}
                value={area.name}
                maxLength={80}
                onChange={(event) => onRenameArea(area.areaId, event.target.value)}
                disabled={disabled}
                aria-label={`Nombre de la zona ${index + 1}`}
              />
              <span className="area-coordinates">{area.bbox.latMin.toFixed(1)}°–{area.bbox.latMax.toFixed(1)}° lat.</span>
              <button type="button" className="remove-area" onClick={() => onRemoveArea(area.areaId)} disabled={disabled} aria-label={`Quitar ${area.name}`}>
                Quitar
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="empty-areas">Aún no has marcado ninguna zona. Empieza dibujando un rectángulo en el mapa.</p>
      )}
    </section>
  )
}
