
import React, { createContext, useContext, useEffect, useState } from 'react'

export type ThemeMode = 'light' | 'dark' | 'colorblind'

type ThemeCtx = { mode: ThemeMode; setMode: (m: ThemeMode)=>void }
const Ctx = createContext<ThemeCtx>({ mode: 'dark', setMode: ()=>{} })

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>((localStorage.getItem('theme') as ThemeMode) || 'dark')
  useEffect(()=>{
    document.documentElement.setAttribute('data-theme', mode)
    localStorage.setItem('theme', mode)
  }, [mode])
  return <Ctx.Provider value={{mode, setMode}}>{children}</Ctx.Provider>
}

export function useTheme() { return useContext(Ctx) }
