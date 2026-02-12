"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Send } from "lucide-react";
import Link from "next/link";

const samplePrompts = [
  "Create a LinkedIn post about our AI Collaboration Suite launch",
  "Write a week of social media content for TechVista across all platforms",
  "What are the trending AI topics on social media this week?",
  "Review this draft tweet for brand alignment and compliance",
];

export function HeroSection() {
  const [inputValue, setInputValue] = useState("");
  const [activePrompt, setActivePrompt] = useState(0);

  return (
    <section className="relative min-h-screen flex flex-col justify-center overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5 dark:to-primary/10" />
      
      {/* Animated grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.02)_1px,transparent_1px)] dark:bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:60px_60px]" />
      
      {/* Floating orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-chart-2/10 rounded-full blur-3xl animate-pulse delay-1000" />
      
      <div className="relative z-10 container mx-auto px-6 py-24">
        <div className="max-w-5xl mx-auto text-center space-y-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium border border-primary/20">
            <Sparkles className="w-4 h-4" />
            Powered by Microsoft Agent Framework
          </div>
          
          {/* Main Headline */}
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            <span className="text-foreground">Your brand&apos;s </span>
            <span className="bg-gradient-to-r from-primary via-chart-1 to-chart-2 bg-clip-text text-transparent">
              social media voice
            </span>
            <span className="text-foreground">, amplified.</span>
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            Social Media Command Center coordinates 7 specialized AI agents—
            Strategist, Researcher, Scribe, Advisor—to create platform-perfect content.
            <span className="text-foreground font-medium"> Describe your goal—agents handle the rest.</span>
          </p>
          
          {/* Intent Delegate Input */}
          <div className="max-w-2xl mx-auto mt-12">
            <div className="relative">
              <div className="absolute -inset-1 bg-gradient-to-r from-primary/50 via-chart-1/50 to-chart-2/50 rounded-2xl blur opacity-30 group-hover:opacity-50 transition" />
              <div className="relative bg-card border border-border rounded-xl p-2 shadow-2xl">
                <div className="flex items-center gap-2 px-4 py-2 text-xs text-muted-foreground uppercase tracking-wider border-b border-border mb-2">
                  <Sparkles className="w-3 h-3" />
                  Intent Delegate
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder={samplePrompts[activePrompt]}
                    className="flex-1 bg-transparent px-4 py-4 text-lg placeholder:text-muted-foreground/50 focus:outline-none"
                    onFocus={() => {
                      const interval = setInterval(() => {
                        setActivePrompt((prev) => (prev + 1) % samplePrompts.length);
                      }, 3000);
                      return () => clearInterval(interval);
                    }}
                  />
                  <Button size="lg" className="rounded-lg" asChild>
                    <Link href="/chat">
                      <Send className="w-5 h-5" />
                    </Link>
                  </Button>
                </div>
              </div>
            </div>
            
            {/* Sample prompts */}
            <div className="flex flex-wrap justify-center gap-2 mt-6">
              {samplePrompts.slice(0, 3).map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => setInputValue(prompt)}
                  className="px-3 py-1.5 text-xs bg-muted hover:bg-muted/80 rounded-full text-muted-foreground hover:text-foreground transition-colors truncate max-w-[200px]"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-8">
            <Button size="lg" className="text-lg px-8 py-6" asChild>
              <Link href="/chat">
                Create Content
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" className="text-lg px-8 py-6" asChild>
              <Link href="#agents">
                Meet the Agents
              </Link>
            </Button>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-16 border-t border-border mt-16">
            {[
              { value: "7", label: "Specialized Agents" },
              { value: "3", label: "Reasoning Patterns" },
              { value: "3", label: "Platform Targets" },
              { value: "24/7", label: "Content Creation" },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-foreground">{stat.value}</div>
                <div className="text-sm text-muted-foreground mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-muted-foreground/30 rounded-full flex items-start justify-center p-2">
          <div className="w-1 h-2 bg-muted-foreground/50 rounded-full animate-pulse" />
        </div>
      </div>
    </section>
  );
}
