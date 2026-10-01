import { useEffect } from 'react'
import {
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
} from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

type Place = {
  name: string
  category: string
  lat: number
  lon: number
  description?: string
}

type Props = {
  destination: string
  center: Place
  origin?: Place | null
  places: Place[]
  route: number[][]
  activePlaces?: Place[]
}

const defaultIcon = new L.Icon({
  iconUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl:
    'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

function FitBounds({
  center,
  origin,
  places,
  route,
}: {
  center: Place
  origin?: Place | null
  places: Place[]
  route: number[][]
}) {
  const map = useMap()

  useEffect(() => {
    const points: [number, number][] = []

    if (origin) {
      points.push([origin.lat, origin.lon])
    }

    points.push([center.lat, center.lon])

    places.forEach((place) => {
      points.push([place.lat, place.lon])
    })

    route.forEach((point) => {
      if (point.length >= 2) {
        points.push([point[0], point[1]])
      }
    })

    if (points.length > 1) {
      map.fitBounds(points, {
        padding: [30, 30],
      })
    } else {
      map.setView(
        [center.lat, center.lon],
        11
      )
    }
  }, [map, center, origin, places, route])

  return null
}

export default function TripMap({
  destination,
  center,
  origin,
  places,
  route,
  activePlaces = [],
}: Props) {
  const activeNames = new Set(
    activePlaces.map((place) => place.name)
  )

  return (
    <div
      style={{
        height: '420px',
        width: '100%',
        overflow: 'hidden',
        borderRadius: '18px',
      }}
    >
      <MapContainer
        center={[center.lat, center.lon]}
        zoom={11}
        scrollWheelZoom={false}
        style={{
          height: '100%',
          width: '100%',
        }}
      >
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <FitBounds
          center={center}
          origin={origin}
          places={places}
          route={route}
        />

        {origin && (
          <Marker
            position={[origin.lat, origin.lon]}
            icon={defaultIcon}
          >
            <Popup>
              <strong>Starting point</strong>
              <br />
              {origin.name}
            </Popup>
          </Marker>
        )}

        <Marker
          position={[center.lat, center.lon]}
          icon={defaultIcon}
        >
          <Popup>
            <strong>{destination}</strong>
            <br />
            Destination
          </Popup>
        </Marker>

        {places.map((place) => (
          <Marker
            key={`${place.name}-${place.lat}-${place.lon}`}
            position={[place.lat, place.lon]}
            icon={defaultIcon}
            opacity={
              activeNames.size === 0 ||
              activeNames.has(place.name)
                ? 1
                : 0.65
            }
          >
            <Popup>
              <strong>{place.name}</strong>
              <br />
              {place.category}
              {place.description && (
                <>
                  <br />
                  {place.description}
                </>
              )}
            </Popup>
          </Marker>
        ))}

        {route.length > 1 && (
          <Polyline
            positions={route as [number, number][]}
            pathOptions={{
              weight: 4,
              opacity: 0.8,
            }}
          />
        )}
      </MapContainer>
    </div>
  )
}