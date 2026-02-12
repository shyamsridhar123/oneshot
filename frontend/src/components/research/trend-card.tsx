"use client";

import { memo, useMemo, useState } from "react";
import { Copy, Check, Share2, TrendingUp, Globe, Newspaper } from "lucide-react";
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

  // Generate tags from bold text or headings
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
      ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
      : status === "error"
        ? "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20"
        : "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20";

  const VariantIcon = variant === "briefing" ? Globe : TrendingUp;

  return (
    <div className="group relative overflow-hidden rounded-xl border bg-card shadow-sm transition-all hover:shadow-md">
      {/* Gradient accent bar */}
      <div
        className={cn(
          "h-1",
          variant === "briefing"
            ? "bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500"
            : "bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500"
        )}
      />

      {/* Header */}
      <div className="flex items-start justify-between gap-3 px-5 pt-4 pb-2">
        <div className="flex items-start gap-3 min-w-0">
          <div
            className={cn(
              "flex h-10 w-10 shrink-0 items-center justify-center rounded-lg",
              variant === "briefing"
                ? "bg-blue-500/10 text-blue-600 dark:text-blue-400"
                : "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
            )}
          >
            <VariantIcon className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <h3 className="font-semibold text-base leading-tight truncate">
              {variant === "briefing" && companyName
                ? companyName
                : query}
            </h3>
            {summaryLine && (
              <p className="mt-0.5 text-sm text-muted-foreground line-clamp-2">
                {summaryLine}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          <Badge variant="outline" className={cn("text-xs", statusColor)}>
            {status}
          </Badge>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity"
            onClick={handleCopy}
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-emerald-500" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
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
              className="text-xs font-medium text-primary/70 hover:text-primary cursor-default transition-colors"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Content */}
      <div className="px-5 pb-4">
        <div
          className={cn(
            "overflow-hidden transition-all duration-300",
            expanded ? "max-h-none" : "max-h-64"
          )}
        >
          <div className="prose prose-sm dark:prose-invert max-w-none prose-p:my-1.5 prose-headings:my-2 prose-ul:my-1 prose-ol:my-1 prose-li:my-0.5 prose-pre:my-2 prose-blockquote:my-2 prose-blockquote:border-primary/30 prose-a:text-primary prose-strong:text-foreground">
            <MemoizedMarkdown content={content} id={id} />
          </div>
        </div>

        {content.length > 600 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-2 text-xs font-medium text-primary hover:text-primary/80 transition-colors"
          >
            {expanded ? "Show less" : "Show more"}
          </button>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t px-5 py-2.5 bg-muted/30">
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Newspaper className="h-3 w-3" />
            {variant === "briefing" ? "Client Brief" : "Research"}
          </span>
          {tokensUsed !== undefined && tokensUsed > 0 && (
            <span>{tokensUsed.toLocaleString()} tokens</span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs gap-1"
            onClick={handleCopy}
          >
            {copied ? (
              <Check className="h-3 w-3" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
            {copied ? "Copied" : "Copy"}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs gap-1"
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
