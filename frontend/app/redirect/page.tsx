'use client'

import { useUser } from '@clerk/nextjs'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function RedirectPage() {
  const { user, isLoaded } = useUser()
  const router = useRouter()

  useEffect(() => {
    if (isLoaded) {
      if (user) {
        // User is authenticated, redirect to dashboard
        router.push('/')
      } else {
        // User is not authenticated, redirect to landing page
        router.push('/landing')
      }
    }
  }, [user, isLoaded, router])

  return (
    <div className="container">
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <h2>Redirecting...</h2>
        <p>Please wait while we redirect you to the appropriate page.</p>
      </div>
    </div>
  )
}
