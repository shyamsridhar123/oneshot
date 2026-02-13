"use client";

import { memo, useMemo, useState } from "react";
import { Copy, Check, Share2, TrendingUp, Globe, Newspaper, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { MemoizedMarkdown } from "@/components/chat/memoized-markdown";

interface TrendCardProps {
  id: string;
  content: string;
  query: string;
  status: string;
  tokensUsed?: number;
  variant?: "research" | "briefing";
  companyName?: string;
}

function extractHashtags(content: string): string[] {
  const tags = content.match(/#\w+/g) || [];
  if (tags.length > 0) return [...new Set(tags)].slice(0, 8);

  const boldMatches = content.match(/\*\*([^*]+)\*\*/g) || [];
  return boldMatches
    .slice(0, 5)
    .map((m) =>
      "#" +
      m
        .replace(/\*\*/g, "")
        .replace(/[^a-zA-Z0-9 ]/g, "")
        .trim()
        .split(/\s+/)
        .slice(0, 2)
        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
        .join("")
    )
    .filter((t) => t.length > 1 && t.length < 30);
}

function extractSummaryLine(content: string): string {
  const lines = content.split("\n").filter((l) => l.trim());
  for (const line of lines) {
    const cleaned = line.replace(/^#+\s*/, "").replace(/\*\*/g, "").trim();
    if (cleaned.length > 20 && cleaned.length < 200 && !cleaned.startsWith("-") && !cleaned.startsWith("*")) {
      return cleaned;
    }
  }
  return lines[0]?.replace(/^#+\s*/, "").replace(/\*\*/g, "").trim() || "";
}

export const TrendCard = memo(function TrendCard({
  id,
  content,
  query,
  status,
  tokensUsed,
  variant = "research",
  companyName,
}: TrendCardProps) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const hashtags = useMemo(() => extractHashtags(content), [content]);
  const summaryLine = useMemo(() => extractSummaryLine(content), [content]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const statusColor =
    status === "completed"
      ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
      : status === "error"
        ? "border-red-500/20 bg-red-500/10 text-red-600 dark:text-red-400"
        : "border-amber-500/20 bg-amber-500/10 text-amber-600 dark:text-amber-400";

  const isResearch = variant === "research";
  const VariantIcon = isResearch ? TrendingUp : Globe;

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-card/80 backdrop-blur-xl shadow-xl shadow-black/5 dark:shadow-black/20 transition-all duration-300 hover:border-white/[0.12] hover:shadow-2xl">
      {/* Top gradient accent line */}
      <div
        className={cn(
          "absolute top-0 left-6 right-6 h-px",
          isResearch
            ? "bg-gradient-to-r from-transparent via-emerald-500/50 to-transparent"
            : "bg-gradient-to-r from-transparent via-blue-500/50 to-transparent"
        )}
      />

      {/* Header */}
      <div className="flex items-start justify-between gap-3 px-5 pt-5 pb-2">
        <div className="flex items-start gap-3 min-w-0">
          {/* Gradient avatar */}
          <div className="relative h-9 w-9 shrink-0">
            <div
              className={cn(
                "absolute inset-0 rounded-xl opacity-40 blur-[3px]",
                isResearch
                  ? "bg-gradient-to-br from-emerald-500 to-cyan-400"
                  : "bg-gradient-to-br from-blue-500 to-purple-500"
              )}
            />
            <div
              className={cn(
                "relative flex h-9 w-9 items-center justify-center rounded-xl text-white ring-2 ring-white/10 shadow-lg",
                isResearch
                  ? "bg-gradient-to-br from-emerald-500 to-cyan-400 shadow-emerald-500/20"
                  : "bg-gradient-to-br from-blue-500 to-purple-500 shadow-blue-500/20"
              )}
            >
              <VariantIcon className="h-4 w-4" />
            </div>
          </div>
          <div className="min-w-0 pt-0.5">
            <h3 className="font-semibold text-sm leading-tight truncate text-foreground/90">
              {variant === "briefing" && companyName ? companyName : query}
            </h3>
            {summaryLine && (
              <p className="mt-1 text-xs text-muted-foreground/60 line-clamp-1">
                {summaryLine}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0 pt-0.5">
          <Badge variant="outline" className={cn("text-[10px] font-medium", statusColor)}>
            {status}
          </Badge>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity hover:bg-white/[0.06]"
            onClick={handleCopy}
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-emerald-500" />
            ) : (
              <Copy className="h-3.5 w-3.5 text-muted-foreground" />
            )}
          </Button>
        </div>
      </div>

      {/* Hashtags */}
      {hashtags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 px-5 pb-2">
          {hashtags.map((tag) => (
            <span
              key={tag}
              className={cn(
                "text-[10px] font-medium px-1.5 py-0.5 rounded-md transition-colors cursor-default",
                isResearch
                  ? "text-emerald-500/60 bg-emerald-500/5 hover:text-emerald-500 hover:bg-emerald-500/10"
                  : "text-blue-500/60 bg-blue-500/5 hover:text-blue-500 hover:bg-blue-500/10"
              )}
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Content */}
      <div className="px-5 pb-4 overflow-hidden">
        <div
          className={cn(
            "overflow-hidden transition-all duration-300",
            expanded ? "max-h-none" : "max-h-64"
          )}
        >
          <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-p:leading-relaxed prose-headings:mt-3 prose-headings:mb-1 prose-headings:leading-snug prose-h2:text-sm prose-h2:font-bold prose-h3:text-[13px] prose-h3:font-semibold prose-ul:my-1 prose-ol:my-1 prose-li:my-0 prose-li:leading-relaxed prose-pre:my-2 prose-pre:overflow-x-auto prose-blockquote:my-2 prose-blockquote:border-primary/30 prose-a:text-primary prose-strong:text-foreground prose-hr:my-2.5 prose-img:rounded-lg prose-img:max-h-96 prose-img:w-full prose-img:object-contain text-foreground/90 break-words [overflow-wrap:anywhere]">
            <MemoizedMarkdown content={content} id={id} />
          </div>
        </div>

        {/* Soft fade-out gradient when collapsed */}
        {!expanded && content.length > 600 && (
          <div className="relative -mt-12 h-12 bg-gradient-to-t from-card/95 to-transparent pointer-events-none" />
        )}

        {content.length > 600 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className={cn(
              "mt-1 flex items-center gap-1 text-xs font-medium transition-colors",
              isResearch
                ? "text-emerald-500 hover:text-emerald-400"
                : "text-blue-500 hover:text-blue-400"
            )}
          >
            {expanded ? (
              <>Show less <ChevronUp className="h-3 w-3" /></>
            ) : (
              <>Show more <ChevronDown className="h-3 w-3" /></>
            )}
          </button>
        )}
      </div>

      {/* Footer — glass divider */}
      <div className="flex items-center justify-between border-t border-white/[0.06] px-5 py-2.5 bg-white/[0.02]">
        <div className="flex items-center gap-3 text-[10px] text-muted-foreground/50 font-medium">
          <span className="flex items-center gap-1">
            <Newspaper className="h-3 w-3" />
            {variant === "briefing" ? "Client Brief" : "Research"}
          </span>
          {tokensUsed !== undefined && tokensUsed > 0 && (
            <span className="flex items-center gap-1">
              <Sparkles className="h-2.5 w-2.5" />
              {tokensUsed.toLocaleString()} tokens
            </span>
          )}
        </div>
        <div className="flex items-center gap-0.5">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-[10px] gap-1 rounded-lg hover:bg-white/[0.06] text-muted-foreground/60 hover:text-foreground"
            onClick={handleCopy}
          >
            {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
            {copied ? "Copied" : "Copy"}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-[10px] gap-1 rounded-lg hover:bg-white/[0.06] text-muted-foreground/60 hover:text-foreground"
            onClick={() => {
              if (navigator.share) {
                navigator.share({ text: content, title: query });
              } else {
                handleCopy();
              }
            }}
          >
            <Share2 className="h-3 w-3" />
            Share
          </Button>
        </div>
      </div>
    </div>
  );
});
