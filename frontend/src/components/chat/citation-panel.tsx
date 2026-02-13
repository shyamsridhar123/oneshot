"use client";

import { ExternalLink, BookOpen, Database, Sparkles } from "lucide-react";
import type { Citation, AgentName } from "@/lib/types";

const AGENT_COLORS: Record<string, string> = {
  researcher: "from-emerald-500 to-teal-500",
  strategist: "from-blue-500 to-indigo-500",
  analyst: "from-orange-500 to-amber-500",
  memory: "from-yellow-500 to-orange-500",
  scribe: "from-pink-500 to-rose-500",
  advisor: "from-cyan-500 to-blue-500",
  orchestrator: "from-violet-500 to-purple-500",
};

const AGENT_LABELS: Record<string, string> = {
  researcher: "Research",
  strategist: "Strategy",
  analyst: "Analysis",
  memory: "Brand Memory",
  scribe: "Content",
  advisor: "Compliance",
  orchestrator: "Orchestrator",
};

function CitationIcon({ type }: { type: string }) {
  if (type === "url") return <ExternalLink className="h-3 w-3" />;
  if (type === "knowledge") return <Database className="h-3 w-3" />;
  return <BookOpen className="h-3 w-3" />;
}

function formatUrl(url: string): string {
  try {
    const u = new URL(url);
    return u.hostname.replace("www.", "");
  } catch {
    return url.substring(0, 40);
  }
}

export function CitationPanel({ citations }: { citations: Citation[] }) {
  if (!citations.length) return null;

  // Group by contributing agent
  const byAgent: Record<string, Citation[]> = {};
  for (const c of citations) {
    const agent = c.contributing_agent || "unknown";
    if (!byAgent[agent]) byAgent[agent] = [];
    byAgent[agent].push(c);
  }

  return (
    <div className="animate-fade-in-up mt-3">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-violet-500/10 border border-violet-500/20">
          <Sparkles className="h-3 w-3 text-violet-400" />
          <span className="text-[10px] font-medium text-violet-300">
            {citations.length} Source{citations.length !== 1 ? "s" : ""} Referenced
          </span>
        </div>
      </div>

      {/* Citation Cards */}
      <div className="rounded-xl border border-white/[0.08] bg-card/60 backdrop-blur-xl overflow-hidden">
        {/* Top accent line */}
        <div className="h-px bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />

        <div className="p-3 space-y-2">
          {Object.entries(byAgent).map(([agent, agentCitations]) => (
            <div key={agent}>
              {/* Agent label */}
              <div className="flex items-center gap-1.5 mb-1.5">
                <div
                  className={`h-1.5 w-1.5 rounded-full bg-gradient-to-r ${AGENT_COLORS[agent] || "from-gray-500 to-gray-400"}`}
                />
                <span className="text-[10px] font-medium text-muted-foreground/70 uppercase tracking-wider">
                  {AGENT_LABELS[agent] || agent}
                </span>
              </div>

              {/* Citations for this agent */}
              <div className="flex flex-wrap gap-1.5">
                {agentCitations.map((citation, idx) => (
                  <CitationChip key={`${agent}-${idx}`} citation={citation} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function CitationChip({ citation }: { citation: Citation }) {
  const isLink = citation.type === "url" && citation.url;

  const content = (
    <div
      className={`
        inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-[10px]
        border border-white/[0.06] bg-white/[0.03]
        transition-all duration-200
        ${isLink ? "hover:bg-white/[0.06] hover:border-white/[0.12] cursor-pointer" : ""}
      `}
    >
      <CitationIcon type={citation.type} />
      <span className="text-muted-foreground/80 max-w-[200px] truncate">
        {isLink ? formatUrl(citation.url!) : citation.source_tool || "Source"}
      </span>
    </div>
  );

  if (isLink) {
    return (
      <a
        href={citation.url}
        target="_blank"
        rel="noopener noreferrer"
        className="no-underline"
      >
        {content}
      </a>
    );
  }

  return content;
}

export function InlineCitationBadge({ count }: { count: number }) {
  if (count === 0) return null;

  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-md bg-violet-500/10 border border-violet-500/20 text-[9px] font-medium text-violet-400">
      <Sparkles className="h-2.5 w-2.5" />
      {count} source{count !== 1 ? "s" : ""}
    </span>
  );
}
