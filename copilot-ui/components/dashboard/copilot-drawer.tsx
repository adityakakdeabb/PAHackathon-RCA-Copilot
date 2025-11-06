"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { X, Send, Loader } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { askCopilot, getChatResult } from "@/lib/api"
import { marked } from 'marked'

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

    try {
      // Send question to /chat endpoint
      const askResponse = await askCopilot(messageText)
      
      if (!askResponse.success) {
        throw new Error(askResponse.error || 'Failed to send question')
      }

      const result = askResponse.data

      if (!result) {
        throw new Error('Failed to get response from copilot')
      }

      // Convert Markdown to HTML using marked.parse (synchronous version)
      let htmlContent = await marked.parse(result, { 
        gfm: true, // GitHub Flavored Markdown
        breaks: true // Convert line breaks to <br>
      })
      // Add a button to create work item instead of automatically adding the banner
      const createWorkItemButton = `
        <div style="margin: 12px 0;">
          <button 
        onclick="window.createWorkItem()"
        style="
          background-color: #3b82f6; 
          color: white; 
          border: none; 
          padding: 8px 16px; 
          border-radius: 6px; 
          cursor: pointer;
          font-size: 14px;
          font-weight: 500;
        "
        onmouseover="this.style.backgroundColor='#2563eb'"
        onmouseout="this.style.backgroundColor='#3b82f6'"
          >
        Create Work Item
          </button>
        </div>
      `;
      
      htmlContent += createWorkItemButton;

      // Add global function to handle work item creation
      if (typeof window !== 'undefined') {
        (window as any).createWorkItem = () => {
          const banner = document.createElement('div');
          banner.innerHTML = `
        <div style='background-color: #dcfce7; border: 1px solid #22c55e; color: #166534; padding: 8px 12px; border-radius: 6px; margin: 8px 0;'>
          <strong>✅ Work Item Successfully Created</strong>
        </div>
          `;
          
          const button = document.querySelector('button[onclick="window.createWorkItem()"]');
          let id = ""
          if (button && button.parentNode) {
        button.parentNode.insertBefore(banner.firstElementChild!, button.nextSibling);
        button.remove();

        // Query the agent message to get the id of its parent message
        const agentMessage = button.closest('.message');
        if (agentMessage) {
          id = agentMessage.id;
          let innerHtml = agentMessage.innerHTML;
          console.log("Inner HTML:", innerHtml);
          const assistantMessage: Message = {
            id: id,
          role: "assistant",
          content: innerHtml,
      }
            setMessages((prev) => [...prev, assistantMessage])
        }


          }
        };
      }
      console.log("HTML Content:", htmlContent);
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: htmlContent,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to get response from copilot",
        variant: "destructive",
      })

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I apologize, but I encountered an error processing your request. Please try again.",
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  // Static hardcoded responses for quick action buttons (no API calls made for these)
  const staticQuickActionResponses: Record<string, string> = {
    "Ask RCA": `### Root Cause Hypothesis (Multi-Source Correlation)\n\n**Primary emerging issues** combine thermal stress, vibration escalation, and pressure instability across multiple machines. Data points:\n\n- **Live Alerts (Critical / High)**:\n  - MCH_012 – High Temperature spike (>90°C) indicates impaired cooling airflow.\n  - MCH_021 – Motor Overload (current >118A) suggests mechanical resistance / bearing degradation.\n  - MCH_045 – Unexpected shutdown triggered by vibration safety relay → acute mechanical imbalance.\n  - MCH_030 / MCH_034 – High pressure / critical temperature excursions under load.\n\n- **Sensor Trends (sample highlights)**:\n  - Repeated critical temperature excursions: MCH_034 (≥89°C), MCH_046, MCH_005, MCH_039, MCH_030.\n  - Critical vibration bursts: MCH_032 (late cycle), MCH_030, MCH_045, MCH_035, MCH_002.\n  - Pressure spikes/drops: MCH_043 & MCH_050 (≥5.8 bar), drop in MCH_034 (2.1 bar alert) suggests sealing / leakage onset.\n\n- **Operator Reports (Critical / Investigating)**:\n  - Recurrent multi-symptom machines: MCH_014 (smoke + delays), MCH_047 (pressure fluctuation), MCH_030 (oil leakage + vibration), MCH_009 (auto-shutdown + temperature).\n\n- **Maintenance Logs (patterns)**:\n  - Frequent emergency/corrective interventions for: MCH_032, MCH_030, MCH_010, MCH_014, MCH_018.\n  - Repeated actions: lubrication + alignment + bearing replacement → progressive mechanical wear & thermal inefficiency.\n  - Gearbox & cooling subsystem dominate high-downtime events (≥6h).\n\n**Likely Root Cause Cluster:**\n1. Thermal load + impaired cooling (fan belt wear / exchanger fouling) → elevated temperatures → friction rise.\n2. Mechanical imbalance (bearing wear / misalignment) → vibration surges → protective trips (e.g., MCH_045).\n3. Secondary pressure instability (valve seating & hydraulic compensation lag) under thermal + vibration stress.\n\n**Recommended Next Actions:**\n- Prioritize thermal & vibration triage: MCH_012, MCH_021, MCH_030, MCH_045.\n- Combined cooling path inspection + vibration baseline re-calibration.\n- Predictive audit: correlate time clusters of critical temperature + vibration ≥10 mm/s for pre-shutdown risk.\n- Teardown scheduling for assets with >2 emergency maint. events (MCH_030, MCH_032, MCH_014).\n\n**Confidence:** Medium-high (multi-source corroboration).\n\nAsk for a machine-specific deep dive or prevention playbook if needed.`,
    "Summarize Alerts": `### Live Alerts Summary\n\n**Totals (10 alerts):**\n- Critical: 3 (ALRT_001, ALRT_005, ALRT_010)\n- High: 3 (ALRT_002, ALRT_004, ALRT_008)\n- Medium: 3 (ALRT_003, ALRT_006, ALRT_009)\n- Low: 1 (ALRT_007)\n\n**Status Breakdown:** Open: 7 | Investigating: 3 | Closed: 0\n\n**Immediate Attention:**\n- MCH_012 – Temperature spike >90°C (cooling failure risk)\n- MCH_021 – Motor overload (repeated protection trips)\n- MCH_045 – Unexpected shutdown (vibration relay)\n\n**Emerging Risks (Investigating):**\n- Oil contamination (MCH_042) → early wear pathway\n- Sensor drift (MCH_002) → calibration integrity risk\n\n**Pattern:** Escalating thermal + vibration combination with zero resolved closures → backlog pressure increasing.\n\nAsk for filtered view (e.g. only Critical Open) if needed.`,
    "Sensor Trend": `### Sensor Trend Overview (Observed Window)\n\n**Temperature Spikes:**\n- Critical temps (≥82–90°C): MCH_034, MCH_046, MCH_005, MCH_039, MCH_030. Afternoon/evening clustering (≈14:00–19:00) → thermal accumulation / reduced cooling efficiency.\n\n**Vibration Escalation:**\n- Critical bursts (≥10 mm/s): MCH_045 (10.92), MCH_020 (11.29), MCH_005 (11.7), MCH_032 (11.91), MCH_030 (11.67), MCH_035 (10.54).\n- Late-cycle intensification suggests thermal expansion driving alignment drift.\n\n**Pressure Instability:**\n- Spikes: MCH_043 (5.84), MCH_048 (5.8), MCH_050 (5.27), MCH_030 (5.53).\n- Local drop event tied to alert for MCH_034 (2.1 bar) → valve seating / leakage suspicion.\n\n**Correlated Stress Assets:** MCH_030, MCH_005, MCH_034 show BOTH critical vibration & temperature → high failure probability.\n\n**Suggested Monitoring Rule:**\nRisk Score = (Critical Temp Count × 2) + (Critical Vibration Count × 1.5) + (Pressure anomalies). Escalate if score > 6 within 6h.\n\nI can draft a scoring function if desired.`,
    "Critical Machines": `### Critical / High-Risk Machines\n\n| Machine | Reason | Data Sources | Suggested Action |\n|---------|--------|-------------|------------------|\n| MCH_030 | Pressure & vibration critical; repeated emergency maint. | Alerts, Sensors, Maintenance | Coupling & valve integrity inspection |\n| MCH_012 | High temp alert + bearing service history | Alerts, Maintenance | Cooling airflow audit + thermal scan |\n| MCH_021 | Motor overload + alignment interventions | Alerts, Maintenance | Torque / current signature analysis |\n| MCH_045 | Shutdown via vibration relay; long downtime events | Alerts, Sensors, Maintenance | Vibration spectrum & mounting review |\n| MCH_034 | Temp & pressure variability; diagnostics repeat | Sensors, Maintenance | Heat exchanger cleaning + valve calibration |\n| MCH_032 | Multiple emergency maint.; late-cycle vibration | Sensors, Maintenance | Gearbox oil analysis + realignment |\n| MCH_014 | Smoke + corrective logs; multi-component wear | Operator, Maintenance | Bearing wear inspection + lubrication QA |\n| MCH_046 | Critical temperature + high downtime corrective tasks | Sensors, Maintenance | Hydraulic circuit & cooling integrity review |\n| MCH_005 | Critical temp + vibration spikes | Sensors | Cooling & lubrication path verification |\n\n**Priority Tier 1:** MCH_030, MCH_012, MCH_045, MCH_021\n**Tier 2:** MCH_034, MCH_032, MCH_014, MCH_046\n\nRequest remediation playbook or export if needed.`,
  }

  const quickActions = [
    { label: "Ask RCA", action: "Ask RCA: What is the root cause?", static: true },
    { label: "Summarize Alerts", action: "Summarize alerts: Give me an overview", static: true },
    { label: "Sensor Trend", action: "Explain sensor trend: Analyze recent patterns", static: true },
    { label: "Critical Machines", action: "List critical machines that need attention", static: true },
  ]

  const handleStaticQuickAction = async (label: string) => {
    const md = staticQuickActionResponses[label]
    if (!md) return
    const html = await marked.parse(md, { gfm: true, breaks: true })
    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: html,
    }
    setMessages((prev) => [
      ...prev,
      { id: Date.now().toString(), role: "user", content: label },
      assistantMessage,
    ])
  }

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
                className={`max-w-xs rounded-lg px-4 py-2 text-sm prose prose-sm ${
                  msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
                }`}
              >
                {msg.role === "user" ? (
                  msg.content
                ) : (
                  <div id={msg.id} dangerouslySetInnerHTML={{ __html: msg.content }} />
                )}
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

        {/* Quick Actions (persist after first use) */}
        <div className="px-4 py-3 border-t border-border space-y-2">
          <p className="text-xs text-muted-foreground font-medium">Quick actions:</p>
          <div className="grid grid-cols-2 gap-2">
            {quickActions.map((action) => (
              <Button
                key={action.label}
                variant="outline"
                size="sm"
                className="text-xs bg-transparent"
                onClick={() => action.static ? handleStaticQuickAction(action.label) : handleSendMessage(action.action)}
              >
                {action.label}
              </Button>
            ))}
          </div>
        </div>

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
