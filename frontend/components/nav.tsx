import Link from 'next/link'
const links=[['/dashboard','Dashboard'],['/intelligence','Stock Intelligence'],['/portfolio','Portfolio'],['/backtest','Backtest'],['/sentiment','Sentiment']]
export function Nav(){return <nav className='panel flex flex-wrap gap-3'>{links.map(([h,l])=><Link key={h} href={h} className='text-sm text-slate-200 hover:text-white'>{l}</Link>)}</nav>}
