"use client";

import { memo, useMemo } from "react";
import { Info, AlertTriangle, CheckCircle2, Lightbulb, Zap, Target } from "lucide-react";
import { cn } from "@/lib/utils";

interface CalloutData {
  type: "info" | "warning" | "success" | "tip" | "insight" | "action";
  title?: string;
  content: string;
}

function parseCalloutData(raw: string): CalloutData | null {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

const CALLOUT_STYLES = {
  info: {
    icon: Info,
    bg: "bg-blue-50 dark:bg-blue-950/30",
    border: "border-blue-200 dark:border-blue-800",
    iconColor: "text-blue-600 dark:text-blue-400",
    title: "text-blue-900 dark:text-blue-200",
  },
  warning: {
    icon: AlertTriangle,
    bg: "bg-amber-50 dark:bg-amber-950/30",
    border: "border-amber-200 dark:border-amber-800",
    iconColor: "text-amber-600 dark:text-amber-400",
    title: "text-amber-900 dark:text-amber-200",
  },
  success: {
    icon: CheckCircle2,
    bg: "bg-emerald-50 dark:bg-emerald-950/30",
    border: "border-emerald-200 dark:border-emerald-800",
    iconColor: "text-emerald-600 dark:text-emerald-400",
    title: "text-emerald-900 dark:text-emerald-200",
  },
  tip: {
    icon: Lightbulb,
    bg: "bg-violet-50 dark:bg-violet-950/30",
    border: "border-violet-200 dark:border-violet-800",
    iconColor: "text-violet-600 dark:text-violet-400",
    title: "text-violet-900 dark:text-violet-200",
  },
  insight: {
    icon: Zap,
    bg: "bg-cyan-50 dark:bg-cyan-950/30",
    border: "border-cyan-200 dark:border-cyan-800",
    iconColor: "text-cyan-600 dark:text-cyan-400",
    title: "text-cyan-900 dark:text-cyan-200",
  },
  action: {
    icon: Target,
    bg: "bg-rose-50 dark:bg-rose-950/30",
    border: "border-rose-200 dark:border-rose-800",
    iconColor: "text-rose-600 dark:text-rose-400",
    title: "text-rose-900 dark:text-rose-200",
  },
};

const CalloutBlock = memo(({ raw }: { raw: string }) => {
  const data = useMemo(() => parseCalloutData(raw), [raw]);
  if (!data) return null;

  const style = CALLOUT_STYLES[data.type] || CALLOUT_STYLES.info;
  const Icon = style.icon;

  return (
    <div className={cn("my-3 flex gap-3 rounded-lg border p-3 overflow-hidden", style.bg, style.border)}>
      <Icon className={cn("h-5 w-5 shrink-0 mt-0.5", style.iconColor)} />
      <div className="flex-1 min-w-0 overflow-hidden">
        {data.title && (
          <p className={cn("text-sm font-semibold mb-0.5 break-words", style.title)}>{data.title}</p>
        )}
        <p className="text-sm text-foreground/80 leading-relaxed break-words">{data.content}</p>
      </div>
    </div>
  );
});
CalloutBlock.displayName = "CalloutBlock";

export const CALLOUT_RENDERERS: Record<string, React.ComponentType<{ raw: string }>> = {
  callout: CalloutBlock,
  insight: CalloutBlock,
  tip: CalloutBlock,
  warning: CalloutBlock,
};
