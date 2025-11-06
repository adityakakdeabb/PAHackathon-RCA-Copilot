"use client"

import { useState, useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RefreshCw, Download, Info } from "lucide-react"
import { useMockData } from "@/lib/mock-data"
import { DataTable } from "./data-table"

export function OperatorReportsPanel() {
  const { operatorReports } = useMockData()
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [expandedRow, setExpandedRow] = useState<string | null>(null)

  const filteredData = useMemo(() => {
    return operatorReports.filter((item) => {
      if (selectedSeverity !== "all" && item.severity !== selectedSeverity) return false
      if (selectedStatus !== "all" && item.status !== selectedStatus) return false
      return true
    })
  }, [operatorReports, selectedSeverity, selectedStatus])

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      Low: "bg-blue-100 text-blue-800",
      Medium: "bg-yellow-100 text-yellow-800",
      High: "bg-orange-100 text-orange-800",
      Critical: "bg-red-100 text-red-800",
    }
    return colors[severity] || "bg-gray-100"
  }

  const columns = [
    { header: "Report ID", accessor: "report_id", width: "12%" },
    { header: "Machine", accessor: "machine_id", width: "12%" },
    { header: "Operator", accessor: "operator_name", width: "12%" },
    { header: "Date", accessor: "date", width: "12%" },
    { header: "Shift", accessor: "shift", width: "10%" },
    {
      header: "Severity",
      accessor: "severity",
      width: "15%",
      render: (severity: string) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(severity)}`}>{severity}</span>
      ),
    },
    {
      header: "Status",
      accessor: "status",
      width: "12%",
      render: (status: string) => (
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            status === "resolved" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
          }`}
        >
          {status}
        </span>
      ),
    },
  ]

  return (
    <Card className="p-6 border border-border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-foreground">Operator Incident Reports</h2>
          <button
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="Incidents reported by operators during shifts"
          >
            <Info className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="w-3 h-3 mr-1" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-3 h-3 mr-1" />
            Export
          </Button>
        </div>
      </div>

      <div className="flex gap-3 mb-4 flex-wrap">
        <Select value={selectedSeverity} onValueChange={setSelectedSeverity}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="All Severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severity</SelectItem>
            <SelectItem value="Low">Low</SelectItem>
            <SelectItem value="Medium">Medium</SelectItem>
            <SelectItem value="High">High</SelectItem>
            <SelectItem value="Critical">Critical</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="All Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <DataTable columns={columns} data={filteredData} />
    </Card>
  )
}
