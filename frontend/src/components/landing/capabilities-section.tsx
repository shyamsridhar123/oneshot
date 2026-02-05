"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { 
  Lightbulb, 
  Cog, 
  Users,
  FileText,
  Clock,
  CheckCircle2,
  Zap,
  Brain
} from "lucide-react";

const capabilities = [
  {
    id: "proposals",
    label: "Proposal Generation",
    icon: Lightbulb,
    title: "From request to deliverable in minutes",
    description: "Transform a single sentence into a comprehensive proposal with research, frameworks, and financials.",
    features: [
      {
        icon: FileText,
        title: "Complete Proposals",
        stat: "End-to-end",
        description: "Full proposals with executive summary, approach, timeline, and investment—generated from a single prompt."
      },
      {
        icon: Clock,
        title: "Rapid Turnaround",
        stat: "Minutes",
        description: "What typically takes 2-3 weeks now happens in under 5 minutes. Win more deals by responding faster."
      },
      {
        icon: CheckCircle2,
        title: "Source-Cited",
        stat: "Traceable",
        description: "Every claim is traceable to its source—past engagements, market data, or knowledge base frameworks."
      }
    ]
  },
  {
    id: "research",
    label: "Client Intelligence",
    icon: Users,
    title: "Know your client before every meeting",
    description: "Comprehensive briefings synthesized from multiple sources in seconds, not hours.",
    features: [
      {
        icon: Brain,
        title: "Deep Synthesis",
        stat: "Multi-source",
        description: "Combines public filings, news, industry reports, and internal engagement history into unified briefings."
      },
      {
        icon: Users,
        title: "Executive Profiles",
        stat: "Leadership",
        description: "Background, tenure, style, and recent statements for key decision-makers you'll be meeting."
      },
      {
        icon: Zap,
        title: "Meeting Ready",
        stat: "Instant",
        description: "Get recommended questions, potential pain points, and relationship history before any client interaction."
      }
    ]
  },
  {
    id: "knowledge",
    label: "Knowledge Discovery",
    icon: Cog,
    title: "Unlock your institutional memory",
    description: "Semantic search that understands meaning, not just keywords. Find relevant work even with different terminology.",
    features: [
      {
        icon: FileText,
        title: "Past Engagements",
        stat: "Semantic",
        description: "Find similar work based on context and outcomes, not keyword matching. Discover hidden patterns."
      },
      {
        icon: Users,
        title: "Expert Matching",
        stat: "Intelligent",
        description: "Surface the right internal experts based on skills, availability, and past client relationships."
      },
      {
        icon: Lightbulb,
        title: "Living Methodologies",
        stat: "Growing",
        description: "Frameworks that grow smarter with every engagement—automatically capturing lessons learned."
      }
    ]
  }
];

