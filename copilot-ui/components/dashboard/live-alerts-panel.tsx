"use client"

import { useState, useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RefreshCw, Download, Info, Zap, AlertTriangle, CheckCircle, Loader } from "lucide-react"
import { useMockData } from "@/lib/mock-data"
import { DataTable } from "./data-table"
import { getRCA } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

interface LiveAlertsPanelProps {
  onGenerateRCA: (alert: any) => void
}

export function LiveAlertsPanel({ onGenerateRCA }: LiveAlertsPanelProps) {
  const { alerts } = useMockData()
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [loading, setLoading] = useState<string | null>(null)
  const { toast } = useToast()

  const filteredData = useMemo(() => {
    return alerts.filter((item) => {
      if (selectedSeverity !== "all" && item.severity !== selectedSeverity) return false
      if (selectedStatus !== "all" && item.status !== selectedStatus) return false
      return true
    })
  }, [alerts, selectedSeverity, selectedStatus])

  const getSeverityBadge = (severity: string) => {
    /* Updated severity badge colors to be more vibrant and interactive */
    const colors: Record<string, string> = {
      Critical: "bg-red-100 text-red-800 border border-red-300",
      High: "bg-orange-100 text-orange-800 border border-orange-300",
      Medium: "bg-yellow-100 text-yellow-800 border border-yellow-300",
      Low: "bg-blue-100 text-blue-800 border border-blue-300",
    }
    return colors[severity] || "bg-gray-100"
  }

  const getStatusIcon = (status: string) => {
    /* Added status icons */
    return status === "active" ? <AlertTriangle className="w-4 h-4" /> : <CheckCircle className="w-4 h-4" />
  }

  const columns = [
    { header: "Alert ID", accessor: "alert_id", width: "12%" },
    { header: "Machine", accessor: "machine_id", width: "12%" },
    { header: "Timestamp", accessor: "timestamp", width: "15%" },
    { header: "Type", accessor: "alert_type", width: "13%" },
    {
      header: "Severity",
      accessor: "severity",
      width: "12%",
      render: (severity: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getSeverityBadge(severity)}`}>{severity}</span>
      ),
    },
    {
      header: "Status",
      accessor: "status",
      width: "12%",
      render: (status: string) => (
        <span
          className={`px-2 py-1 rounded-full text-xs font-semibold flex items-center gap-1 w-fit ${
            status === "active"
              ? "bg-red-100 text-red-800 border border-red-300"
              : "bg-green-100 text-green-800 border border-green-300"
          }`}
        >
          {getStatusIcon(status)}
          {status}
        </span>
      ),
    },
    {
      header: "Action",
      accessor: "alert_id",
      width: "12%",
      render: (alertId: string) => {
        const alert = filteredData.find((a) => a.alert_id === alertId);
        return (
          <Button
            variant="outline"
            size="sm"
            onClick={async () => {
              if (!alert) return;
              
              setLoading(alertId);
              const result = await getRCA(alert.alert_description);
              setLoading(null);

              if (result.success && result.data) {
                onGenerateRCA(alert);
              } else {
                toast({
                  title: "Error generating RCA",
                  description: result.error || "Failed to generate RCA. Please try again.",
                  variant: "destructive",
                });
              }
            }}
            disabled={loading === alertId}
            title="Generate RCA for this alert"
            className="hover:bg-primary/10 hover:border-primary/40 hover:text-primary transition-all duration-200"
          >
            {loading === alertId ? (
              <Loader className="w-3 h-3 mr-1 animate-spin" />
            ) : (
              <Zap className="w-3 h-3 mr-1" />
            )}
            RCA
          </Button>
        );
      },
    },
  ]

  return (
    <Card className="p-6 border border-border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-foreground">Live Alerts</h2>
          <button
            className="text-muted-foreground hover:text-primary transition-colors"
            title="Real-time actionable alerts from monitoring systems"
          >
            <Info className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="hover:bg-primary/10 hover:border-primary/40 bg-transparent">
            <RefreshCw className="w-3 h-3 mr-1" />
            Refresh
          </Button>
          <Button variant="outline" size="sm" className="hover:bg-accent/10 hover:border-accent/40 bg-transparent">
            <Download className="w-3 h-3 mr-1" />
            Export
          </Button>
        </div>
      </div>

      <div className="flex gap-3 mb-4 flex-wrap">
        <Select value={selectedSeverity} onValueChange={setSelectedSeverity}>
          <SelectTrigger className="w-40 hover:border-primary/40">
            <SelectValue placeholder="All Severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severity</SelectItem>
            <SelectItem value="Critical">Critical</SelectItem>
            <SelectItem value="High">High</SelectItem>
            <SelectItem value="Medium">Medium</SelectItem>
            <SelectItem value="Low">Low</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger className="w-40 hover:border-primary/40">
            <SelectValue placeholder="All Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <DataTable columns={columns} data={filteredData} />
    </Card>
  )
}
