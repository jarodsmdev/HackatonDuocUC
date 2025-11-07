
import React from 'react'
import { CriticalRoute } from '../types'
import { riskColor } from '../lib/utils'

export default function CriticalRoutesTable({ routes }: { routes: CriticalRoute[] }) {
  return (
    <div className="card">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h3>Rutas críticas</h3>
        <span className="tag">{routes.length} rutas</span>
      </div>
      <table className="table">
        <thead>
          <tr><th>Ruta</th><th>Nivel</th><th style={{textAlign:'right'}}>Índice</th></tr>
        </thead>
        <tbody>
          {routes.map(r => (
            <tr key={r.id}>
              <td>{r.label}</td>
              <td><span className="tag" style={{borderColor:riskColor(r.risk), color:'#fff'}}>{r.risk}</span></td>
              <td style={{textAlign:'right'}}><span className="badge">{r.score}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
