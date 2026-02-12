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
    id: "content",
    label: "Content Creation",
    icon: Lightbulb,
    title: "From idea to publish-ready posts in seconds",
    description: "Transform a single topic into platform-specific social media content for LinkedIn, Twitter/X, and Instagram—with brand compliance built in.",
    features: [
      {
        icon: FileText,
        title: "Multi-Platform Posts",
        stat: "3 platforms",
        description: "Generate LinkedIn articles, Twitter threads, and Instagram captions simultaneously from a single prompt."
      },
      {
        icon: Clock,
        title: "Brand Compliance",
        stat: "Scored 1-10",
        description: "Every post is reviewed by the Advisor agent for brand voice alignment, hashtag compliance, and content policy adherence."
      },
      {
        icon: CheckCircle2,
        title: "Data-Grounded",
        stat: "RAG-powered",
        description: "Content is grounded in brand guidelines, past post performance, and trending topics—not hallucinated."
      }
    ]
  },
  {
    id: "trends",
    label: "Trend Research",
    icon: Users,
    title: "Know what's trending before you post",
    description: "Real-time trend analysis, competitor monitoring, and hashtag research across all platforms—synthesized by the Researcher agent.",
    features: [
      {
        icon: Brain,
        title: "Trend Discovery",
        stat: "ReAct pattern",
        description: "The Researcher agent uses Thought-Action-Observation loops to discover and validate trending topics in your industry."
      },
      {
        icon: Users,
        title: "Competitor Analysis",
        stat: "Gap detection",
        description: "Analyze what competitors are posting, identify content gaps, and find opportunities for differentiation."
      },
      {
        icon: Zap,
        title: "Hashtag Strategy",
        stat: "Optimized",
        description: "Get recommended hashtags with estimated reach, competition level, and relevance scoring per platform."
      }
    ]
  },
  {
    id: "brand",
    label: "Brand Intelligence",
    icon: Cog,
    title: "Your brand knowledge, always accessible",
    description: "Semantic search across brand guidelines, past post performance, and content calendars—the Memory agent keeps all agents aligned.",
    features: [
      {
        icon: FileText,
        title: "Past Post Analytics",
        stat: "Performance",
        description: "Learn from what worked: high-performing posts, engagement patterns, and content formats that drive results."
      },
      {
        icon: Users,
        title: "Brand Voice Guard",
        stat: "Consistent",
        description: "Brand guidelines are embedded in every agent's context, ensuring consistent voice across all platforms."
      },
      {
        icon: Lightbulb,
        title: "Content Calendar",
        stat: "Planned",
        description: "Weekly content plans with optimal posting times, content mix recommendations, and platform-specific scheduling."
      }
    ]
  }
];

export function CapabilitiesSection() {
  const [activeTab, setActiveTab] = useState("content");
  const activeCapability = capabilities.find(c => c.id === activeTab)!;

  return (
    <section id="capabilities" className="py-24 bg-muted/30">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Purpose-built for <span className="text-primary">social media teams</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Transform how your team creates, reviews, and publishes content across
              LinkedIn, Twitter/X, and Instagram—with AI agents handling every step.
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
                    <span className="ml-2 text-sm text-muted-foreground">social-media-workspace</span>
                  </div>

                  {activeTab === "content" && (
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs">You</div>
                        <div className="flex-1 bg-muted rounded-xl p-3 text-sm">
                          Write a LinkedIn post about our AI Collaboration Suite launch...
                        </div>
                      </div>
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                          <Brain className="w-4 h-4 text-primary-foreground" />
                        </div>
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center gap-2 text-xs text-muted-foreground">
                            <span>Orchestrator coordinating 2 waves...</span>
                          </div>
                          <div className="grid grid-cols-4 gap-2">
                            {["Research", "Strategy", "Writing", "Review"].map((phase, i) => (
                              <div key={i} className={cn(
                                "h-1.5 rounded-full",
                                i <= 2 ? "bg-primary" : "bg-muted"
                              )} />
                            ))}
                          </div>
                          <div className="bg-card border border-border rounded-lg p-3 text-sm">
                            <div className="font-medium mb-1">LinkedIn + Twitter + Instagram</div>
                            <div className="text-muted-foreground text-xs">3 posts generated | Score: 9/10</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === "trends" && (
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs">You</div>
                        <div className="flex-1 bg-muted rounded-xl p-3 text-sm">
                          What AI topics are trending on social media?
                        </div>
                      </div>
                      <div className="space-y-2">
                        {[
                          { topic: "#AIAgents", platform: "Twitter", trend: "Surging" },
                          { topic: "AI Collaboration", platform: "LinkedIn", trend: "Rising" },
                          { topic: "AI company culture", platform: "Instagram", trend: "Stable" },
                        ].map((result, i) => (
                          <div key={i} className="flex items-center justify-between bg-card border border-border rounded-lg p-3">
                            <span className="text-sm">{result.topic}</span>
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-muted-foreground">{result.platform}</span>
                              <span className="text-xs text-primary font-medium">{result.trend}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === "brand" && (
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs">You</div>
                        <div className="flex-1 bg-muted rounded-xl p-3 text-sm">
                          What content performed best last month?
                        </div>
                      </div>
                      <div className="bg-card border border-border rounded-lg p-4 space-y-3">
                        <div className="flex items-center gap-2 text-sm font-medium">
                          <Users className="w-4 h-4 text-primary" />
                          Top Performing Posts
                        </div>
                        <div className="space-y-2 text-xs">
                          <div className="flex justify-between"><span>LinkedIn myth-busting post</span><span className="text-primary font-medium">5.8% engagement</span></div>
                          <div className="flex justify-between"><span>Twitter founder thread</span><span className="text-primary font-medium">6.2% engagement</span></div>
                          <div className="flex justify-between"><span>Instagram team celebration</span><span className="text-primary font-medium">5.1% engagement</span></div>
                        </div>
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
