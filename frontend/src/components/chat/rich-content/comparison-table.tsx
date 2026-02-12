"use client";

import { memo, useMemo } from "react";
import { Check, X, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

interface ComparisonData {
  title?: string;
  headers: string[];
  rows: {
    label: string;
    values: (string | number | boolean)[];
    highlight?: boolean;
  }[];
}

function parseComparisonData(raw: string): ComparisonData | null {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function CellValue({ value }: { value: string | number | boolean }) {
  if (typeof value === "boolean") {
    return value ? (
      <Check className="h-4 w-4 text-emerald-600 dark:text-emerald-400 mx-auto" />
    ) : (
      <X className="h-4 w-4 text-rose-500 dark:text-rose-400 mx-auto" />
    );
  }
  if (value === "-" || value === "N/A") {
    return <Minus className="h-4 w-4 text-muted-foreground mx-auto" />;
  }
  return <span>{value}</span>;
}

const ComparisonTableBlock = memo(({ raw }: { raw: string }) => {
  const data = useMemo(() => parseComparisonData(raw), [raw]);
  if (!data) return null;

  return (
    <div className="my-4 rounded-xl border bg-card shadow-sm overflow-hidden">
      {data.title && (
        <div className="px-4 py-3 border-b bg-muted/30">
          <h4 className="text-sm font-semibold text-foreground">{data.title}</h4>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/20">
              <th className="px-4 py-2.5 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Feature
              </th>
              {data.headers.map((h) => (
                <th key={h} className="px-4 py-2.5 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, i) => (
              <tr
                key={i}
                className={cn(
                  "border-b last:border-0 transition-colors",
                  row.highlight
                    ? "bg-primary/5 dark:bg-primary/10"
                    : "hover:bg-muted/30"
                )}
              >
                <td className="px-4 py-2.5 text-sm font-medium text-foreground">
                  {row.label}
                </td>
                {row.values.map((val, j) => (
                  <td key={j} className="px-4 py-2.5 text-sm text-center text-muted-foreground">
                    <CellValue value={val} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
});
ComparisonTableBlock.displayName = "ComparisonTableBlock";

export const COMPARISON_RENDERERS: Record<string, React.ComponentType<{ raw: string }>> = {
  "comparison": ComparisonTableBlock,
  "comparison-table": ComparisonTableBlock,
};
