"use client";

import { ExternalLink, BookOpen, Database, Sparkles } from "lucide-react";
import type { Citation } from "@/lib/types";

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
    const agent = c.contributing_agent || c.source_tool || "sources";
    if (!byAgent[agent]) byAgent[agent] = [];
    byAgent[agent].push(c);
  }

  return (
    <div className="animate-fade-in-up mt-4 ml-11">
      {/* Glass card — matches assistant message bubble styling */}
      <div className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-card/80 backdrop-blur-xl shadow-xl shadow-black/5 dark:shadow-black/20 transition-all duration-300 hover:border-white/[0.12]">
        {/* Violet accent line — same as message bubbles */}
        <div className="absolute top-0 left-4 right-4 h-px bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />

        {/* Header */}
        <div className="px-5 pt-4 pb-2 flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-violet-500/10 border border-violet-500/20">
            <Sparkles className="h-3 w-3 text-violet-400" />
            <span className="text-[10px] font-semibold text-violet-300 tracking-wide">
              {citations.length} Source{citations.length !== 1 ? "s" : ""} Referenced
            </span>
          </div>
        </div>

        {/* Citation groups by agent */}
        <div className="px-5 pb-4 space-y-3">
          {Object.entries(byAgent).map(([agent, agentCitations]) => (
            <div key={agent}>
              {/* Agent label with colored dot */}
              <div className="flex items-center gap-1.5 mb-2">
                <div
                  className={`h-1.5 w-1.5 rounded-full bg-gradient-to-r ${AGENT_COLORS[agent] || "from-gray-500 to-gray-400"}`}
                />
                <span className="text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wider">
                  {AGENT_LABELS[agent] || agent}
                </span>
              </div>

              {/* Citation chips */}
              <div className="flex flex-wrap gap-1.5">
                {agentCitations.map((citation, idx) => (
                  <CitationChip key={`${agent}-${idx}`} citation={citation} />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Bottom accent — subtle separator */}
        <div className="h-px bg-gradient-to-r from-transparent via-white/[0.04] to-transparent" />
      </div>
    </div>
  );
}

function CitationChip({ citation }: { citation: Citation }) {
  const isLink = citation.type === "url" && citation.url;

  const chipContent = (
    <div
      className={`
        inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px]
        border border-white/[0.08] bg-white/[0.04]
        transition-all duration-200
        ${isLink
          ? "hover:bg-violet-500/10 hover:border-violet-500/20 cursor-pointer group"
          : ""}
      `}
    >
      <span className={`shrink-0 ${isLink ? "text-violet-400 group-hover:text-violet-300" : "text-muted-foreground/50"}`}>
        <CitationIcon type={citation.type} />
      </span>
      <span className="text-muted-foreground/80 max-w-[220px] truncate">
        {isLink
          ? formatUrl(citation.url!)
          : citation.preview || citation.source_tool || "Source"}
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
        {chipContent}
      </a>
    );
  }

  return chipContent;
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
