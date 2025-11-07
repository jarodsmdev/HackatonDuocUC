import React, { useEffect, useState } from 'react'
import Navbar from './components/Navbar'
import AgentQuery from './components/AgentQuery'
import MapView from './components/MapView'
import CriticalRoutesTable from './components/CriticalRoutesTable'
import TemporalAnalysis from './components/TemporalAnalysis'
import AgentProposals from './components/AgentProposals'
import ComunaRanking from './components/ComunaRanking'
import { CriticalPoint, CriticalRoute, KPI, Proposal, ComunaRanking as CRType } from './types'
import { buildProposalFromDriver } from './helpers/proposals'

// --- Helpers para parsear el texto ---
function normalize(str: string) {
  return str.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

function extractDate(q: string): string | null {
  const m1 = q.match(/\b(\d{2})[\/\-](\d{2})[\/\-](\d{4})\b/)
  if (m1) {
    const [, dd, mm, yyyy] = m1
    return `${yyyy}-${mm}-${dd}`
  }
  const m2 = q.match(/\b(\d{4})-(\d{2})-(\d{2})\b/)
  if (m2) return m2[0]
  return null
}

function extractAccidentType(q: string): string {
  const s = normalize(q)
  if (/\b(choque|colision|colisión)\b/.test(s)) return 'colision'
  if (/\b(atropello|atropellar)\b/.test(s)) return 'atropello'
  if (/\b(volcamiento|volcar)\b/.test(s)) return 'volcamiento'
  if (/\b(incendio)\b/.test(s)) return 'incendio'
  if (/\b(despiste|salida de via)\b/.test(s)) return 'despiste'
  return 'colision'
}

function extractComunaRegion(q: string): { comuna: string; region: string } {
  const s = normalize(q)
  const alias: Record<string, string> = {
    alameda: 'SANTIAGO',
    'santiago centro': 'SANTIAGO',
    santiago: 'SANTIAGO',
    providencia: 'PROVIDENCIA',
    'las condes': 'LAS CONDES',
    maipu: 'MAIPU',
    nunoa: 'NUÑOA',
    'la florida': 'LA FLORIDA',
    'lo espejo': 'LO ESPEJO',
    curacavi: 'CURACAVI',
    pirque: 'PIRQUE',
    tiltil: 'TILTIL',
    'isla de maipo': 'ISLA DE MAIPO'
  }
  for (const key of Object.keys(alias)) {
    if (s.includes(key)) return { comuna: alias[key], region: 'METROPOLITANA' }
  }
  return { comuna: 'SANTIAGO', region: 'METROPOLITANA' }
}

function parseUserQuery(q: string) {
let fecha = extractDate(q)
if (!fecha) {
  // Busca formato DD/MM/YYYY
  const m = q.match(/\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b/)
  if (m) {
    const [, d, mth, y] = m
    fecha = `${y}-${mth.padStart(2, '0')}-${d.padStart(2, '0')}`
  } else {
    fecha = new Date().toISOString().slice(0, 10)
  }
}
  const tipo_accidente = extractAccidentType(q)
  const { comuna, region } = extractComunaRegion(q)
  return { comuna, region, tipo_accidente, fecha, prompt: q.trim() }
}

export default function App() {
  const [query, setQuery] = useState('')
  const [points, setPoints] = useState<CriticalPoint[]>([])
  const [routes, setRoutes] = useState<CriticalRoute[]>([])
  const [kpi, setKpi] = useState<KPI | null>(null)
  const [temporal, setTemporal] = useState<any>(null)
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [selected, setSelected] = useState<CriticalPoint | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [ranking, setRanking] = useState<CRType[]>([])
  const [rankingLoading, setRankingLoading] = useState(false)
  const [rankingError, setRankingError] = useState<string | null>(null)

  const API_BASE = '' // usando proxy de Vite

  const onAsk = async (q: string) => {
    setQuery(q)
    setLoading(true)
    setError(null)

    try {
      const payload = parseUserQuery(q)
      console.log('📤 Payload enviado:', payload)
      const res = await fetch(`${API_BASE}/api/risk/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      if (!res.ok) throw new Error(`Error HTTP ${res.status}`)
      const data = await res.json()

      const score = Number(data?.risk_score ?? 0)
      const level = String(data?.risk_level ?? 'Bajo') as 'Alto' | 'Medio' | 'Bajo'

      setKpi({
        accidents: { value: Math.round(score * 100), deltaPct: 0 },
        victims: { value: Math.round(score * 25), deltaPct: 0 },
        improvements: { value: level === 'Alto' ? 1 : 0, deltaPct: 0 }
      })

      const drv: string[] = Array.isArray(data?.drivers) ? data.drivers : []
      setProposals(drv.slice(0, 5).map((d, i) => buildProposalFromDriver(d, i, score)))

      setPoints([])
      setRoutes([])
      setTemporal({ scoreSeries: [{ t: data?.timestamp || new Date().toISOString(), v: score }] })
    } catch (e: any) {
      console.error('Error al consultar la API:', e)
      setError('No se pudo conectar con el backend o el formato de respuesta no es válido.')
    } finally {
      setLoading(false)
    }
  }

  const fetchRanking = async () => {
    setRankingLoading(true)
    try {
      const res = await fetch(`${API_BASE}/api/risk/comunas/ranking`)
      if (!res.ok) throw new Error(`Error HTTP ${res.status}`)
      const data: CRType[] = await res.json()
      setRanking(data ?? [])
    } catch (e: any) {
      console.error('Error ranking:', e)
      setRankingError('No se pudo obtener el ranking de comunas.')
    } finally {
      setRankingLoading(false)
    }
  }

  useEffect(() => {
    fetchRanking()
  }, [])

  return (
    <div className="container">
      <Navbar />
      <div className="content">
        <AgentQuery
          kpi={
            kpi || {
              accidents: { value: 0, deltaPct: 0 },
              victims: { value: 0, deltaPct: 0 },
              improvements: { value: 0, deltaPct: 0 }
            }
          }
          onSubmit={onAsk}
        />

        {loading && <div className="card"><strong>Cargando datos...</strong></div>}
        {error && <div className="card" style={{ color: 'red' }}>{error}</div>}

        <div className="grid-main">
          <MapView points={points} onSelect={setSelected} />

          {selected && (
            <div className="card">
              <h3>Detalle del punto seleccionado</h3>
              <p><strong>{selected.name}</strong></p>
              <ul>
                <li>Riesgo: {selected.risk}</li>
                <li>Probabilidad: {(selected.probability * 100).toFixed(0)}%</li>
                <li>Tipo de vía: {selected.roadType}</li>
                <li>Región/Ciudad: {selected.region} / {selected.city}</li>
                <li>Horario crítico: {selected.timeband ?? 's/d'}</li>
              </ul>
            </div>
          )}

          <ComunaRanking items={ranking} loading={rankingLoading} error={rankingError} />
          <CriticalRoutesTable routes={routes} />
{temporal ? (
  <TemporalAnalysis data={temporal} />
) : (
  <div className="card"><p>No hay datos temporales disponibles.</p></div>
)}
          <AgentProposals proposals={proposals} />
        </div>
      </div>
    </div>
  )
}
