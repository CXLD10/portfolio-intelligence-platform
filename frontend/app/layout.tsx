import './globals.css'
import { Nav } from '@/components/nav'
import { Toaster } from 'sonner'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html className='dark'>
      <body className='max-w-7xl mx-auto p-6 space-y-4'>
        <Nav />
        <main className='page-enter'>{children}</main>
        <Toaster richColors theme='dark' position='top-right' />
      </body>
    </html>
  )
}
