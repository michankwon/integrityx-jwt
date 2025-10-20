'use client'

import { usePathname } from 'next/navigation'
import MainNav from '@/components/MainNav'
import VoiceCommandButton from '@/components/VoiceCommandButton'
import { SimpleToastContainer as ToastContainer } from '@/components/ui/simple-toast'

export function LayoutContent({ children }: Readonly<{ children: React.ReactNode }>) {
  const pathname = usePathname()
  
  // Check if current route is public
  const isPublicRoute = 
    pathname === '/' ||
    pathname.startsWith('/sign-in') || 
    pathname.startsWith('/sign-up') || 
    pathname === '/landing'

  return (
    <>
      {!isPublicRoute && <MainNav />}
      <main className={isPublicRoute ? "" : "min-h-screen bg-gray-50"}>
        {children}
      </main>
      {!isPublicRoute && <VoiceCommandButton />}
      <ToastContainer />
    </>
  )
}

