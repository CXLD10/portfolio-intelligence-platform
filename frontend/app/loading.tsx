import { SkeletonCard } from '@/components/ui'

export default function Loading() {
  return <div className='grid md:grid-cols-3 gap-4'><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
}
