'use client'

import { useEffect, useMemo, useState } from 'react'

export function AnimatedNumber({ value, suffix = '', digits = 2 }: { value: number; suffix?: string; digits?: number }) {
  const [display, setDisplay] = useState(value)
  useEffect(() => {
    const start = display
    const diff = value - start
    const duration = 400
    const t0 = performance.now()
    let raf = 0
    const tick = (now: number) => {
      const p = Math.min((now - t0) / duration, 1)
      setDisplay(start + diff * p)
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [value])
  return <span>{display.toFixed(digits)}{suffix}</span>
}

export function ErrorCard({ title, message }: { title: string; message: string }) {
  return <div className='panel border-red-900/60'><h3 className='text-red-300 font-semibold'>{title}</h3><p className='text-sm text-slate-300 mt-2'>{message}</p></div>
}

export function SkeletonCard() {
  return <div className='panel animate-pulse h-28 bg-slate-900/60' />
}

export const confidenceColor = (c: number) => c > 0.7 ? '#22c55e' : c >= 0.5 ? '#eab308' : '#ef4444'

export function momentumLabel(value: number) {
  if (value > 0.05) return '↑ Bullish momentum'
  if (value < -0.05) return '↓ Bearish momentum'
  return '→ Neutral momentum'
}

export function useDebounce<T>(value: T, delay = 250) {
  const [v, setV] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setV(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return v
}

export function useDerived<T>(factory: () => T, deps: unknown[]) {
  return useMemo(factory, deps)
}
