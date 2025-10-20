import { ReactNode } from 'react'
import { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: ReactNode
  className?: string
}

export function EmptyState({ 
  icon: Icon, 
  title, 
  description, 
  action, 
  className = '' 
}: EmptyStateProps) {
  return (
    <div className={`text-center py-12 ${className}`}>
      <Icon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 mb-6 max-w-sm mx-auto">{description}</p>
      {action && <div>{action}</div>}
    </div>
  )
}

// Alias for backward compatibility
export const NoResultsEmptyState = EmptyState;