"use client";

import { Clock, Zap, ExternalLink, Database, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";
import type { AgentTrace, Citation, ToolCallRecord } from "@/lib/types";

const AGENT_COLORS: Record<string, string> = {
  orchestrator: "bg-violet-500",
  researcher: "bg-emerald-500",
  strategist: "bg-blue-500",
  analyst: "bg-orange-500",
  memory: "bg-yellow-500",
  scribe: "bg-pink-500",
  advisor: "bg-cyan-500",
};

const AGENT_BAR_COLORS: Record<string, string> = {
  orchestrator: "from-violet-500/60 to-purple-500/60",
  researcher: "from-emerald-500/60 to-teal-500/60",
  strategist: "from-blue-500/60 to-indigo-500/60",
  analyst: "from-orange-500/60 to-amber-500/60",
  memory: "from-yellow-500/60 to-orange-500/60",
  scribe: "from-pink-500/60 to-rose-500/60",
  advisor: "from-cyan-500/60 to-blue-500/60",
};

function formatDuration(ms: number | null): string {
  if (ms === null || ms === undefined) return "--";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
}

interface TraceWaterfallProps {
  traces: AgentTrace[];
}

export function TraceWaterfall({ traces }: TraceWaterfallProps) {
  // Find orchestrator trace as parent, agent traces as children
  const orchestratorTrace = traces.find(
    (t) => t.agent_name === "orchestrator" && t.parent_trace_id === null
  );
  const agentTraces = traces.filter(
    (t) => t.agent_name !== "orchestrator" || t.parent_trace_id !== null
  );

  if (!traces.length) return null;

  // Calculate timeline bounds
  const allStarts = traces.map((t) => new Date(t.started_at).getTime());
  const allEnds = traces
    .filter((t) => t.completed_at)
    .map((t) => new Date(t.completed_at!).getTime());

  const timelineStart = Math.min(...allStarts);
  const timelineEnd = allEnds.length ? Math.max(...allEnds) : timelineStart + 5000;
  const totalDuration = Math.max(timelineEnd - timelineStart, 1);

  return (
    <div className="rounded-xl border border-white/[0.08] bg-card/60 backdrop-blur-xl overflow-hidden">
      {/* Top accent line */}
      <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent" />

      {/* Header */}
      <div className="px-4 py-3 border-b border-white/[0.06]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-cyan-400" />
            <span className="text-sm font-medium">Agent Execution Waterfall</span>
          </div>
          <span className="text-xs text-muted-foreground/50">
            Total: {formatDuration(totalDuration)}
          </span>
        </div>
      </div>

      {/* Waterfall rows */}
      <div className="p-4 space-y-1">
        {/* Orchestrator row */}
        {orchestratorTrace && (
          <TraceRow
            trace={orchestratorTrace}
            timelineStart={timelineStart}
            totalDuration={totalDuration}
            isParent
          />
        )}

        {/* Agent rows */}
        {agentTraces
          .sort((a, b) => new Date(a.started_at).getTime() - new Date(b.started_at).getTime())
          .map((trace) => (
            <TraceRow
              key={trace.id}
              trace={trace}
              timelineStart={timelineStart}
              totalDuration={totalDuration}
            />
          ))}
      </div>

      {/* Footer with timeline markers */}
      <div className="px-4 py-2 border-t border-white/[0.06] bg-white/[0.02]">
        <div className="flex justify-between text-[10px] text-muted-foreground/40">
          <span>0s</span>
          <span>{(totalDuration / 4000).toFixed(1)}s</span>
          <span>{(totalDuration / 2000).toFixed(1)}s</span>
          <span>{((totalDuration * 3) / 4000).toFixed(1)}s</span>
          <span>{(totalDuration / 1000).toFixed(1)}s</span>
        </div>
      </div>
    </div>
  );
}

interface TraceRowProps {
  trace: AgentTrace;
  timelineStart: number;
  totalDuration: number;
  isParent?: boolean;
}

function TraceRow({ trace, timelineStart, totalDuration, isParent }: TraceRowProps) {
  const [expanded, setExpanded] = useState(false);

  const start = new Date(trace.started_at).getTime();
  const end = trace.completed_at
    ? new Date(trace.completed_at).getTime()
    : start + (trace.duration_ms || 0);

  const leftPct = ((start - timelineStart) / totalDuration) * 100;
  const widthPct = Math.max(((end - start) / totalDuration) * 100, 1);

  const hasCitations = trace.citations?.length > 0;
  const hasToolCalls = trace.tool_calls?.length > 0;
  const expandable = hasCitations || hasToolCalls;

  return (
    <div>
      <div
        className={`
          flex items-center gap-3 py-1.5 rounded-lg px-2
          ${expandable ? "cursor-pointer hover:bg-white/[0.03]" : ""}
          ${isParent ? "mb-1" : ""}
        `}
        onClick={() => expandable && setExpanded(!expanded)}
      >
        {/* Agent name */}
        <div className="w-24 flex items-center gap-1.5 shrink-0">
          {expandable && (
            expanded
              ? <ChevronDown className="h-3 w-3 text-muted-foreground/40" />
              : <ChevronRight className="h-3 w-3 text-muted-foreground/40" />
          )}
          <div
            className={`h-2 w-2 rounded-full ${AGENT_COLORS[trace.agent_name] || "bg-gray-500"}`}
          />
          <span className="text-xs font-medium capitalize truncate">
            {trace.agent_name}
          </span>
        </div>

        {/* Waterfall bar */}
        <div className="flex-1 relative h-5">
          <div
            className={`
              absolute top-0.5 h-4 rounded-sm
              bg-gradient-to-r ${AGENT_BAR_COLORS[trace.agent_name] || "from-gray-500/60 to-gray-400/60"}
              ${trace.status === "failed" ? "opacity-50 border border-red-500/30" : ""}
            `}
            style={{
              left: `${leftPct}%`,
              width: `${widthPct}%`,
              minWidth: "4px",
            }}
          />
        </div>

        {/* Duration */}
        <div className="w-14 text-right shrink-0">
          <span className="text-[10px] text-muted-foreground/60 tabular-nums">
            {formatDuration(trace.duration_ms)}
          </span>
        </div>

        {/* Tokens */}
        <div className="w-16 text-right shrink-0">
          <span className="text-[10px] text-muted-foreground/60 tabular-nums">
            {trace.tokens_used > 0 ? `${trace.tokens_used}t` : "--"}
          </span>
        </div>

        {/* Citation badge */}
        <div className="w-8 shrink-0 text-right">
          {hasCitations && (
            <span className="inline-flex items-center justify-center h-4 w-4 rounded-full bg-violet-500/20 text-[9px] text-violet-400">
              {trace.citations.length}
            </span>
          )}
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="ml-28 mr-4 mb-2 animate-fade-in">
          {hasToolCalls && (
            <div className="mb-2">
              <span className="text-[10px] text-muted-foreground/50 uppercase tracking-wider">
                Tool Calls
              </span>
              <div className="flex flex-wrap gap-1 mt-1">
                {trace.tool_calls.map((tc: ToolCallRecord, i: number) => (
                  <span
                    key={i}
                    className="px-1.5 py-0.5 rounded text-[10px] bg-white/[0.04] border border-white/[0.06] text-muted-foreground/70"
                  >
                    <Zap className="h-2.5 w-2.5 inline mr-0.5" />
                    {tc.tool_name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {hasCitations && (
            <div>
              <span className="text-[10px] text-muted-foreground/50 uppercase tracking-wider">
                Sources
              </span>
              <div className="flex flex-wrap gap-1 mt-1">
                {trace.citations.map((c: Citation, i: number) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] bg-violet-500/10 border border-violet-500/20 text-violet-300"
                  >
                    {c.type === "url" ? (
                      <ExternalLink className="h-2.5 w-2.5" />
                    ) : (
                      <Database className="h-2.5 w-2.5" />
                    )}
                    {c.url
                      ? (() => {
                          try {
                            return new URL(c.url).hostname.replace("www.", "");
                          } catch {
                            return c.url.substring(0, 30);
                          }
                        })()
                      : c.source_tool || "Source"}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
