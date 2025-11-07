
# 🛣️ Optimizador — Dashboard con Agente (RAG), Modos de Tema y Accesibilidad

- Entrada principal con **consulta libre** (RAG/Agente), botones de **voz a texto** (Web Speech API) y **lector** (SpeechSynthesis).
- **Mapa** con puntos por criticidad (color-safe en modo daltónico).
- **KPIs + Barras** (Recharts) compatibles con **modo oscuro**.
- **Propuestas del agente** en cards (template, listo para API).

## Arranque
```bash
npm install
npm run dev
```
Abre http://localhost:5173

## Temas
- Selector en el navbar: **Día**, **Oscuro**, **Daltónico (Okabe–Ito)**.
- Se guardan en `localStorage`. Variables CSS en `:root[data-theme]`.

## Voz
- **STT**: Web Speech API (Chrome/Edge). Botón “Dictar por voz”.
- **TTS**: botón “Leer instrucciones”. Puedes usar `speechSynthesis` para leer resultados.

## Conexión a API (ejemplo)
```ts
// En App.tsx -> onAsk:
fetch('/api/agent', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ query: q })})
  .then(r=>r.json())
  .then(data => {/* actualizar mapa, lista, KPIs con data */})
```

## Paleta daltónica (Okabe–Ito)
- Alto: #D55E00, Medio: #E69F00, Bajo: #009E73, Azul soporte: #0072B2.
