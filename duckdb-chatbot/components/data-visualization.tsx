"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"

type DataPoint = {
  label: string
  value: number
}

type DataVisualizationProps = {
  data: DataPoint[]
  title: string
  type?: "bar" | "line"
}

export function DataVisualization({ data, title, type = "bar" }: DataVisualizationProps) {
  const [isVisible, setIsVisible] = useState(false)
  const maxValue = Math.max(...data.map((d) => d.value))

  useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700">
      <h3 className="text-lg font-medium text-white mb-4">{title}</h3>
      <div className="h-64 flex items-end justify-between gap-2">
        {data.map((item, index) => (
          <div key={item.label} className="flex flex-col items-center flex-1">
            <motion.div
              className="w-full bg-emerald-500/80 rounded-t-md"
              initial={{ height: 0 }}
              animate={{ height: isVisible ? `${(item.value / maxValue) * 100}%` : 0 }}
              transition={{ duration: 0.8, delay: index * 0.1, ease: "backOut" }}
            />
            <div className="mt-2 text-xs text-slate-400 text-center">
              <div className="truncate max-w-full">{item.label}</div>
              <div className="font-medium text-slate-300">{item.value}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
