import { Proposal } from '../types'

export function buildProposalFromDriver(text: string, idx: number, score: number): Proposal {
  // Ajustamos las prioridades al formato en español
  let priority: Proposal['priority']
  if (score > 0.5) priority = 'Alta'
  else if (score > 0.25) priority = 'Media'
  else priority = 'Baja'

  return {
    id: `p${idx}`,
    title: text.split(':')[0]?.trim() || `Driver ${idx + 1}`,
    description: text,
    priority,
    expectedImpactPct: Math.round(score * 100 / (idx + 1)) || 10,
    eta: '2-4 semanas',
    cost: `$${(idx + 1) * 1000}`, // string (no number)
    techDetails: 'Análisis técnico preliminar'
  }
}
