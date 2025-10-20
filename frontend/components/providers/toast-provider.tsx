"use client"

import { ToastProvider } from "@/components/ui/accessible-toast"

interface AppToastProviderProps {
  children: React.ReactNode
}

export function AppToastProvider({ children }: AppToastProviderProps) {
  return (
    <ToastProvider position="top-right">
      {children}
    </ToastProvider>
  )
}

