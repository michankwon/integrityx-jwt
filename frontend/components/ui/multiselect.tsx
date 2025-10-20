"use client"

import * as React from "react"
import { ChevronDown, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"

export interface MultiselectOption {
  value: string
  label: string
  disabled?: boolean
}

interface MultiselectProps {
  options: MultiselectOption[]
  value: string[]
  onChange: (value: string[]) => void
  placeholder?: string
  className?: string
  disabled?: boolean
  maxDisplay?: number
}

export function Multiselect({
  options,
  value,
  onChange,
  placeholder = "Select options...",
  className,
  disabled = false,
  maxDisplay = 3
}: MultiselectProps) {
  const [open, setOpen] = React.useState(false)

  const handleSelect = (optionValue: string) => {
    if (value.includes(optionValue)) {
      onChange(value.filter(v => v !== optionValue))
    } else {
      onChange([...value, optionValue])
    }
  }

  const handleRemove = (optionValue: string) => {
    onChange(value.filter(v => v !== optionValue))
  }

  const selectedOptions = options.filter(option => value.includes(option.value))
  const displayText = selectedOptions.length === 0 
    ? placeholder
    : selectedOptions.length <= maxDisplay
    ? selectedOptions.map(opt => opt.label).join(", ")
    : `${selectedOptions.length} selected`

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn(
            "w-full justify-between text-left font-normal",
            !value.length && "text-muted-foreground",
            className
          )}
          disabled={disabled}
        >
          <span className="truncate">{displayText}</span>
          <ChevronDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0" align="start">
        <div className="max-h-60 overflow-auto">
          {options.map((option) => (
            <div
              key={option.value}
              className={cn(
                "flex items-center space-x-2 px-3 py-2 hover:bg-accent hover:text-accent-foreground cursor-pointer",
                option.disabled && "opacity-50 cursor-not-allowed"
              )}
              onClick={() => !option.disabled && handleSelect(option.value)}
            >
              <Checkbox
                checked={value.includes(option.value)}
                disabled={option.disabled}
                className="pointer-events-none"
              />
              <span className="flex-1 text-sm">{option.label}</span>
            </div>
          ))}
        </div>
        {value.length > 0 && (
          <div className="border-t p-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onChange([])}
              className="w-full text-xs"
            >
              Clear all
            </Button>
          </div>
        )}
      </PopoverContent>
    </Popover>
  )
}

interface MultiselectBadgesProps {
  options: MultiselectOption[]
  value: string[]
  onRemove: (value: string) => void
  maxDisplay?: number
  className?: string
}

export function MultiselectBadges({
  options,
  value,
  onRemove,
  maxDisplay = 3,
  className
}: MultiselectBadgesProps) {
  const selectedOptions = options.filter(option => value.includes(option.value))
  const displayOptions = selectedOptions.slice(0, maxDisplay)
  const remainingCount = selectedOptions.length - maxDisplay

  if (selectedOptions.length === 0) {
    return null
  }

  return (
    <div className={cn("flex flex-wrap gap-1", className)}>
      {displayOptions.map((option) => (
        <Badge
          key={option.value}
          variant="secondary"
          className="text-xs"
        >
          {option.label}
          <button
            onClick={() => onRemove(option.value)}
            className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
          >
            <X className="h-3 w-3" />
          </button>
        </Badge>
      ))}
      {remainingCount > 0 && (
        <Badge variant="outline" className="text-xs">
          +{remainingCount} more
        </Badge>
      )}
    </div>
  )
}
