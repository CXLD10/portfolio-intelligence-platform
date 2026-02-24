'use client'

import { toast } from 'sonner'
import { useEffect } from 'react'
import { ErrorCard } from '@/components/ui'

export default function Error({ error }: { error: Error }) {
  useEffect(() => { toast.error(error.message || 'Unexpected application error') }, [error])
  return <ErrorCard title='Application error' message='An unexpected error occurred while rendering the page.' />
}
