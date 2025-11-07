
import React from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import { CriticalPoint } from '../types'
import { riskColor } from '../lib/utils'

export default function MapView({ points, onSelect }: { points: CriticalPoint[], onSelect: (p: CriticalPoint)=>void }) {
  const center = [-33.45, -70.66] // Santiago
  return (
    <div className="card map-card">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8}}>
        <h3>Mapa de Rutas Críticas</h3>
        <div className="legend">
          <div className="pill"><span className="dot" style={{background:'#ff6b6b'}}/> Alto</div>
          <div className="pill"><span className="dot" style={{background:'#ffbf4f'}}/> Medio</div>
          <div className="pill"><span className="dot" style={{background:'#38d39f'}}/> Bajo</div>
        </div>
      </div>
      <MapContainer center={center as any} zoom={6} scrollWheelZoom className="leaflet-container">
        <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {points.map(p => (
          <CircleMarker
            key={p.id}
            center={[p.lat, p.lng] as any}
            radius={10}
            pathOptions={{ color: riskColor(p.risk), fillColor: riskColor(p.risk), fillOpacity: 0.7, weight: 2 }}
            eventHandlers={{ click: () => onSelect(p) }}
          >
            <Popup>
              <strong>{p.name}</strong><br/>
              Riesgo: {p.risk}<br/>
              Probabilidad: {(p.probability*100).toFixed(0)}%<br/>
              Tipo de vía: {p.roadType}<br/>
              Región/Ciudad: {p.region} / {p.city}<br/>
              Horario crítico: {p.timeband ?? 's/d'}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}
