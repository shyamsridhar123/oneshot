"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  FileText,
  BarChart3,
  Menu,
  X,
  BookOpen,
  Search,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useStore } from "@/lib/store";
import { ThemeToggle } from "@/components/theme-toggle";

const navigation = [
  { name: "Chat", href: "/chat", icon: MessageSquare, gradient: "from-violet-500 to-blue-500" },
  { name: "Content", href: "/proposals", icon: FileText, gradient: "from-pink-500 to-rose-500" },
  { name: "Trends", href: "/research", icon: Search, gradient: "from-emerald-500 to-teal-500" },
  { name: "Brand", href: "/knowledge", icon: BookOpen, gradient: "from-amber-500 to-orange-500" },
  { name: "Analytics", href: "/analytics", icon: BarChart3, gradient: "from-cyan-500 to-blue-500" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isSidebarOpen, toggleSidebar } = useStore();

  return (
    <>
      {/* Mobile toggle */}
      <Button
        variant="ghost"
        size="icon"
        className="fixed top-4 left-4 z-50 lg:hidden rounded-xl border border-white/[0.08] bg-card/80 backdrop-blur-xl shadow-lg"
        onClick={toggleSidebar}
      >
        {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
      </Button>

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-white/[0.06] bg-card/30 backdrop-blur-md transition-transform duration-300 lg:translate-x-0",
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <Link href="/" className="group flex h-14 shrink-0 items-center gap-3 border-b border-white/[0.06] px-5 transition-colors hover:bg-white/[0.02]">
          <div className="relative">
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-violet-500 to-cyan-400 opacity-30 blur-[6px] group-hover:opacity-50 transition-opacity" />
            <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 via-blue-500 to-cyan-400 text-sm font-bold text-white shadow-lg shadow-violet-500/20">
              O
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold tracking-tight text-foreground/90">OneShot</span>
            <span className="text-[10px] text-muted-foreground/50 font-medium">AI Content Platform</span>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 p-3 pt-4">
          <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/40">
            Workspace
          </p>
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-violet-500/10 border border-violet-500/20 text-foreground shadow-sm shadow-violet-500/5"
                    : "border border-transparent text-muted-foreground/70 hover:bg-white/[0.04] hover:border-white/[0.06] hover:text-foreground/90"
                )}
              >
                {/* Active indicator bar */}
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-0.5 rounded-full bg-gradient-to-b from-violet-400 to-blue-400" />
                )}
                {/* Icon with gradient background */}
                <div
                  className={cn(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg transition-colors",
                    isActive
                      ? `bg-gradient-to-br ${item.gradient} text-white shadow-md`
                      : "bg-white/[0.04] text-muted-foreground/60 group-hover:bg-white/[0.08] group-hover:text-foreground/70"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                </div>
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-white/[0.06] p-3">
          {/* Theme toggle row */}
          <div className="flex items-center justify-between rounded-xl px-3 py-2 hover:bg-white/[0.04] transition-colors">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/[0.04]">
                <Sparkles className="h-3.5 w-3.5 text-muted-foreground/50" />
              </div>
              <span className="text-xs font-medium text-muted-foreground/60">Theme</span>
            </div>
            <ThemeToggle />
          </div>

          {/* Branding */}
          <div className="mt-2 rounded-xl bg-white/[0.02] border border-white/[0.04] px-4 py-3">
            <p className="text-[10px] font-medium text-muted-foreground/50">
              OneShot by NotContosso Inc.
            </p>
            <p className="text-[10px] text-muted-foreground/30 mt-0.5">
              Multi-Agent Content Platform
            </p>
          </div>
        </div>
      </aside>
    </>
  );
}
