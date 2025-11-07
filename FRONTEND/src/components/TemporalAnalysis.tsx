// src/components/TemporalAnalysis.tsx
import React from 'react'

type TemporalPoint = {
  t: string
  v: number
}

type TemporalAnalysisProps = {
  data?: {
    scoreSeries?: TemporalPoint[]
  }
}

export default function TemporalAnalysis({ data }: TemporalAnalysisProps) {
  // Evitar error si data o scoreSeries no existen
  if (!data || !Array.isArray(data.scoreSeries)) {
    return (
      <div className="card">
        <h3>Análisis Temporal</h3>
        <p>No hay datos de riesgo temporal disponibles.</p>
      </div>
    )
  }

  return (
    <div className="card">
      <h3>Análisis Temporal</h3>
      <ul>
        {data.scoreSeries.map((p, i) => (
          <li key={i}>
            <strong>{new Date(p.t).toLocaleString()}:</strong> {(p.v * 100).toFixed(2)}%
          </li>
        ))}
      </ul>
    </div>
  )
}
