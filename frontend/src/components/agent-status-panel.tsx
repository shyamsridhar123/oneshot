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
} from "lucide-react";

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

export function AgentStatusPanel() {
  const { agentStates } = useStore();

  const activeAgents = Object.values(agentStates).filter(
    (a) => a.status !== "idle"
  );

  return (
    <aside className="hidden xl:flex w-72 flex-col border-l bg-card fixed top-0 right-0 h-screen z-40">
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
            if (!config) return null; // Skip unknown agents
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
  );
}
