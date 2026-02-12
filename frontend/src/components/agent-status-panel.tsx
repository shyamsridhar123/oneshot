"use client";

import { useStore } from "@/lib/store";
import type { AgentName, AgentStatusType } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Brain,
  Search,
  TrendingUp,
  FileEdit,
  Users,
  Database,
  GitBranch,
  Wrench,
  Plug,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const agentConfig: Record<
  AgentName,
  { label: string; icon: React.ComponentType<{ className?: string }>; color: string }
> = {
  orchestrator: { label: "Orchestrator", icon: GitBranch, color: "text-purple-500" },
  strategist: { label: "Strategist", icon: Brain, color: "text-blue-500" },
  researcher: { label: "Researcher", icon: Search, color: "text-green-500" },
  analyst: { label: "Analyst", icon: TrendingUp, color: "text-orange-500" },
  scribe: { label: "Scribe", icon: FileEdit, color: "text-pink-500" },
  advisor: { label: "Advisor", icon: Users, color: "text-cyan-500" },
  memory: { label: "Memory", icon: Database, color: "text-yellow-500" },
};

const statusColors: Record<AgentStatusType, string> = {
  idle: "bg-muted text-muted-foreground",
  thinking: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
  executing: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  waiting: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200",
  completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
  error: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
};

const TOOL_LABELS: Record<string, string> = {
  search_web: "Web Search",
  search_news: "News Search",
  search_trends: "Trend Search",
  analyze_hashtags: "Hashtags",
  search_competitor_content: "Competitors",
  fetch_mcp: "Fetch (MCP)",
  filesystem_mcp: "File Save (MCP)",
  get_brand_guidelines: "Brand Guide",
  get_past_posts: "Past Posts",
  get_content_calendar: "Calendar",
  search_knowledge_base: "Knowledge",
  calculate_engagement_metrics: "Metrics",
  recommend_posting_schedule: "Schedule",
};

export function AgentStatusPanel() {
  const { agentStates } = useStore();
  const [collapsed, setCollapsed] = useState(false);

  const activeAgents = Object.values(agentStates).filter(
    (a) => a.status !== "idle"
  );

  return (
    <>
      {/* Toggle button — visible on md+ screens */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setCollapsed(!collapsed)}
        className="hidden md:flex fixed top-20 right-0 z-50 h-8 w-8 rounded-l-md rounded-r-none border border-r-0 bg-card shadow-sm"
        aria-label={collapsed ? "Show agent panel" : "Hide agent panel"}
      >
        {collapsed ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
      </Button>

      <aside
        className={cn(
          "hidden md:flex flex-col border-l bg-card fixed top-0 right-0 h-screen z-40 transition-all duration-200",
          collapsed ? "w-0 overflow-hidden border-l-0" : "w-72"
        )}
      >
        <div className="flex h-16 items-center border-b px-4">
          <h2 className="font-semibold">Agent Activity</h2>
          {activeAgents.length > 0 && (
            <Badge variant="secondary" className="ml-auto">
              {activeAgents.length} active
            </Badge>
          )}
        </div>

        <ScrollArea className="flex-1 p-4">
          <div className="space-y-3">
            {Object.entries(agentStates).map(([name, state]) => {
              const config = agentConfig[name as AgentName];
              if (!config) return null;
              const Icon = config.icon;

              return (
                <div
                  key={name}
                  className={cn(
                    "rounded-lg border p-3 transition-all",
                    state.status !== "idle" && "border-primary/50 bg-primary/5"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <Icon className={cn("h-4 w-4", config.color)} />
                    <span className="text-sm font-medium">{config.label}</span>
                    <Badge
                      variant="outline"
                      className={cn("ml-auto text-xs", statusColors[state.status])}
                    >
                      {state.status}
                    </Badge>
                  </div>

                  {state.current_task && (
                    <p className="mt-2 text-xs text-muted-foreground line-clamp-2">
                      {state.current_task}
                    </p>
                  )}

                  {/* Tool call chips */}
                  {state.tool_calls.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {state.tool_calls.map((tc, i) => (
                        <span
                          key={`${tc.name}-${i}`}
                          className={cn(
                            "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium",
                            tc.type === "mcp"
                              ? "bg-violet-100 text-violet-700 dark:bg-violet-900 dark:text-violet-300"
                              : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300"
                          )}
                        >
                          {tc.type === "mcp" ? (
                            <Plug className="h-2.5 w-2.5" />
                          ) : (
                            <Wrench className="h-2.5 w-2.5" />
                          )}
                          {TOOL_LABELS[tc.name] || tc.name}
                        </span>
                      ))}
                    </div>
                  )}

                  {state.status === "thinking" && (
                    <div className="mt-2 flex gap-1">
                      <span className="animate-pulse h-1.5 w-1.5 rounded-full bg-yellow-500" />
                      <span className="animate-pulse h-1.5 w-1.5 rounded-full bg-yellow-500 delay-150" />
                      <span className="animate-pulse h-1.5 w-1.5 rounded-full bg-yellow-500 delay-300" />
                    </div>
                  )}

                  {state.status === "executing" && (
                    <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-muted">
                      <div className="h-full w-1/3 animate-pulse rounded-full bg-blue-500" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </aside>
    </>
  );
}
