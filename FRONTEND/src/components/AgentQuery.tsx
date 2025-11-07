import React, { useEffect, useRef, useState } from 'react'
import { KPI } from '../types'

declare global {
  interface Window {
    webkitSpeechRecognition?: any
    SpeechRecognition?: any
  }
}

export default function AgentQuery({
  kpi,
  onSubmit
}: {
  kpi: KPI
  onSubmit: (q: string) => void
}) {
  const [q, setQ] = useState('Quiero saber el riesgo de accidentes en Alameda el 23/09/2025')
  const [listening, setListening] = useState(false)
  const recRef = useRef<any>(null)

  useEffect(() => {
    const Rec = window.SpeechRecognition || window.webkitSpeechRecognition
    if (Rec) {
      const rec = new Rec()
      rec.lang = 'es-CL'
      rec.interimResults = false
      rec.maxAlternatives = 1
      rec.onresult = (e: any) => {
        const txt = e.results[0][0].transcript
        setQ(prev => (prev ? prev + ' ' : '') + txt)
      }
      rec.onend = () => setListening(false)
      recRef.current = rec
    }
  }, [])

  const startStop = () => {
    if (!recRef.current) return alert('Este navegador no soporta reconocimiento de voz. Usa Chrome/Edge en escritorio.')
    if (listening) { recRef.current.stop(); setListening(false) }
    else { setListening(true); recRef.current.start() }
  }

  const speak = (text: string) => {
    const u = new SpeechSynthesisUtterance(text)
    u.lang = 'es-CL'
    window.speechSynthesis.speak(u)
  }

  const submitNow = () => onSubmit(q)

  return (
    <div className="card query-box">
      <h3>Consulta al Agente</h3>

      <form
        onSubmit={(e) => { e.preventDefault(); submitNow() }}
        style={{ display: 'grid', gap: 8 }}
      >
        <textarea
          value={q}
          onChange={e => setQ(e.target.value)}
          aria-label="Escribe tu consulta"
          placeholder="Ej: Riesgo de accidentes en Alameda el 23/09/2025"
        />
        <div className="row" style={{ marginTop: 8 }}>
          <button type="submit">Preguntar</button>
          <button type="button" className="secondary" onClick={startStop}>
            {listening ? 'Detener voz' : 'Dictar por voz'}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={() => speak('Ingresa tu consulta en el cuadro de texto. Puedes dictar usando el botón de voz. Para oír resultados, activa el lector en tu navegador.')}
          >
            Leer instrucciones
          </button>
        </div>
      </form>

      <p style={{ color: '#a9b3d8', fontSize: 12, marginTop: 8 }}>
        Template: la pregunta será enviada al RAG/Agente cuando el backend esté disponible.
      </p>

      {/* KPIs (sin gráficos) */}
      <div className="kpi" style={{ marginTop: 12 }}>
        <div className="kpi-item red">
          <div>Accidentes (6 meses)</div>
          <strong>{kpi.accidents.value}</strong>
          <span className="delta">+{kpi.accidents.deltaPct}%</span>
        </div>
        <div className="kpi-item blue">
          <div>Víctimas fatales/graves</div>
          <strong>{kpi.victims.value}</strong>
          <span className="delta">{kpi.victims.deltaPct}%</span>
        </div>
        <div className="kpi-item green">
          <div>Mejoras aplicadas</div>
          <strong>{kpi.improvements.value}</strong>
          <span className="delta">+{kpi.improvements.deltaPct}%</span>
        </div>
      </div>
    </div>
  )
}
