import './globals.css'
import { Nav } from '@/components/nav'
export default function RootLayout({children}:{children:React.ReactNode}){return <html className='dark'><body className='max-w-7xl mx-auto p-6 space-y-4'><Nav/>{children}</body></html>}
