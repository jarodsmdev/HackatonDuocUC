// props esperadas ahora:
export default function TemporalAnalysis({ data }: { data: {
  criticalHours: string[],
  causes: { label: string, pct: number }[]
} }) {
  return (
    <div className="card">
      <h3>Horarios y causas</h3>
      <div className="card-grid">
        <div className="card">
          <h3>Horarios críticos</h3>
          <div className="row" style={{flexWrap:'wrap', gap:8}}>
            {data.criticalHours.map(h => <span key={h} className="tag">{h} hrs</span>)}
          </div>
        </div>
        <div className="card">
          <h3>Causas principales</h3>
          <table className="table">
            <thead><tr><th>Causa</th><th style={{textAlign:'right'}}>%</th></tr></thead>
            <tbody>
              {data.causes.map(c=>(
                <tr key={c.label}><td>{c.label}</td><td style={{textAlign:'right'}}>{c.pct}%</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      <p style={{color:'#a9b3d8', fontSize:12}}>Template en espera de API.</p>
    </div>
  )
}
