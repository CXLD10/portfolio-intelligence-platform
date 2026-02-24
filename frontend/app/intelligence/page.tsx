import { getIntelligence } from '@/lib/api'
export default async function Intelligence(){const d=await getIntelligence('INFY','NSE'); return <div className='grid md:grid-cols-3 gap-4'>
<div className='panel md:col-span-2'><h2 className='font-semibold'>AI Reasoning</h2><p className='text-sm text-slate-300 mt-2'>{d.summary}</p><div className='mt-3 text-sm'>Model: {d.provenance.model_version}</div></div>
<div className='panel'><h2 className='font-semibold'>Confidence</h2><div className='text-2xl mt-2'>{(d.confidence*100).toFixed(1)}%</div></div>
<div className='panel'><h3 className='font-semibold'>Quant</h3><p>{d.quant_score.toFixed(3)}</p></div>
<div className='panel'><h3 className='font-semibold'>Risk</h3><p>{d.risk_score.toFixed(3)}</p></div>
<div className='panel'><h3 className='font-semibold'>Feature Importance</h3>{Object.entries(d.explainability.feature_importance).map(([k,v])=><div key={k} className='text-sm flex justify-between'><span>{k}</span><span>{Number(v).toFixed(2)}</span></div>)}</div>
</div>}