export function CapabilitiesSection() {
  const [activeTab, setActiveTab] = useState("proposals");
  const activeCapability = capabilities.find(c => c.id === activeTab)!;

  return (
    <section id="capabilities" className="py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Purpose-built for <span className="text-primary">professional services</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Transform how consultants create, deliver, and capture value across every 
              engagement—from initial pitch to final deliverable.
            </p>
          </div>

          {/* Tabs */}
          <div className="flex justify-center mb-12">
            <div className="inline-flex items-center bg-card border border-border rounded-xl p-1.5 gap-1">
              {capabilities.map((cap) => {
                const Icon = cap.icon;
                return (
                  <button
                    key={cap.id}
                    onClick={() => setActiveTab(cap.id)}
                    className={cn(
                      "flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all",
                      activeTab === cap.id
                        ? "bg-primary text-primary-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {cap.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Content */}
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Description */}
            <div className="space-y-6">
              <div className={cn(
                "w-16 h-16 rounded-2xl flex items-center justify-center",
                "bg-gradient-to-br from-primary to-chart-2"
              )}>
                {(() => {
                  const Icon = activeCapability.icon;
                  return <Icon className="w-8 h-8 text-white" />;
                })()}
              </div>
              <h3 className="text-3xl font-bold">{activeCapability.title}</h3>
              <p className="text-lg text-muted-foreground">
                {activeCapability.description}
              </p>
              
              {/* Mini features list */}
              <div className="space-y-4 pt-4">
                {activeCapability.features.map((feature, i) => {
                  const FeatureIcon = feature.icon;
                  return (
                    <div key={i} className="flex gap-4">
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <FeatureIcon className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold">{feature.title}</span>
                          <span className="px-2 py-0.5 bg-primary/10 text-primary text-xs font-medium rounded-full">
                            {feature.stat}
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground mt-1">{feature.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right: Visual */}
            <div className="relative">
              <div className="absolute -inset-4 bg-gradient-to-br from-primary/20 via-chart-1/10 to-chart-2/20 rounded-3xl blur-2xl" />
              <div className="relative bg-card border border-border rounded-2xl p-8 shadow-2xl">
                {/* Demo visualization */}
                <div className="space-y-4">
                  <div className="flex items-center gap-3 pb-4 border-b border-border">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    <div className="w-3 h-3 rounded-full bg-green-500" />
                    <span className="ml-2 text-sm text-muted-foreground">federation-workspace</span>
                  </div>
                  
                  {activeTab === "proposals" && (
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs">You</div>
                        <div className="flex-1 bg-muted rounded-xl p-3 text-sm">
                          Create a proposal for Acme Corp&apos;s digital transformation...
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                          <Brain className="w-4 h-4 text-primary-foreground" />
                        </div>
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span>Orchestrator is coordinating...</span>
                          </div>
                          <div className="grid grid-cols-4 gap-2">
                            {["Research", "Strategy", "Analysis", "Writing"].map((phase, i) => (
                              <div key={i} className={cn(
                                "h-1.5 rounded-full",
                                i <= 2 ? "bg-primary" : "bg-muted"
                              )} />
                            ))}
                          </div>
                          <div className="bg-card border border-border rounded-lg p-3 text-sm">
                            <div className="font-medium mb-1">📄 Proposal Generated</div>
                            <div className="text-muted-foreground text-xs">15 pages • 3 sources cited</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === "research" && (
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs">You</div>
                        <div className="flex-1 bg-muted rounded-xl p-3 text-sm">
                          Brief me on TechCorp before tomorrow&apos;s meeting
                        </div>
                      </div>
                      <div className="bg-card border border-border rounded-lg p-4 space-y-3">
                        <div className="flex items-center gap-2 text-sm font-medium">
                          <Users className="w-4 h-4 text-primary" />
                          TechCorp Solutions
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-xs">
                          <div><span className="text-muted-foreground">Revenue:</span> $50M ARR</div>
                          <div><span className="text-muted-foreground">Industry:</span> B2B SaaS</div>
                          <div><span className="text-muted-foreground">Employees:</span> 250</div>
                          <div><span className="text-muted-foreground">Growth:</span> +40% YoY</div>
                        </div>
                        <div className="pt-2 border-t border-border text-xs text-muted-foreground">
                          ✅ Past engagement: Growth Strategy (2024)
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === "knowledge" && (
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs">You</div>
                        <div className="flex-1 bg-muted rounded-xl p-3 text-sm">
                          Healthcare M&A integration frameworks?
                        </div>
                      </div>
                      <div className="space-y-2">
                        {[
                          { title: "HealthCare Partners Integration", match: "92%" },
                          { title: "Regional Health System PMI", match: "87%" },
                          { title: "Medical Device M&A Playbook", match: "84%" },
                        ].map((result, i) => (
                          <div key={i} className="flex items-center justify-between bg-card border border-border rounded-lg p-3">
                            <span className="text-sm">{result.title}</span>
                            <span className="text-xs text-primary font-medium">{result.match} match</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
