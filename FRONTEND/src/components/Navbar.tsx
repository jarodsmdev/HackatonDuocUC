
import React from 'react'
import { useTheme, ThemeMode } from '../theme'

export default function Navbar() {
  const { mode, setMode } = useTheme()
  return (
    <div className="navbar">
      <div className="brand">
        <div className="logo">OT</div>
        <div>
          <h1>Optimizador de Rutas Terrestres</h1>
          <small>Sistema de análisis y prevención de accidentes viales</small>
        </div>
      </div>
      <div className="nav-metrics">
        <div className="badge"><span className="dot" /> Rutas críticas <strong>23</strong></div>
        <div className="badge">Reducción potencial <strong>34%</strong></div>
        <div className="theme-toggle">
          <select value={mode} onChange={e=>setMode(e.target.value as ThemeMode)} aria-label="Cambiar tema">
            <option value="light">Modo día</option>
            <option value="dark">Modo oscuro</option>
            <option value="colorblind">Modo daltónico</option>
          </select>
        </div>
      </div>
    </div>
  )
}
