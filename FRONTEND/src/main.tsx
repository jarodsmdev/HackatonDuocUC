
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles.css'
import 'leaflet/dist/leaflet.css'
import { ThemeProvider } from './theme'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>
)
