"use client";

import { cn } from "@/lib/utils";
import { 
  Database, 
  Sparkles, 
  Shield, 
  Rocket,
  CheckCircle2
} from "lucide-react";

const phases = [
  {
    quarter: "Phase 1",
    phase: "01",
    title: "Foundation",
    icon: Database,
    color: "from-blue-500 to-cyan-500",
    features: [
      "Microsoft Agent Framework integration",
      "7 specialized agents deployed",
      "Knowledge base with sample data",
    ],
    status: "completed"
  },
  {
    quarter: "Phase 2",
    phase: "02",
    title: "Enterprise Integration",
    icon: Sparkles,
    color: "from-purple-500 to-pink-500",
    features: [
      "Connect to DMS & CRM systems",
      "SSO authentication",
      "Fine-tuning on historical data",
    ],
    status: "planned"
  },
  {
    quarter: "Phase 3",
    phase: "03",
    title: "Security & Governance",
    icon: Shield,
    color: "from-emerald-500 to-green-500",
    features: [
      "Human + agent audit trails",
      "Engagement-specific permissions",
      "Compliance certification",
    ],
    status: "planned"
  },
  {
    quarter: "Phase 4",
    phase: "04",
    title: "Full Production",
    icon: Rocket,
    color: "from-orange-500 to-amber-500",
    features: [
      "Firm-wide rollout",
      "Client-facing capabilities",
      "Continuous learning loop",
    ],
    status: "planned"
  },
];

export function RoadmapSection() {
  return (
    <section id="implementation" className="py-24">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Implementation <span className="text-primary">roadmap</span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              A phased approach to deploying agentic AI in your organization—starting with 
              this proof of concept and scaling to enterprise-wide operations.
            </p>
          </div>

          {/* Timeline */}
          <div className="relative">
            {/* Connecting line */}
            <div className="absolute left-8 md:left-1/2 top-0 bottom-0 w-0.5 bg-gradient-to-b from-primary via-chart-2 to-muted -translate-x-1/2 hidden md:block" />
            
            <div className="space-y-12">
              {phases.map((phase, i) => {
                const Icon = phase.icon;
                const isLeft = i % 2 === 0;
                
                return (
                  <div key={i} className={cn(
                    "relative grid md:grid-cols-2 gap-8 items-center",
                    !isLeft && "md:direction-rtl"
                  )}>
                    {/* Content */}
                    <div className={cn(
                      "md:direction-ltr",
                      isLeft ? "md:text-right md:pr-12" : "md:col-start-2 md:pl-12"
                    )}>
                      <div className={cn(
                        "inline-block px-3 py-1 rounded-full text-xs font-medium mb-4",
                      phase.status === "completed" ? "bg-green-500/10 text-green-500" : "bg-muted text-muted-foreground"
                      )}>
                        {phase.quarter}
                      </div>
                      <h3 className="text-2xl font-bold mb-4">{phase.title}</h3>
                      <ul className={cn(
                        "space-y-2",
                        isLeft && "md:ml-auto"
                      )}>
                        {phase.features.map((feature, j) => (
                          <li key={j} className={cn(
                            "flex items-center gap-2 text-muted-foreground",
                            isLeft && "md:flex-row-reverse"
                          )}>
                            <CheckCircle2 className={cn(
                              "w-4 h-4 flex-shrink-0",
                              phase.status === "completed" ? "text-green-500" : "text-muted-foreground/50"
                            )} />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Circle on timeline */}
                    <div className={cn(
                      "absolute left-8 md:left-1/2 -translate-x-1/2 w-16 h-16 rounded-2xl flex items-center justify-center z-10",
                      "bg-gradient-to-br shadow-lg border-4 border-background",
                      phase.color
                    )}>
                      <Icon className="w-8 h-8 text-white" />
                    </div>

                    {/* Phase number */}
                    <div className={cn(
                      "hidden md:block md:direction-ltr",
                      isLeft && "md:col-start-2 md:pl-12",
                      !isLeft && "md:col-start-1 md:pr-12 md:text-right"
                    )}>
                      <span className="text-8xl font-bold text-muted/30">{phase.phase}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
