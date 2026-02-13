"use client";

import { memo, useMemo } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricItem {
  label: string;
  value: string | number;
  change?: number;
  unit?: string;
  description?: string;
}

interface MetricCardData {
  title?: string;
  metrics: MetricItem[];
}

function parseMetricData(raw: string): MetricCardData | null {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

const MetricCardBlock = memo(({ raw }: { raw: string }) => {
  const data = useMemo(() => parseMetricData(raw), [raw]);
  if (!data) return null;

  return (
    <div className="my-4">
      {data.title && (
        <h4 className="text-sm font-semibold text-foreground mb-3">{data.title}</h4>
      )}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {data.metrics.map((metric, i) => {
          const isPositive = metric.change !== undefined && metric.change > 0;
          const isNegative = metric.change !== undefined && metric.change < 0;
          const isNeutral = metric.change !== undefined && metric.change === 0;

          return (
            <div
              key={i}
              className="rounded-xl border bg-card p-4 shadow-sm overflow-hidden min-w-0"
            >
              <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider truncate">
                {metric.label}
              </p>
              <div className="mt-2 flex items-baseline gap-1 min-w-0">
                <span className="text-xl font-bold text-foreground tabular-nums truncate">
                  {metric.value}
                </span>
                {metric.unit && (
                  <span className="text-sm text-muted-foreground">{metric.unit}</span>
                )}
              </div>
              {metric.change !== undefined && (
                <div className={cn(
                  "mt-1 flex items-center gap-1 text-xs font-medium",
                  isPositive && "text-emerald-600 dark:text-emerald-400",
                  isNegative && "text-rose-600 dark:text-rose-400",
                  isNeutral && "text-muted-foreground"
                )}>
                  {isPositive && <TrendingUp className="h-3 w-3" />}
                  {isNegative && <TrendingDown className="h-3 w-3" />}
                  {isNeutral && <Minus className="h-3 w-3" />}
                  <span>{isPositive ? "+" : ""}{metric.change}%</span>
                </div>
              )}
              {metric.description && (
                <p className="mt-1 text-[11px] text-muted-foreground">{metric.description}</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
});
MetricCardBlock.displayName = "MetricCardBlock";

export const METRIC_RENDERERS: Record<string, React.ComponentType<{ raw: string }>> = {
  "metrics": MetricCardBlock,
  "metric-cards": MetricCardBlock,
  "kpi": MetricCardBlock,
};
