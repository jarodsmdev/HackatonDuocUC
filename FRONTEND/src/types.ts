
export type RiskLevel = 'Alto' | 'Medio' | 'Bajo'
export type CriticalPoint = { id: string; name: string; lat: number; lng: number; risk: RiskLevel; probability: number; roadType: string; region: string; city: string; timeband?: string }
export type CriticalRoute = { id: string; label: string; risk: RiskLevel; score: number }
export type KPI = { accidents: { value: number, deltaPct: number }, victims: { value: number, deltaPct: number }, improvements: { value: number, deltaPct: number } }
export type Proposal = { id: string; title: string; priority: 'Alta' | 'Media' | 'Baja'; expectedImpactPct: number; eta: string; cost: string; description: string; techDetails: string }
