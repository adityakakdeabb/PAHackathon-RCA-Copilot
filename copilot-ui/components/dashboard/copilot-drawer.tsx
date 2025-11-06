"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { X, Send, Loader } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface CopilotDrawerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialAlert?: any
}

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  loading?: boolean
}

export function CopilotDrawer({ open, onOpenChange, initialAlert }: CopilotDrawerProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your RCA Copilot. I can help you analyze incidents, summarize alerts, and provide insights on sensor trends. What would you like to explore?",
    },
  ])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const messagesEnd = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  const scrollToBottom = () => {
    messagesEnd.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    if (initialAlert && open) {
      const alertText = `Analyze alert for machine ${initialAlert.machine_id}: ${initialAlert.alert_description}`
      handleSendMessage(alertText)
    }
  }, [initialAlert, open])

  const handleSendMessage = async (text?: string) => {
    const messageText = text || input.trim()
    if (!messageText) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: messageText,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setLoading(true)

    // Simulate API call with delay
    setTimeout(() => {
      const responses: Record<string, string> = {
        "ask rca":
          "Based on the available data, the root cause analysis suggests: 1) Check sensor calibration, 2) Review recent maintenance logs, 3) Correlate with operator reports.",
        "summarize alerts":
          "Current alert summary: 3 Critical, 5 High priority, 2 Medium priority. Most common: Temperature fluctuations in Machine-02.",
        "explain sensor trend":
          "Sensor trend shows gradual increase over the past 6 hours. This may indicate wear or calibration drift. Recommend preventive maintenance.",
        "list critical machines":
          "Critical machines: Machine-02 (3 alerts), Machine-05 (2 alerts), Machine-08 (1 alert). Machine-02 requires immediate attention.",
      }

      let response =
        "I received your request. Please provide more specific details or use one of the quick actions below."

      for (const [key, value] of Object.entries(responses)) {
        if (messageText.toLowerCase().includes(key)) {
          response = value
          break
        }
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response,
      }

      setMessages((prev) => [...prev, assistantMessage])
      setLoading(false)
    }, 500)
  }

  const quickActions = [
    { label: "Ask RCA", action: "Ask RCA: What is the root cause?" },
    { label: "Summarize Alerts", action: "Summarize alerts: Give me an overview" },
    { label: "Sensor Trend", action: "Explain sensor trend: Analyze recent patterns" },
    { label: "Critical Machines", action: "List critical machines that need attention" },
  ]

  if (!open) return null

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 z-40" onClick={() => onOpenChange(false)} />

      {/* Drawer */}
      <div
        className="fixed right-0 top-0 h-screen w-full max-w-md bg-card border-l border-border shadow-lg z-50 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h3 className="font-semibold text-foreground">RCA Copilot</h3>
          <button
            onClick={() => onOpenChange(false)}
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-xs rounded-lg px-4 py-2 text-sm ${
                  msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-muted rounded-lg px-4 py-3 flex items-center gap-2 text-sm text-muted-foreground">
                <Loader className="w-4 h-4 animate-spin" />
                Analyzing...
              </div>
            </div>
          )}

          <div ref={messagesEnd} />
        </div>

        {/* Quick Actions */}
        {messages.length === 1 && (
          <div className="px-4 py-3 border-t border-border space-y-2">
            <p className="text-xs text-muted-foreground font-medium">Quick actions:</p>
            <div className="grid grid-cols-2 gap-2">
              {quickActions.map((action) => (
                <Button
                  key={action.label}
                  variant="outline"
                  size="sm"
                  className="text-xs bg-transparent"
                  onClick={() => handleSendMessage(action.action)}
                >
                  {action.label}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-border space-y-3">
          <div className="flex gap-2">
            <Input
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
              disabled={loading}
            />
            <Button size="icon" onClick={() => handleSendMessage()} disabled={loading || !input.trim()}>
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">Tip: Use Alt+C to toggle copilot. ESC to close.</p>
        </div>
      </div>
    </>
  )
}
