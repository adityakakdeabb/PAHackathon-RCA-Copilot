"use client"
import { Menu, Settings, Filter, Bot } from "lucide-react"
import { Button } from "@/components/ui/button"
import Image from "next/image"

interface HeaderProps {
  onCopilotClick: () => void
}

export function Header({ onCopilotClick }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 bg-card border-b border-border shadow-sm">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <Image src="/logo.png" alt="RCA Copilot Logo" width={40} height={40} className="object-contain" />
          <h1 className="text-xl font-bold text-foreground">RCA Copilot Dashboard</h1>
        </div>

        <nav className="hidden md:flex items-center gap-1">
          {["Dashboard", "Alerts", "Reports", "Settings"].map((item) => (
            <button
              key={item}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                item === "Dashboard"
                  ? "bg-primary/15 text-primary shadow-sm"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted hover:shadow-sm"
              }`}
            >
              {item}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            title="Global filters (Ctrl+K)"
            className="hover:bg-primary/10 hover:border-primary/30 bg-transparent"
          >
            <Filter className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={onCopilotClick}
            title="Copilot (Alt+C)"
            className="hover:bg-secondary/10 hover:border-secondary/30 bg-transparent"
          >
            <Bot className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="icon" className="hover:bg-accent/10 hover:border-accent/30 bg-transparent">
            <Settings className="w-4 h-4" />
          </Button>
          <Button variant="outline" size="icon" className="md:hidden bg-transparent hover:bg-muted">
            <Menu className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </header>
  )
}
