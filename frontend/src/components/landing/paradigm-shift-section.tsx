"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { 
  FolderSearch, 
  Network, 
  Search, 
  Sparkles, 
  LayoutGrid, 
  Zap,
  Lock,
  Shield
} from "lucide-react";

const comparisons = [
  {
    before: {
      icon: FolderSearch,
      title: "Document libraries & email chains",
      description: "Information scattered across SharePoint, email threads, and local drives. Average search takes 15+ minutes to find the right version.",
    },
    after: {
      icon: Network,
      title: "Unified knowledge graph",
      description: "Clients, projects, experts, and methodologies linked with semantic relationships enabling instant contextual retrieval.",
    },
  },
  {
    before: {
      icon: Search,
      title: "Keyword search & manual review",
      description: "Consultants spend 30-40% of billable time finding and synthesizing information from past engagements.",
    },
    after: {
      icon: Sparkles,
      title: "Goal-driven agent orchestration",
      description: "State your objective, Orchestrator coordinates specialist agents to synthesize, draft, and prepare deliverables with full provenance.",
    },
  },
  {
    before: {
      icon: LayoutGrid,
      title: "Portal navigation & self-service",
      description: "Multiple internal systems, different credentials, inconsistent user experiences across practice areas.",
    },
    after: {
      icon: Zap,
      title: "Ambient intelligence layer",
      description: "Proactive insights surface automatically based on your current context, client meetings, and project timelines.",
    },
  },
  {
    before: {
      icon: Lock,
      title: "Static role-based permissions",
      description: "Binary access controls that don't adapt to engagement context or confidentiality requirements.",
    },
    after: {
      icon: Shield,
      title: "Dynamic permission fabric",
      description: "Context-aware access where both human consultants and AI agents operate within auditable, engagement-specific boundaries.",
    },
  },
];

export function ParadigmShiftSection() {
  const [activeTab, setActiveTab] = useState<"before" | "after">("after");

  return (
    <section id="platform" className="py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <div className="max-w-5xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              The paradigm shift
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              From fragmented knowledge silos to a living intelligence fabric—transforming how 
              consultants create and deliver value.
            </p>
          </div>

          {/* Toggle */}
          <div className="flex justify-center mb-12">
            <div className="inline-flex items-center bg-card border border-border rounded-full p-1">
              <button
                onClick={() => setActiveTab("before")}
                className={cn(
                  "px-6 py-2 rounded-full text-sm font-medium transition-all",
                  activeTab === "before"
                    ? "bg-muted-foreground text-background"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                BEFORE
              </button>
              <button
                onClick={() => setActiveTab("after")}
                className={cn(
                  "px-6 py-2 rounded-full text-sm font-medium transition-all",
                  activeTab === "after"
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:text-foreground"
                )}
              >
                WITH FEDERATION
              </button>
            </div>
          </div>

          {/* Comparison Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {comparisons.map((item, i) => {
              const comparison = activeTab === "before" ? item.before : item.after;
              const Icon = comparison.icon;
              
              return (
                <div
                  key={i}
                  className={cn(
                    "relative p-6 rounded-2xl border transition-all duration-500",
                    activeTab === "before"
                      ? "bg-card border-border"
                      : "bg-gradient-to-br from-card to-primary/5 border-primary/20 shadow-lg"
                  )}
                >
                  <div className={cn(
                    "w-12 h-12 rounded-xl flex items-center justify-center mb-4",
                    activeTab === "before"
                      ? "bg-muted"
                      : "bg-primary/10"
                  )}>
                    <Icon className={cn(
                      "w-6 h-6",
                      activeTab === "before"
                        ? "text-muted-foreground"
                        : "text-primary"
                    )} />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{comparison.title}</h3>
                  <p className="text-muted-foreground">{comparison.description}</p>
                  
                  {activeTab === "after" && (
                    <div className="absolute top-4 right-4">
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/10 text-green-500 text-xs font-medium rounded-full">
                        <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                        Enhanced
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
