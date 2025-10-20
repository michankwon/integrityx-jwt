"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

interface SparklineProps {
  readonly data: number[]
  readonly width?: number
  readonly height?: number
  readonly strokeWidth?: number
  readonly strokeColor?: string
  readonly fillColor?: string
  readonly className?: string
  readonly showDots?: boolean
  readonly dotColor?: string
  readonly dotSize?: number
  readonly smooth?: boolean
  readonly animation?: boolean
  readonly animationDuration?: number
}

export function Sparkline({
  data,
  width = 120,
  height = 40,
  strokeWidth = 2,
  strokeColor = "currentColor",
  fillColor = "none",
  className,
  showDots = false,
  dotColor = "currentColor",
  dotSize = 3,
  smooth = true,
  animation = true,
  animationDuration = 1000
}: SparklineProps) {
  const svgRef = React.useRef<SVGSVGElement>(null)
  const [isVisible, setIsVisible] = React.useState(false)

  // Calculate the path data
  const pathData = React.useMemo(() => {
    if (data.length === 0) return ""

    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width
      const y = height - ((value - min) / range) * height
      return `${x},${y}`
    })

    if (smooth && points.length > 2) {
      // Create smooth curves using quadratic Bézier curves
      let path = `M ${points[0]}`
      
      for (let i = 1; i < points.length - 1; i++) {
        const [x1, y1] = points[i - 1].split(',').map(Number)
        const [x2, y2] = points[i].split(',').map(Number)
        
        const cp1x = x1 + (x2 - x1) / 2
        const cp1y = y1
        
        path += ` Q ${cp1x},${cp1y} ${x2},${y2}`
      }
      
      const [x2, y2] = points[points.length - 2].split(',').map(Number)
      const [x3, y3] = points[points.length - 1].split(',').map(Number)
      const cp1x = x2 + (x3 - x2) / 2
      const cp1y = y2
      
      path += ` Q ${cp1x},${cp1y} ${x3},${y3}`
      
      return path
    } else {
      // Simple line
      return `M ${points.join(' L ')}`
    }
  }, [data, width, height, smooth])

  // Calculate the area fill path
  const areaPath = React.useMemo(() => {
    if (data.length === 0 || fillColor === "none") return ""

    const min = Math.min(...data)
    const max = Math.max(...data)
    const range = max - min || 1

    const points = data.map((value, index) => {
      const x = (index / (data.length - 1)) * width
      const y = height - ((value - min) / range) * height
      return `${x},${y}`
    })

    const lastPoint = points[points.length - 1]
    
    return `${pathData} L ${lastPoint.split(',')[0]},${height} L 0,${height} Z`
  }, [data, width, height, pathData, fillColor])

  // Intersection observer for animation
  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
        }
      },
      { threshold: 0.1 }
    )

    if (svgRef.current) {
      observer.observe(svgRef.current)
    }

    return () => observer.disconnect()
  }, [])

  // Calculate statistics
  const stats = React.useMemo(() => {
    if (data.length === 0) return { min: 0, max: 0, avg: 0, trend: 0 }
    
    const min = Math.min(...data)
    const max = Math.max(...data)
    const avg = data.reduce((sum, val) => sum + val, 0) / data.length
    
    // Calculate trend (simple linear regression slope)
    let trend = 0
    if (data.length > 1) {
      const n = data.length
      const sumX = (n * (n - 1)) / 2
      const sumY = data.reduce((sum, val) => sum + val, 0)
      const sumXY = data.reduce((sum, val, i) => sum + val * i, 0)
      const sumXX = data.reduce((sum, val, i) => sum + i * i, 0)
      
      trend = (n * sumXY - sumX * sumY) / (n * sumXX - sumX * sumX)
    }
    
    return { min, max, avg, trend }
  }, [data])

  return (
    <div className={cn("inline-flex items-center gap-2", className)}>
      <svg
        ref={svgRef}
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
        className="overflow-visible"
        style={{
          color: strokeColor
        }}
      >
        {/* Area fill */}
        {fillColor !== "none" && (
          <path
            d={areaPath}
            fill={fillColor}
            fillOpacity={0.1}
            className={cn(
              animation && isVisible && "animate-pulse"
            )}
            style={{
              animationDuration: `${animationDuration}ms`
            }}
          />
        )}
        
        {/* Main line */}
        <path
          d={pathData}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeLinejoin="round"
          className={cn(
            animation && isVisible && "animate-draw"
          )}
          style={{
            strokeDasharray: animation && isVisible ? "1000" : "none",
            strokeDashoffset: animation && isVisible ? "1000" : "0",
            animationDuration: `${animationDuration}ms`,
            animationFillMode: "forwards"
          }}
        />
        
        {/* Dots */}
        {showDots && data.map((value, index) => {
          const min = Math.min(...data)
          const max = Math.max(...data)
          const range = max - min || 1
          const x = (index / (data.length - 1)) * width
          const y = height - ((value - min) / range) * height
          
          return (
            <circle
              key={`dot-${x}-${y}`}
              cx={x}
              cy={y}
              r={dotSize}
              fill={dotColor}
              className={cn(
                animation && isVisible && "animate-fade-in"
              )}
              style={{
                animationDelay: `${(index * animationDuration) / data.length}ms`,
                animationDuration: `${animationDuration / 2}ms`
              }}
            />
          )
        })}
      </svg>
      
      {/* Optional stats display */}
      <div className="text-xs text-muted-foreground min-w-0">
        <div className="truncate">
          {stats.trend > 0 ? "↗" : (stats.trend < 0 ? "↘" : "→")} {stats.avg.toFixed(1)}
        </div>
      </div>
    </div>
  )
}

