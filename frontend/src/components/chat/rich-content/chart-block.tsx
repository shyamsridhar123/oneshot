"use client";

import { memo, useMemo } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart";

const COLORS = [
  "oklch(0.488 0.243 264.376)", // violet
  "oklch(0.696 0.17 162.48)",   // teal
  "oklch(0.646 0.222 41.116)",  // orange
  "oklch(0.645 0.246 16.439)",  // rose
  "oklch(0.828 0.189 84.429)",  // amber
  "oklch(0.627 0.265 303.9)",   // purple
  "oklch(0.6 0.118 184.704)",   // cyan
  "oklch(0.769 0.188 70.08)",   // yellow-green
];

interface ChartData {
  title?: string;
  subtitle?: string;
  data: Record<string, unknown>[];
  xKey?: string;
  yKeys?: string[];
  nameKey?: string;
  valueKey?: string;
}

function parseChartData(raw: string): ChartData | null {
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function ChartTitle({ title, subtitle }: { title?: string; subtitle?: string }) {
  if (!title && !subtitle) return null;
  return (
    <div className="mb-3 px-1">
      {title && <h4 className="text-sm font-semibold text-foreground">{title}</h4>}
      {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
    </div>
  );
}

function buildConfig(keys: string[]): ChartConfig {
  const config: ChartConfig = {};
  keys.forEach((key, i) => {
    config[key] = {
      label: key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, " "),
      color: COLORS[i % COLORS.length],
    };
  });
  return config;
}

const BarChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  const { xKey, yKeys, config } = useMemo(() => {
    if (!chart) return { xKey: "", yKeys: [] as string[], config: {} as ChartConfig };
    const x = chart.xKey || Object.keys(chart.data[0])[0];
    const y = chart.yKeys || Object.keys(chart.data[0]).filter((k) => k !== x);
    return { xKey: x, yKeys: y, config: buildConfig(y) };
  }, [chart]);
  if (!chart) return <FallbackBlock raw={raw} />;

  return (
    <div className="my-4 rounded-xl border bg-card p-5 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ChartContainer config={config} className="h-[300px] w-full">
        <BarChart accessibilityLayer data={chart.data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid vertical={false} />
          <XAxis dataKey={xKey} tickLine={false} axisLine={false} tickMargin={8} tick={{ fontSize: 11 }} />
          <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          {yKeys.map((key) => (
            <Bar
              key={key}
              dataKey={key}
              fill={`var(--color-${key})`}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      </ChartContainer>
    </div>
  );
});
BarChartBlock.displayName = "BarChartBlock";

const LineChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  const { xKey, yKeys, config } = useMemo(() => {
    if (!chart) return { xKey: "", yKeys: [] as string[], config: {} as ChartConfig };
    const x = chart.xKey || Object.keys(chart.data[0])[0];
    const y = chart.yKeys || Object.keys(chart.data[0]).filter((k) => k !== x);
    return { xKey: x, yKeys: y, config: buildConfig(y) };
  }, [chart]);
  if (!chart) return <FallbackBlock raw={raw} />;

  return (
    <div className="my-4 rounded-xl border bg-card p-5 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ChartContainer config={config} className="h-[300px] w-full">
        <LineChart accessibilityLayer data={chart.data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid vertical={false} />
          <XAxis dataKey={xKey} tickLine={false} axisLine={false} tickMargin={8} tick={{ fontSize: 11 }} />
          <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          {yKeys.map((key) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={`var(--color-${key})`}
              strokeWidth={2}
              dot={{ r: 3, fill: `var(--color-${key})` }}
              activeDot={{ r: 5 }}
            />
          ))}
        </LineChart>
      </ChartContainer>
    </div>
  );
});
LineChartBlock.displayName = "LineChartBlock";

const AreaChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  const { xKey, yKeys, config } = useMemo(() => {
    if (!chart) return { xKey: "", yKeys: [] as string[], config: {} as ChartConfig };
    const x = chart.xKey || Object.keys(chart.data[0])[0];
    const y = chart.yKeys || Object.keys(chart.data[0]).filter((k) => k !== x);
    return { xKey: x, yKeys: y, config: buildConfig(y) };
  }, [chart]);
  if (!chart) return <FallbackBlock raw={raw} />;

  return (
    <div className="my-4 rounded-xl border bg-card p-5 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ChartContainer config={config} className="h-[300px] w-full">
        <AreaChart accessibilityLayer data={chart.data} margin={{ top: 10, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid vertical={false} />
          <XAxis dataKey={xKey} tickLine={false} axisLine={false} tickMargin={8} tick={{ fontSize: 11 }} />
          <YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
          <ChartTooltip content={<ChartTooltipContent indicator="line" />} />
          <ChartLegend content={<ChartLegendContent />} />
          {yKeys.map((key) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stroke={`var(--color-${key})`}
              fill={`var(--color-${key})`}
              fillOpacity={0.15}
              strokeWidth={2}
            />
          ))}
        </AreaChart>
      </ChartContainer>
    </div>
  );
});
AreaChartBlock.displayName = "AreaChartBlock";

const PieChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);

  const { nameKey, valueKey } = useMemo(() => {
    if (!chart) return { nameKey: "", valueKey: "" };
    return {
      nameKey: chart.nameKey || Object.keys(chart.data[0])[0],
      valueKey: chart.valueKey || Object.keys(chart.data[0])[1],
    };
  }, [chart]);

  const config = useMemo<ChartConfig>(() => {
    if (!chart) return {};
    const c: ChartConfig = { [valueKey]: { label: valueKey } };
    chart.data.forEach((d, i) => {
      const name = String(d[nameKey] ?? `item-${i}`);
      c[name] = {
        label: name,
        color: COLORS[i % COLORS.length],
      };
    });
    return c;
  }, [chart, nameKey, valueKey]);

  const dataWithFill = useMemo(
    () =>
      chart
        ? chart.data.map((d, i) => ({
            ...d,
            fill: COLORS[i % COLORS.length],
          }))
        : [],
    [chart]
  );

  if (!chart) return <FallbackBlock raw={raw} />;

  return (
    <div className="my-4 rounded-xl border bg-card p-5 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ChartContainer config={config} className="mx-auto aspect-square h-[340px]">
        <PieChart>
          <ChartTooltip content={<ChartTooltipContent nameKey={nameKey} />} />
          <Pie
            data={dataWithFill}
            dataKey={valueKey}
            nameKey={nameKey}
            cx="50%"
            cy="45%"
            outerRadius={90}
            innerRadius={45}
            paddingAngle={3}
            strokeWidth={2}
            stroke="var(--background)"
          >
            {dataWithFill.map((entry, i) => (
              <Cell key={i} fill={entry.fill} />
            ))}
          </Pie>
          <ChartLegend content={<ChartLegendContent nameKey={nameKey} />} />
        </PieChart>
      </ChartContainer>
    </div>
  );
});
PieChartBlock.displayName = "PieChartBlock";

const RadarChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  const { subjectKey, valueKeys, config } = useMemo(() => {
    if (!chart) return { subjectKey: "", valueKeys: [] as string[], config: {} as ChartConfig };
    const s = chart.xKey || chart.nameKey || Object.keys(chart.data[0])[0];
    const v = chart.yKeys || Object.keys(chart.data[0]).filter((k) => k !== s);
    return { subjectKey: s, valueKeys: v, config: buildConfig(v) };
  }, [chart]);
  if (!chart) return <FallbackBlock raw={raw} />;

  return (
    <div className="my-4 rounded-xl border bg-card p-5 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ChartContainer config={config} className="h-[300px] w-full">
        <RadarChart data={chart.data}>
          <PolarGrid />
          <PolarAngleAxis dataKey={subjectKey} tick={{ fontSize: 11 }} />
          <PolarRadiusAxis tick={{ fontSize: 10 }} />
          <ChartTooltip content={<ChartTooltipContent />} />
          <ChartLegend content={<ChartLegendContent />} />
          {valueKeys.map((key) => (
            <Radar
              key={key}
              name={key}
              dataKey={key}
              stroke={`var(--color-${key})`}
              fill={`var(--color-${key})`}
              fillOpacity={0.2}
            />
          ))}
        </RadarChart>
      </ChartContainer>
    </div>
  );
});
RadarChartBlock.displayName = "RadarChartBlock";

function FallbackBlock({ raw }: { raw: string }) {
  return (
    <pre className="my-4 overflow-x-auto rounded-lg border bg-muted/50 p-4 text-xs">
      <code>{raw}</code>
    </pre>
  );
}

export const CHART_RENDERERS: Record<string, React.ComponentType<{ raw: string }>> = {
  "chart-bar": BarChartBlock,
  "chart-line": LineChartBlock,
  "chart-area": AreaChartBlock,
  "chart-pie": PieChartBlock,
  "chart-radar": RadarChartBlock,
};
