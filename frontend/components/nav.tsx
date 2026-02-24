'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState } from 'react'
import { useDebounce } from './ui'

const links: [string, string][] = [
  ['/dashboard', 'Market Overview'],
  ['/intelligence', 'Stock Intelligence'],
  ['/portfolio', 'Portfolio'],
  ['/backtest', 'Backtest'],
  ['/sentiment', 'Sentiment'],
]

export function Nav() {
  const pathname = usePathname()
  const [query, setQuery] = useState('')
  const q = useDebounce(query)
  return (
    <nav className='panel sticky top-3 z-40 flex flex-wrap items-center gap-3 backdrop-blur'>
      <div className='text-xs uppercase tracking-[0.18em] text-slate-400'>PIP Terminal</div>
      <div className='flex flex-wrap gap-2'>
        {links
          .filter(([, label]) => label.toLowerCase().includes(q.toLowerCase()))
          .map(([h, l]) => (
            <Link key={h} href={h} className={`px-3 py-1.5 rounded-md text-sm transition-colors ${pathname === h ? 'bg-slate-700 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'}`}>
              {l}
            </Link>
          ))}
      </div>
      <div className='ml-auto'>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className='bg-slate-900 border border-slate-700 rounded-md px-3 py-1.5 text-sm w-56'
          placeholder='Search modules...'
        />
      </div>
    </nav>
  )
}
