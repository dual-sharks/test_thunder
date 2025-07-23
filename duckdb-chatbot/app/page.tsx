"use client"

import { useState, useRef, useEffect } from "react"
import { useChat } from "@ai-sdk/react"
import { motion, AnimatePresence } from "framer-motion"
import { Sparkles, Send, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { DuckLogo } from "@/components/duck-logo"
import { DuckAnimation } from "@/components/duck-animation"

export default function ChatInterface() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: "/api/chat",
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [showWelcome, setShowWelcome] = useState(true)

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  // Hide welcome message after first user message
  useEffect(() => {
    if (messages.length > 0 && messages[0].role === "user") {
      setShowWelcome(false)
    }
  }, [messages])

  return (
    <div className="flex flex-col min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Header */}
      <motion.header
        className="p-4 border-b border-slate-700"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center justify-between max-w-5xl mx-auto">
          <div className="flex items-center gap-3">
            <DuckLogo size={48} />
            <div>
              <h1 className="text-xl font-bold text-white">DuckDB Chat Explorer</h1>
              <p className="text-slate-400 text-sm">Ask your data anything</p>
            </div>
          </div>
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button variant="outline" className="gap-2 text-emerald-400 border-emerald-400/30 bg-transparent">
              <BarChart3 className="h-4 w-4" />
              <span>Data Insights</span>
            </Button>
          </motion.div>
        </div>
      </motion.header>

      {/* Main chat area */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full max-w-5xl mx-auto p-4 overflow-y-auto">
          {/* Welcome message */}
          <AnimatePresence>
            {showWelcome && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.5 }}
                className="mb-8 p-6 rounded-lg bg-slate-800/50 backdrop-blur-sm border border-slate-700"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-full bg-emerald-500/20">
                    <Sparkles className="h-6 w-6 text-emerald-400" />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-white mb-2">Welcome to DuckDB Chat Explorer</h2>
                    <p className="text-slate-300">
                      Ask me anything about your data! I can help you explore and analyze your DuckDB database through
                      natural conversation.
                    </p>
                    <div className="mt-4 flex flex-wrap gap-2">
                      {["Show me sales trends", "Analyze customer data", "Compare quarterly results"].map(
                        (suggestion) => (
                          <motion.button
                            key={suggestion}
                            whileHover={{ scale: 1.03 }}
                            whileTap={{ scale: 0.97 }}
                            className="px-3 py-1.5 rounded-full bg-slate-700/50 text-sm text-slate-300 hover:bg-slate-700 transition-colors"
                            onClick={() => {
                              handleInputChange({ target: { value: suggestion } } as any)
                              setTimeout(() => {
                                const form = document.querySelector("form")
                                if (form) form.dispatchEvent(new Event("submit", { cancelable: true, bubbles: true }))
                              }, 100)
                            }}
                          >
                            {suggestion}
                          </motion.button>
                        ),
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Chat messages */}
          <div className="space-y-6">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl p-4 ${
                      message.role === "user"
                        ? "bg-emerald-500 text-white"
                        : "bg-slate-800 border border-slate-700 text-slate-200"
                    }`}
                  >
                    {message.content}

                    {/* If the message contains data visualization, we could render it here */}
                    {message.role === "assistant" && message.content.includes("data") && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        transition={{ delay: 0.3 }}
                        className="mt-4 p-3 bg-slate-900/50 rounded-lg border border-slate-700"
                      >
                        <div className="h-40 flex items-center justify-center">
                          <div className="text-center text-slate-400">
                            <BarChart3 className="h-10 w-10 mx-auto mb-2 opacity-50" />
                            <p>Data visualization would appear here</p>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Loading indicator */}
            <AnimatePresence>
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  className="flex justify-start"
                >
                  <div className="max-w-[80%] rounded-2xl p-4 bg-slate-800 border border-slate-700">
                    <div className="flex items-center gap-2">
                      <div className="flex space-x-1">
                        {[0, 1, 2].map((dot) => (
                          <motion.div
                            key={dot}
                            className="h-2 w-2 rounded-full bg-emerald-400"
                            animate={{ opacity: [0.4, 1, 0.4] }}
                            transition={{
                              duration: 1.5,
                              repeat: Number.POSITIVE_INFINITY,
                              delay: dot * 0.2,
                              ease: "easeInOut",
                            }}
                          />
                        ))}
                      </div>
                      <span className="text-slate-400 text-sm">Analyzing data...</span>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Input area */}
      <motion.div
        className="border-t border-slate-700 bg-slate-900/80 backdrop-blur-sm p-4"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <form onSubmit={handleSubmit} className="max-w-5xl mx-auto flex gap-2">
          <Input
            value={input}
            onChange={handleInputChange}
            placeholder="Ask about your data..."
            className="flex-1 bg-slate-800 border-slate-700 text-white placeholder:text-slate-400 focus-visible:ring-emerald-500"
          />
          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-emerald-500 hover:bg-emerald-600 text-white"
            >
              <Send className="h-4 w-4" />
              <span className="sr-only">Send</span>
            </Button>
          </motion.div>
        </form>
      </motion.div>

      {/* Duck mascot animation */}
      <DuckAnimation />
    </div>
  )
}
