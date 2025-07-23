"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { DuckLogo } from "./duck-logo"

export function DuckAnimation() {
  const [isVisible, setIsVisible] = useState(false)
  const [showMessage, setShowMessage] = useState(false)

  useEffect(() => {
    // Show the duck after a delay
    const timer = setTimeout(() => {
      setIsVisible(true)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    // Show the message bubble after the duck appears
    if (isVisible) {
      const timer = setTimeout(() => {
        setShowMessage(true)
      }, 1500)

      return () => clearTimeout(timer)
    }
  }, [isVisible])

  return (
    <div className="fixed bottom-20 right-6 z-10">
      {showMessage && (
        <motion.div
          className="mb-2 p-3 bg-emerald-500 text-white rounded-lg rounded-br-none max-w-[200px] shadow-lg"
          initial={{ opacity: 0, y: 10, scale: 0.8 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <p className="text-sm font-medium">Need help with your data? Just ask me!</p>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, x: 100 }}
        animate={{
          opacity: isVisible ? 1 : 0,
          x: isVisible ? 0 : 100,
        }}
        whileHover={{ scale: 1.05, rotate: [-2, 2, -2, 0] }}
        transition={{ duration: 0.5 }}
        onClick={() => setShowMessage(!showMessage)}
        className="cursor-pointer"
      >
        <DuckLogo size={80} className="filter drop-shadow-lg" />
      </motion.div>
    </div>
  )
}
