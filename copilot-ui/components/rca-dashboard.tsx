"use client"

import { useState, useEffect } from "react"
import { Header } from "./dashboard/header"
import { KPISummary } from "./dashboard/kpi-summary"
import { SensorDataPanel } from "./dashboard/sensor-data-panel"
import { OperatorReportsPanel } from "./dashboard/operator-reports-panel"
import { MaintenanceLogsPanel } from "./dashboard/maintenance-logs-panel"
import { LiveAlertsPanel } from "./dashboard/live-alerts-panel"
import { CopilotDrawer } from "./dashboard/copilot-drawer"
import { useToast } from "@/hooks/use-toast"

export function RCACopilotDashboard() {
  const [copilotOpen, setCopilotOpen] = useState(false)
  const [selectedAlert, setSelectedAlert] = useState(null)
  const { toast } = useToast()

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === "k") {
        e.preventDefault()
        // Focus global search (placeholder)
      }
      if (e.altKey && e.key === "c") {
        e.preventDefault()
        setCopilotOpen((prev) => !prev)
      }
      if (e.key === "r") {
        e.preventDefault()
        // Refresh active panel (placeholder)
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  const handleGenerateRCA = (alert: any) => {
    setSelectedAlert(alert)
    setCopilotOpen(true)
  }

  return (
    <div className="min-h-screen bg-background">
      <Header onCopilotClick={() => setCopilotOpen(!copilotOpen)} />

      <main className="p-6 space-y-6">
        <KPISummary />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SensorDataPanel />
          <OperatorReportsPanel />
          <MaintenanceLogsPanel />
          <LiveAlertsPanel onGenerateRCA={handleGenerateRCA} />
        </div>
      </main>

      <CopilotDrawer open={copilotOpen} onOpenChange={setCopilotOpen} initialAlert={selectedAlert} />
    </div>
  )
}
