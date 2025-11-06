"use client"

import { useState, useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RefreshCw, Download, Info } from "lucide-react"
import { useMockData } from "@/lib/mock-data"
import { DataTable } from "./data-table"

export function SensorDataPanel() {
  const { sensors } = useMockData()
  const [selectedMachine, setSelectedMachine] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")
  const [searchValue, setSearchValue] = useState("")
  const [page, setPage] = useState(0)

  const machines = useMemo(() => [...new Set(sensors.map((s) => s.machine_id))], [sensors])

  const filteredData = useMemo(() => {
    return sensors.filter((item) => {
      if (selectedMachine !== "all" && item.machine_id !== selectedMachine) return false
      if (selectedStatus !== "all" && item.status !== selectedStatus) return false
      return true
    })
  }, [sensors, selectedMachine, selectedStatus])

  const columns = [
    { header: "Timestamp", accessor: "timestamp", width: "20%" },
    { header: "Machine ID", accessor: "machine_id", width: "15%" },
    { header: "Sensor Type", accessor: "sensor_type", width: "15%" },
    {
      header: "Value",
      accessor: "sensor_value",
      width: "12%",
      render: (value: number) => <span className="font-mono">{value.toFixed(2)}</span>,
    },
    { header: "Unit", accessor: "unit", width: "10%" },
    {
      header: "Status",
      accessor: "status",
      width: "15%",
      render: (status: string) => {
        const colors: Record<string, string> = {
          Normal: "bg-green-100 text-green-800",
          Warning: "bg-yellow-100 text-yellow-800",
          Critical: "bg-red-100 text-red-800",
        }
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || "bg-gray-100"}`}>
            {status}
          </span>
        )
      },
    },
  ]

  return (
    <Card className="p-6 border border-border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-foreground">Real-Time Sensor Stream</h2>
          <button
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="Shows live sensor data from all machines"
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
        <Select value={selectedMachine} onValueChange={setSelectedMachine}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="All Machines" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Machines</SelectItem>
            {machines.map((m) => (
              <SelectItem key={m} value={m}>
                {m}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={selectedStatus} onValueChange={setSelectedStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="All Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="Normal">Normal</SelectItem>
            <SelectItem value="Warning">Warning</SelectItem>
            <SelectItem value="Critical">Critical</SelectItem>
          </SelectContent>
        </Select>

        <Input
          placeholder="Search..."
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
          className="w-40"
        />
      </div>

      <DataTable columns={columns} data={filteredData} />
    </Card>
  )
}
