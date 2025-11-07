
import React from 'react'
import { Proposal } from '../types'

export default function AgentProposals({ proposals }:{ proposals: Proposal[] }) {
  return (
    <div className="card">
      <h3>Mejoras propuestas por el agente</h3>
      <div className="card-grid">
        {proposals.map(p => (
          <div key={p.id} className="card">
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
              <strong>{p.title}</strong>
              <span className="tag">Prioridad: {p.priority}</span>
            </div>
            <p style={{marginTop:8}}>{p.description}</p>
            <ul>
              <li><strong>Impacto esperado:</strong> {p.expectedImpactPct}%</li>
              <li><strong>Plazo:</strong> {p.eta}</li>
              <li><strong>Costo:</strong> {p.cost}</li>
            </ul>
            <details>
              <summary>Detalles técnicos</summary>
              <p>{p.techDetails}</p>
            </details>
          </div>
        ))}
      </div>
      <p style={{color:'#a9b3d8', fontSize:12, marginTop:8}}>Template en espera de respuesta de API.</p>
    </div>
  )
}
