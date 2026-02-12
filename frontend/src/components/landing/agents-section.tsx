"use client";

import { cn } from "@/lib/utils";
import { 
  Brain, 
  Target, 
  Search, 
  BarChart3, 
  FileEdit, 
  MessageSquare,
  Database
} from "lucide-react";

const agents = [
  {
    name: "Orchestrator",
    role: "Content Coordinator",
    description: "Analyzes incoming requests, identifies target platforms, and coordinates two-wave parallel dispatch: context gathering then content creation + review.",
    icon: Brain,
    color: "from-violet-500 to-purple-600",
  },
  {
    name: "Strategist",
    role: "Content Strategist (CoT)",
    description: "Plans content strategy using Chain-of-Thought reasoning: audience targeting, tone selection, content calendar, and platform-specific CTAs.",
    icon: Target,
    color: "from-blue-500 to-cyan-500",
  },
  {
    name: "Researcher",
    role: "Trend Analyst (ReAct)",
    description: "Discovers trending topics, analyzes competitor content, and researches hashtags using the ReAct reasoning pattern: Thought, Action, Observation loops.",
    icon: Search,
    color: "from-emerald-500 to-green-500",
  },
  {
    name: "Analyst",
    role: "Engagement Analyst",
    description: "Provides engagement benchmarks, predicts content performance, recommends optimal posting times, and suggests content formats for maximum reach.",
    icon: BarChart3,
    color: "from-orange-500 to-amber-500",
  },
  {
    name: "Scribe",
    role: "Content Writer",
    description: "Generates platform-specific content using template-guided patterns: LinkedIn articles, Twitter/X threads, Instagram captions with brand voice alignment.",
    icon: FileEdit,
    color: "from-pink-500 to-rose-500",
  },
  {
    name: "Advisor",
    role: "Brand Compliance (Self-Reflection)",
    description: "Reviews content for brand alignment using Self-Reflection: initial review, metacognitive reflection, then revised compliance scoring from 1-10.",
    icon: MessageSquare,
    color: "from-indigo-500 to-blue-600",
  },
  {
    name: "Memory",
    role: "Brand Knowledge (RAG)",
    description: "Retrieves brand guidelines, past post performance data, and content calendar context to ground all content in NotContosso's brand identity.",
    icon: Database,
    color: "from-teal-500 to-cyan-600",
  },
];

export function AgentsSection() {
  return (
    <section id="agents" className="py-24">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Meet your <span className="text-primary">content agents</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Specialized AI agents with distinct reasoning patterns, scoped tools, and full
              audit trails—creating platform-perfect social media content 24/7.
            </p>
          </div>

          {/* Agents Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent, i) => {
              const Icon = agent.icon;
              
              return (
                <div
                  key={i}
                  className={cn(
                    "group relative p-6 rounded-2xl border bg-card hover:shadow-xl transition-all duration-300",
                    "hover:-translate-y-1"
                  )}
                >
                  {/* Status indicator */}
                  <div className="absolute top-4 right-4">
                    <span className="inline-flex items-center gap-1.5 px-2 py-1 text-xs font-medium rounded-full bg-green-500/10 text-green-500">
                      <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
                      Ready
                    </span>
                  </div>

                  {/* Icon */}
                  <div className={cn(
                    "w-14 h-14 rounded-xl flex items-center justify-center mb-4",
                    "bg-gradient-to-br",
                    agent.color
                  )}>
                    <Icon className="w-7 h-7 text-white" />
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-bold mb-1">{agent.name}</h3>
                  <p className="text-sm text-primary mb-3">{agent.role}</p>
                  <p className="text-muted-foreground text-sm leading-relaxed mb-4">
                    {agent.description}
                  </p>

                  {/* Hover effect */}
                  <div className={cn(
                    "absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none",
                    "bg-gradient-to-br",
                    agent.color,
                    "opacity-0 group-hover:opacity-5"
                  )} />
                </div>
              );
            })}
          </div>

          {/* Coordination visualization */}
          <div className="mt-16 p-8 rounded-2xl bg-gradient-to-br from-muted/50 to-muted border border-border">
            <div className="text-center mb-8">
              <h3 className="text-2xl font-bold mb-2">Two-Wave Parallel Orchestration</h3>
              <p className="text-muted-foreground">
                Wave 1 gathers context (research, strategy, brand data). Wave 2 creates content and reviews compliance—all in parallel.
              </p>
            </div>
            
            <div className="flex items-center justify-center gap-4 flex-wrap">
              <div className="flex -space-x-3">
                {agents.slice(0, 5).map((agent, i) => {
                  const Icon = agent.icon;
                  return (
                    <div
                      key={i}
                      className={cn(
                        "w-10 h-10 rounded-full flex items-center justify-center border-2 border-background",
                        "bg-gradient-to-br",
                        agent.color
                      )}
                    >
                      <Icon className="w-5 h-5 text-white" />
                    </div>
                  );
                })}
              </div>
              <div className="flex items-center gap-2">
                <div className="w-16 h-0.5 bg-gradient-to-r from-primary to-transparent" />
                <span className="text-sm text-muted-foreground">coordinated by</span>
                <div className="w-16 h-0.5 bg-gradient-to-l from-primary to-transparent" />
              </div>
              <div className={cn(
                "w-12 h-12 rounded-full flex items-center justify-center",
                "bg-gradient-to-br from-violet-500 to-purple-600",
                "ring-4 ring-primary/20"
              )}>
                <Brain className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
