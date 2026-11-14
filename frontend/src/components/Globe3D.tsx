import { useEffect, useMemo, useRef } from 'react'
import { Canvas } from '@react-three/fiber'
import { Line, OrbitControls } from '@react-three/drei'
import * as THREE from 'three'
import type { BBox, Region } from '../types/api'

function latLonToVector(lat: number, lon: number, radius: number) {
  const phi = THREE.MathUtils.degToRad(90 - lat)
  const theta = THREE.MathUtils.degToRad(lon + 180)
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta),
  )
}

function buildGraticule(): THREE.Vector3[][] {
  const lines: THREE.Vector3[][] = []
  for (let lat = -60; lat <= 60; lat += 30) {
    const pts: THREE.Vector3[] = []
    for (let lon = -180; lon <= 180; lon += 5) {
      pts.push(latLonToVector(lat, lon, 1.003))
    }
    lines.push(pts)
  }
  for (let lon = -180; lon < 180; lon += 30) {
    const pts: THREE.Vector3[] = []
    for (let lat = -90; lat <= 90; lat += 5) {
      pts.push(latLonToVector(lat, lon, 1.003))
    }
    lines.push(pts)
  }
  return lines
}

const GRATICULE = buildGraticule()

function bboxGeometry(bbox: BBox) {
  const lonMax = bbox.lonMax < bbox.lonMin ? bbox.lonMax + 360 : bbox.lonMax
  const steps = 16
  const lerp = (a: number, b: number, t: number) => a + (b - a) * t
  const r = 1.012
  const pts: THREE.Vector3[] = []

  for (let i = 0; i <= steps; i++)
    pts.push(latLonToVector(bbox.latMin, lerp(bbox.lonMin, lonMax, i / steps), r))
  for (let i = 0; i <= steps; i++)
    pts.push(latLonToVector(lerp(bbox.latMin, bbox.latMax, i / steps), lonMax, r))
  for (let i = 0; i <= steps; i++)
    pts.push(latLonToVector(bbox.latMax, lerp(lonMax, bbox.lonMin, i / steps), r))
  for (let i = 0; i <= steps; i++)
    pts.push(latLonToVector(lerp(bbox.latMax, bbox.latMin, i / steps), bbox.lonMin, r))

  const centerLat = (bbox.latMin + bbox.latMax) / 2
  const centerLon = (bbox.lonMin + lonMax) / 2
  return { outline: pts, center: latLonToVector(centerLat, centerLon, 1) }
}

function GlobeScene({ bbox }: { bbox: BBox }) {
  const group = useRef<THREE.Group>(null)
  const { outline, center } = useMemo(() => bboxGeometry(bbox), [bbox])

  // Gira el globo para que la región quede de frente a la cámara (+z).
  useEffect(() => {
    group.current?.quaternion.setFromUnitVectors(
      center.clone().normalize(),
      new THREE.Vector3(0, 0, 1),
    )
  }, [center])

  return (
    <>
      <ambientLight intensity={1} />
      <directionalLight position={[5, 3, 5]} intensity={1.2} />
      <group ref={group}>
        <mesh>
          <sphereGeometry args={[1, 64, 64]} />
          <meshStandardMaterial color="#cfe3f5" />
        </mesh>
        {GRATICULE.map((pts, i) => (
          <Line key={i} points={pts} color="#7aa7cf" lineWidth={1} />
        ))}
        <Line points={outline} color="#e8590c" lineWidth={3} />
      </group>
      <OrbitControls enablePan={false} minDistance={1.8} maxDistance={6} />
    </>
  )
}

export default function Globe3D({ region }: { region: Region }) {
  const { bbox } = region
  const key = `${bbox.latMin}_${bbox.latMax}_${bbox.lonMin}_${bbox.lonMax}`

  return (
    <section className="card" aria-labelledby="globe-title">
      <h2 id="globe-title">Región seleccionada</h2>
      <div
        className="globe-box"
        role="img"
        aria-label={`Globo 3D con la región ${region.name} resaltada`}
      >
        {/* key: reinicia la cámara cuando cambia la región */}
        <Canvas key={key} camera={{ position: [0, 0, 3.2], fov: 45 }}>
          <GlobeScene bbox={bbox} />
        </Canvas>
      </div>
      <p className="caption">
        {region.name}: lat {bbox.latMin}° a {bbox.latMax}°, lon {bbox.lonMin}°
        a {bbox.lonMax}°. Arrastra para rotar y usa la rueda para acercar.
      </p>
    </section>
  )
}