"use client";

import { useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  Search, Loader2, Building2, Sparkles, ArrowUp,
  TrendingUp, Globe, Newspaper, BarChart3,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { researchApi } from "@/lib/api";
import { TrendCard } from "@/components/research/trend-card";
import { useAgentWebSocket } from "@/lib/websocket";
import { v4 as uuidv4 } from "uuid";

/* ── Quick-start suggestions ── */

const suggestions = [
  { icon: TrendingUp, label: "Latest AI trends in healthcare", type: "research" as const },
  { icon: Globe, label: "Competitive analysis of cloud providers", type: "research" as const },
  { icon: BarChart3, label: "Social media marketing benchmarks 2026", type: "research" as const },
  { icon: Newspaper, label: "Generate briefing for Salesforce", type: "briefing" as const },
];

export default function ResearchPage() {
  const [query, setQuery] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [activeTab, setActiveTab] = useState<"research" | "briefing">("research");
  const [inputFocused, setInputFocused] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const companyInputRef = useRef<HTMLInputElement>(null);
  const researchCardId = useRef(uuidv4());
  const briefingCardId = useRef(uuidv4());

  const [sessionId] = useState(() => `research-${uuidv4()}`);
  useAgentWebSocket(sessionId);

  const researchMutation = useMutation({
    mutationFn: researchApi.query,
    onMutate: () => { researchCardId.current = uuidv4(); },
  });

  const briefingMutation = useMutation({
    mutationFn: researchApi.briefing,
    onMutate: () => { briefingCardId.current = uuidv4(); },
  });

  const handleResearch = () => {
    if (!query.trim() || researchMutation.isPending) return;
    researchMutation.mutate({ query, research_type: "comprehensive", session_id: sessionId });
  };

  const handleBriefing = () => {
    if (!companyName.trim() || briefingMutation.isPending) return;
    briefingMutation.mutate({ company_name: companyName, session_id: sessionId });
  };

  const handleSuggestion = (s: typeof suggestions[number]) => {
    if (s.type === "briefing") {
      const name = s.label.replace("Generate briefing for ", "");
      setCompanyName(name);
      setActiveTab("briefing");
      setTimeout(() => companyInputRef.current?.focus(), 50);
    } else {
      setQuery(s.label);
      setActiveTab("research");
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleResearch();
    }
  };

  const isPending = researchMutation.isPending || briefingMutation.isPending;
  const hasResults = researchMutation.data || briefingMutation.data;

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header — minimal glass bar */}
      <div className="flex h-12 shrink-0 items-center border-b border-white/[0.06] px-5 bg-card/40 backdrop-blur-md">
        <div className="flex items-center gap-2.5">
          <div className="h-2 w-2 rounded-full bg-gradient-to-r from-emerald-400 to-cyan-400" />
          <h1 className="text-sm font-semibold text-foreground/90">Trends</h1>
        </div>
        {/* Tab switcher */}
        <div className="ml-auto flex items-center gap-1 rounded-lg border border-white/[0.06] bg-card/30 p-0.5">
          <button
            onClick={() => setActiveTab("research")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
              activeTab === "research"
                ? "bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 text-emerald-500 dark:text-emerald-400 shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Search className="h-3 w-3" />
            Research
          </button>
          <button
            onClick={() => setActiveTab("briefing")}
            className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition-all duration-200 ${
              activeTab === "briefing"
                ? "bg-gradient-to-r from-blue-500/10 to-purple-500/10 text-blue-500 dark:text-blue-400 shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <Building2 className="h-3 w-3" />
            Briefing
          </button>
        </div>
      </div>

      {/* Scrollable content area */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden">
        <div className="mx-auto max-w-3xl px-6 py-6 space-y-6">

          {/* Empty state — show when no results yet */}
          {!hasResults && !isPending && (
            <div className="flex flex-col items-center justify-center pt-12 pb-6">
              {/* Background glow */}
              <div className="absolute -top-20 left-1/2 -translate-x-1/2 h-40 w-80 rounded-full bg-gradient-to-r from-emerald-500/10 via-cyan-500/10 to-blue-500/10 blur-3xl pointer-events-none" />

              {/* Logo mark */}
              <div className="relative mx-auto flex h-16 w-16 items-center justify-center mb-6">
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-400 opacity-20 blur-xl" />
                <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500/10 to-cyan-400/10 border border-white/[0.08] backdrop-blur-sm">
                  <Search className="h-7 w-7 text-emerald-400" />
                </div>
              </div>

              <h2 className="text-2xl font-bold tracking-tight bg-gradient-to-b from-foreground to-foreground/60 bg-clip-text text-transparent mb-2">
                {activeTab === "research" ? "What would you like to research?" : "Generate a client briefing"}
              </h2>
              <p className="text-sm text-muted-foreground/70 max-w-md text-center leading-relaxed mb-8">
                {activeTab === "research"
                  ? "Our AI agents will search the web, analyze trends, and compile comprehensive research on any topic."
                  : "Get a detailed briefing document about any company, including market position, recent news, and strategic insights."}
              </p>

              {/* Quick-start suggestion cards */}
              <div className="grid grid-cols-2 gap-2.5 w-full max-w-lg">
                {suggestions.map((s) => {
                  const Icon = s.icon;
                  return (
                    <button
                      key={s.label}
                      onClick={() => handleSuggestion(s)}
                      className="group relative flex items-center gap-3 rounded-xl border border-white/[0.06] bg-card/50 backdrop-blur-sm px-4 py-3.5 text-left text-sm transition-all duration-200 hover:border-emerald-500/20 hover:bg-emerald-500/[0.04] hover:shadow-lg hover:shadow-emerald-500/5"
                    >
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 text-emerald-400 group-hover:from-emerald-500/20 group-hover:to-cyan-500/20 transition-colors">
                        <Icon className="h-4 w-4" />
                      </div>
                      <span className="text-xs text-muted-foreground group-hover:text-foreground transition-colors font-medium leading-tight">
                        {s.label}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Pending indicator */}
          {isPending && (
            <div className="flex items-center gap-3.5 animate-fade-in-up">
              <div className="relative h-8 w-8 shrink-0">
                <div className="absolute inset-0 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-400 opacity-50 blur-[3px] animate-pulse" />
                <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-400 text-white ring-2 ring-white/10">
                  <Sparkles className="h-3.5 w-3.5 animate-spin" style={{ animationDuration: "3s" }} />
                </div>
              </div>
              <div className="relative overflow-hidden rounded-2xl rounded-tl-md border border-white/[0.08] bg-card/60 backdrop-blur-xl px-5 py-4 shadow-lg">
                <div className="absolute inset-0 rounded-2xl">
                  <div className="absolute inset-[-1px] rounded-2xl bg-gradient-conic from-emerald-500/40 via-transparent to-emerald-500/40 animate-spin" style={{ animationDuration: "4s" }} />
                  <div className="absolute inset-[1px] rounded-2xl bg-card/90 backdrop-blur-xl" />
                </div>
                <div className="relative flex items-center gap-3">
                  <div className="flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <span className="h-2 w-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <span className="h-2 w-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                  <span className="text-sm text-muted-foreground/70 font-medium">
                    {activeTab === "research" ? "Researching..." : "Generating briefing..."}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {researchMutation.data && (
            <div className="animate-fade-in-up">
              <TrendCard
                id={researchCardId.current}
                content={researchMutation.data.message}
                query={query}
                status={researchMutation.data.status}
                tokensUsed={researchMutation.data.tokens_used}
                variant="research"
              />
            </div>
          )}

          {briefingMutation.data && (
            <div className="animate-fade-in-up">
              <TrendCard
                id={briefingCardId.current}
                content={briefingMutation.data.message}
                query={`${briefingMutation.data.company_name} Client Briefing`}
                status={briefingMutation.data.status}
                variant="briefing"
                companyName={briefingMutation.data.company_name}
              />
            </div>
          )}
        </div>
      </div>

      {/* Input area — floating glass card (matching chat design) */}
      <div className="shrink-0 px-6 pb-5 pt-2">
        <div className="mx-auto max-w-3xl">
          {activeTab === "research" ? (
            <div
              className={`relative rounded-2xl border transition-all duration-300 ${
                inputFocused
                  ? "border-emerald-500/30 shadow-lg shadow-emerald-500/5 bg-card/80"
                  : "border-white/[0.08] bg-card/50"
              } backdrop-blur-xl`}
            >
              {inputFocused && (
                <div className="absolute -inset-px rounded-2xl bg-gradient-to-r from-emerald-500/20 via-teal-500/20 to-cyan-500/20 blur-sm -z-10" />
              )}
              <div className="flex items-end gap-2 p-3">
                <textarea
                  ref={inputRef}
                  value={query}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  onFocus={() => setInputFocused(true)}
                  onBlur={() => setInputFocused(false)}
                  placeholder="What would you like to research?"
                  rows={1}
                  className="flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none"
                  style={{ maxHeight: "160px" }}
                  disabled={researchMutation.isPending}
                />
                <Button
                  onClick={handleResearch}
                  disabled={!query.trim() || researchMutation.isPending}
                  size="icon"
                  className="h-9 w-9 shrink-0 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white shadow-lg shadow-emerald-500/20 hover:shadow-xl hover:shadow-emerald-500/30 hover:from-emerald-600 hover:to-cyan-600 disabled:opacity-30 disabled:shadow-none transition-all duration-200 border-0"
                >
                  {researchMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <ArrowUp className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="flex items-center justify-between px-5 pb-2.5 text-[10px] text-muted-foreground/40">
                <span>Enter to search, Shift+Enter for new line</span>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-[10px] h-4 px-1.5 border-emerald-500/20 text-emerald-500/60">Web</Badge>
                  <Badge variant="outline" className="text-[10px] h-4 px-1.5 border-emerald-500/20 text-emerald-500/60">News</Badge>
                  <Badge variant="outline" className="text-[10px] h-4 px-1.5 border-emerald-500/20 text-emerald-500/60">Data</Badge>
                </div>
              </div>
            </div>
          ) : (
            <div
              className={`relative rounded-2xl border transition-all duration-300 ${
                inputFocused
                  ? "border-blue-500/30 shadow-lg shadow-blue-500/5 bg-card/80"
                  : "border-white/[0.08] bg-card/50"
              } backdrop-blur-xl`}
            >
              {inputFocused && (
                <div className="absolute -inset-px rounded-2xl bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-pink-500/20 blur-sm -z-10" />
              )}
              <div className="flex items-center gap-2 p-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500/10 to-purple-500/10 text-blue-400">
                  <Building2 className="h-4 w-4" />
                </div>
                <input
                  ref={companyInputRef}
                  type="text"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") handleBriefing(); }}
                  onFocus={() => setInputFocused(true)}
                  onBlur={() => setInputFocused(false)}
                  placeholder="Enter company name..."
                  className="flex-1 bg-transparent px-2 py-1.5 text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none"
                  disabled={briefingMutation.isPending}
                />
                <Button
                  onClick={handleBriefing}
                  disabled={!companyName.trim() || briefingMutation.isPending}
                  size="icon"
                  className="h-9 w-9 shrink-0 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg shadow-blue-500/20 hover:shadow-xl hover:shadow-blue-500/30 hover:from-blue-600 hover:to-purple-600 disabled:opacity-30 disabled:shadow-none transition-all duration-200 border-0"
                >
                  {briefingMutation.isPending ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <ArrowUp className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="flex items-center justify-between px-5 pb-2.5 text-[10px] text-muted-foreground/40">
                <span>Enter to generate briefing</span>
                <span className="flex items-center gap-1">
                  <Sparkles className="h-2.5 w-2.5" />
                  Comprehensive analysis
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
