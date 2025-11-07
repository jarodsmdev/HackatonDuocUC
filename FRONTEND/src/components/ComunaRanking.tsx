// src/components/ComunaRanking.tsx
import React from 'react'

import { aurocColor, aurocToPct } from '../lib/utils'
import { ComunaRanking } from '../types'

type Props = {
  items: ComunaRanking[]
  loading?: boolean
  error?: string | null
}

export default function ComunaRankings({ items, loading, error }: Props) {
  return (
    <div className="card">
      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
        <h3>Ranking por comuna (AUROC)</h3>
        <span className="tag">{items.length} comunas</span>
      </div>

      {loading && <div><strong>Cargando ranking…</strong></div>}
      {error && <div style={{color:'red'}}>{error}</div>}

      {!loading && !error && (
        <table className="table">
          <thead>
            <tr>
              <th>Comuna</th>
              <th style={{textAlign:'right'}}>AUROC</th>
            </tr>
          </thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.comuna}>
                <td>{r.comuna}</td>
                <td style={{textAlign:'right'}}>
                  <span className="badge" style={{borderColor: aurocColor(r.auroc)}}>
                    {aurocToPct(r.auroc)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
