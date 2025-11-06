"use client"

import type React from "react"

import { useState } from "react"
import { ChevronLeft, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface Column {
  header: string
  accessor: string
  width: string
  render?: (value: any) => React.ReactNode
}

interface DataTableProps {
  columns: Column[]
  data: any[]
}

export function DataTable({ columns, data }: DataTableProps) {
  const [page, setPage] = useState(0)
  const itemsPerPage = 8
  const totalPages = Math.ceil(data.length / itemsPerPage)
  const paginatedData = data.slice(page * itemsPerPage, (page + 1) * itemsPerPage)

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-muted border-b border-border">
              {columns.map((col) => (
                <th
                  key={col.accessor}
                  className="px-4 py-3 text-left text-xs font-semibold text-muted-foreground"
                  style={{ width: col.width }}
                >
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {paginatedData.length > 0 ? (
              paginatedData.map((row, idx) => (
                <tr key={idx} className="border-b border-border hover:bg-muted/50 transition-colors">
                  {columns.map((col) => (
                    <td key={col.accessor} className="px-4 py-3 text-sm text-foreground" style={{ width: col.width }}>
                      {col.render ? col.render(row[col.accessor]) : row[col.accessor]}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-sm text-muted-foreground">
                  No records match current filters
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between px-4 py-3 border-t border-border bg-muted/50">
        <div className="text-xs text-muted-foreground">
          Showing {paginatedData.length > 0 ? page * itemsPerPage + 1 : 0}–
          {Math.min((page + 1) * itemsPerPage, data.length)} of {data.length} records
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <span className="px-2 py-1 text-xs font-medium text-muted-foreground">
            Page {page + 1} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page === totalPages - 1}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}
