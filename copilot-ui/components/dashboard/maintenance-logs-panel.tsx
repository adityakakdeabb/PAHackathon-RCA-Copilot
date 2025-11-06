"use client"

import { useMemo } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { RefreshCw, Download, Info } from "lucide-react"
import { useMockData } from "@/lib/mock-data"

export function MaintenanceLogsPanel() {
  const { maintenanceLogs } = useMockData()

  // Dynamically derive categories from maintenance log remarks
  const categories = useMemo(() => {
    const categoryMap: Record<string, { count: number; items: string[]; color: string; tag: string }> = {}

    const keywords: Record<string, { tag: string; color: string }> = {
      wear: { tag: "Minor wear", color: "bg-slate-100 text-slate-800" },
      awaiting: { tag: "Awaiting parts", color: "bg-amber-100 text-amber-800" },
      restored: { tag: "Resolved / restored", color: "bg-green-100 text-green-800" },
      temperature: { tag: "Temperature stability improved", color: "bg-blue-100 text-blue-800" },
      pressure: { tag: "Pressure fluctuation resolved", color: "bg-cyan-100 text-cyan-800" },
      vibration: { tag: "Vibration issue fixed", color: "bg-purple-100 text-purple-800" },
    }

    maintenanceLogs.forEach((log) => {
      const remark = log.remarks.toLowerCase()
      let matched = false

      for (const [key, { tag, color }] of Object.entries(keywords)) {
        if (remark.includes(key)) {
          if (!categoryMap[tag]) {
            categoryMap[tag] = { count: 0, items: [], color, tag }
          }
          categoryMap[tag].count += 1
          categoryMap[tag].items.push(log.remarks)
          matched = true
          break
        }
      }

      if (!matched) {
        const tag = "Other"
        if (!categoryMap[tag]) {
          categoryMap[tag] = { count: 0, items: [], color: "bg-gray-100 text-gray-800", tag }
        }
        categoryMap[tag].count += 1
        categoryMap[tag].items.push(log.remarks)
      }
    })

    return Object.values(categoryMap)
  }, [maintenanceLogs])

  return (
    <Card className="p-6 border border-border">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-lg font-semibold text-foreground">Maintenance Log Insights</h2>
          <button
            className="text-muted-foreground hover:text-foreground transition-colors"
            title="Categorized maintenance activities"
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

      <div className="space-y-4">
        {categories.map((category) => (
          <div key={category.tag} className="border border-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${category.color}`}>{category.tag}</span>
                <span className="text-sm font-semibold text-foreground">{category.count} items</span>
              </div>
            </div>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {category.items.slice(0, 3).map((item, idx) => (
                <p key={idx} className="text-sm text-muted-foreground line-clamp-1">
                  {item}
                </p>
              ))}
              {category.items.length > 3 && (
                <p className="text-xs text-primary font-medium">+{category.items.length - 3} more</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
