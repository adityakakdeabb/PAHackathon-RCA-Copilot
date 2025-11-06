"use client"

import { useMockData } from "@/lib/mock-data"
import { AlertCircle, Activity, FileText, Wrench, Clock, TrendingUp } from "lucide-react"
import { Card } from "@/components/ui/card"

export function KPISummary() {
  const { sensors, operatorReports, alerts } = useMockData()

  const totalMachines = new Set(sensors.map((s) => s.machine_id)).size
  const activeAlerts = alerts.filter((a) => a.status !== "resolved").length
  const criticalAlerts = alerts.filter((a) => a.severity === "Critical").length
  const openReports = operatorReports.filter((r) => r.status !== "resolved").length
  const lastUpdate = new Date().toLocaleTimeString()

  const kpis = [
    {
      label: "Machines Monitored",
      value: totalMachines,
      icon: Activity,
      color: "text-primary",
      bgColor: "bg-primary/10",
      trend: "+2%",
    },
    {
      label: "Active Alerts",
      value: activeAlerts,
      sublabel: `${criticalAlerts} Critical`,
      icon: AlertCircle,
      color: "text-destructive",
      bgColor: "bg-destructive/10",
      trend: "-5%",
    },
    {
      label: "Open Reports",
      value: openReports,
      icon: FileText,
      color: "text-secondary",
      bgColor: "bg-secondary/10",
      trend: "+1%",
    },
    {
      label: "Pending Maintenance",
      value: 12,
      icon: Wrench,
      color: "text-accent",
      bgColor: "bg-accent/10",
      trend: "+3%",
    },
  ]

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon
          return (
            <Card
              key={kpi.label}
              className={`p-4 border border-border hover:border-primary/40 transition-all duration-200 ${kpi.bgColor} hover:shadow-md`}
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-muted-foreground font-medium">{kpi.label}</p>
                  <p className="text-2xl font-bold text-foreground mt-2">{kpi.value}</p>
                  {kpi.sublabel && <p className="text-xs text-destructive font-semibold mt-1">{kpi.sublabel}</p>}
                  <div className="flex items-center gap-1 mt-2">
                    <TrendingUp className="w-3 h-3 text-primary" />
                    <span className="text-xs text-primary font-medium">{kpi.trend}</span>
                  </div>
                </div>
                <Icon className={`w-6 h-6 ${kpi.color}`} />
              </div>
            </Card>
          )
        })}
      </div>
      <div className="flex items-center justify-end text-xs text-muted-foreground">
        <Clock className="w-3 h-3 mr-1" />
        Last update: {lastUpdate}
      </div>
    </div>
  )
}
