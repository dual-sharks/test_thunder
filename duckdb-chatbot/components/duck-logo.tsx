"use client"

import { motion } from "framer-motion"

export function DuckLogo({ className = "", size = 40 }: { className?: string; size?: number }) {
  return (
    <motion.div
      className={`relative ${className}`}
      style={{ width: size, height: size }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Duck body */}
      <motion.svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
        {/* Duck body */}
        <motion.path
          d="M75,65 C85,55 85,40 75,30 C65,20 50,20 40,30 C30,40 20,45 15,40 C10,35 10,25 15,20 C20,15 30,15 35,20 C40,25 45,20 45,15 C45,10 40,5 30,5 C20,5 10,15 5,25 C0,35 0,50 10,60 C20,70 30,75 40,75 C50,75 65,75 75,65Z"
          fill="#10b981"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1, ease: "easeInOut" }}
        />

        {/* Duck bill */}
        <motion.path
          d="M15,40 C10,40 5,45 5,50 C5,55 10,60 20,60 C30,60 30,50 30,45 C30,40 25,35 20,35 C15,35 15,40 15,40Z"
          fill="#f59e0b"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        />

        {/* Duck eye */}
        <motion.circle
          cx="25"
          cy="30"
          r="5"
          fill="white"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.8, duration: 0.3 }}
        />

        <motion.circle
          cx="25"
          cy="30"
          r="2.5"
          fill="#1e293b"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 1, duration: 0.3 }}
        />

        {/* Smart glasses */}
        <motion.path
          d="M15,30 C15,25 20,25 25,25 C30,25 35,25 35,30"
          stroke="#1e293b"
          strokeWidth="2"
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.8 }}
        />

        <motion.path
          d="M35,30 L45,25"
          stroke="#1e293b"
          strokeWidth="2"
          strokeLinecap="round"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 1 }}
          transition={{ delay: 1.6, duration: 0.4 }}
        />
      </motion.svg>

      {/* Animated thinking bubbles */}
      <motion.div
        className="absolute top-0 right-0"
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 1, 0] }}
        transition={{ delay: 2, duration: 2, repeat: Number.POSITIVE_INFINITY, repeatDelay: 5 }}
      >
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="10" cy="10" r="3" fill="#10b981" opacity="0.7" />
        </svg>
      </motion.div>

      <motion.div
        className="absolute top-0 right-5"
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 1, 0] }}
        transition={{ delay: 2.2, duration: 2, repeat: Number.POSITIVE_INFINITY, repeatDelay: 5 }}
      >
        <svg width="15" height="15" viewBox="0 0 15 15" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="7.5" cy="7.5" r="2.5" fill="#10b981" opacity="0.5" />
        </svg>
      </motion.div>

      <motion.div
        className="absolute top-2 right-10"
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 1, 0] }}
        transition={{ delay: 2.4, duration: 2, repeat: Number.POSITIVE_INFINITY, repeatDelay: 5 }}
      >
        <svg width="10" height="10" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="5" cy="5" r="2" fill="#10b981" opacity="0.3" />
        </svg>
      </motion.div>
    </motion.div>
  )
}