// Preset configurations for common use cases
export function SparklineSuccess({ data, ...props }: Readonly<Omit<SparklineProps, 'strokeColor' | 'fillColor'>>) {
  return (
    <Sparkline
      {...props}
      data={data}
      strokeColor="hsl(var(--chart-1))"
      fillColor="hsl(var(--chart-1))"
    />
  )
}

export function SparklineWarning({ data, ...props }: Readonly<Omit<SparklineProps, 'strokeColor' | 'fillColor'>>) {
  return (
    <Sparkline
      {...props}
      data={data}
      strokeColor="hsl(var(--chart-2))"
      fillColor="hsl(var(--chart-2))"
    />
  )
}

export function SparklineError({ data, ...props }: Readonly<Omit<SparklineProps, 'strokeColor' | 'fillColor'>>) {
  return (
    <Sparkline
      {...props}
      data={data}
      strokeColor="hsl(var(--chart-3))"
      fillColor="hsl(var(--chart-3))"
    />
  )
}

export function SparklineInfo({ data, ...props }: Readonly<Omit<SparklineProps, 'strokeColor' | 'fillColor'>>) {
  return (
    <Sparkline
      {...props}
      data={data}
      strokeColor="hsl(var(--chart-4))"
      fillColor="hsl(var(--chart-4))"
    />
  )
}

// Mini sparkline for compact displays
export function MiniSparkline({ data, ...props }: Readonly<Omit<SparklineProps, 'width' | 'height'>>) {
  return (
    <Sparkline
      {...props}
      data={data}
      width={60}
      height={20}
      strokeWidth={1.5}
      showDots={false}
      animation={false}
    />
  )
}

// Add CSS animations
const style = document.createElement('style')
style.textContent = `
  @keyframes draw {
    to {
      stroke-dashoffset: 0;
    }
  }
  
  @keyframes fade-in {
    from {
      opacity: 0;
      transform: scale(0);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }
  
  .animate-draw {
    animation: draw linear forwards;
  }
  
  .animate-fade-in {
    animation: fade-in ease-out forwards;
  }
`
document.head.appendChild(style)
