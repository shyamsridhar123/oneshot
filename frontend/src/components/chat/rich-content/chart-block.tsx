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
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const COLORS = [
  "hsl(221, 83%, 53%)", // blue-600
  "hsl(262, 83%, 58%)", // violet-500
  "hsl(173, 80%, 40%)", // teal-600
  "hsl(25, 95%, 53%)",  // orange-500
  "hsl(338, 71%, 51%)", // rose-500
  "hsl(47, 96%, 53%)",  // amber-400
  "hsl(142, 71%, 45%)", // green-500
  "hsl(199, 89%, 48%)", // sky-500
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

const BarChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  if (!chart) return <FallbackBlock raw={raw} />;

  const xKey = chart.xKey || Object.keys(chart.data[0])[0];
  const yKeys = chart.yKeys || Object.keys(chart.data[0]).filter((k) => k !== xKey);

  return (
    <div className="my-4 rounded-xl border bg-card p-4 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={chart.data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid hsl(var(--border))",
              backgroundColor: "hsl(var(--card))",
              fontSize: "12px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} />
          {yKeys.map((key, i) => (
            <Bar
              key={key}
              dataKey={key}
              fill={COLORS[i % COLORS.length]}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
});
BarChartBlock.displayName = "BarChartBlock";

const LineChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  if (!chart) return <FallbackBlock raw={raw} />;

  const xKey = chart.xKey || Object.keys(chart.data[0])[0];
  const yKeys = chart.yKeys || Object.keys(chart.data[0]).filter((k) => k !== xKey);

  return (
    <div className="my-4 rounded-xl border bg-card p-4 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chart.data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid hsl(var(--border))",
              backgroundColor: "hsl(var(--card))",
              fontSize: "12px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} />
          {yKeys.map((key, i) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={COLORS[i % COLORS.length]}
              strokeWidth={2}
              dot={{ r: 3 }}
              activeDot={{ r: 5 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
});
LineChartBlock.displayName = "LineChartBlock";

const AreaChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  if (!chart) return <FallbackBlock raw={raw} />;

  const xKey = chart.xKey || Object.keys(chart.data[0])[0];
  const yKeys = chart.yKeys || Object.keys(chart.data[0]).filter((k) => k !== xKey);

  return (
    <div className="my-4 rounded-xl border bg-card p-4 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chart.data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid hsl(var(--border))",
              backgroundColor: "hsl(var(--card))",
              fontSize: "12px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} />
          {yKeys.map((key, i) => (
            <Area
              key={key}
              type="monotone"
              dataKey={key}
              stroke={COLORS[i % COLORS.length]}
              fill={COLORS[i % COLORS.length]}
              fillOpacity={0.15}
              strokeWidth={2}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
});
AreaChartBlock.displayName = "AreaChartBlock";

const PieChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  if (!chart) return <FallbackBlock raw={raw} />;

  const nameKey = chart.nameKey || Object.keys(chart.data[0])[0];
  const valueKey = chart.valueKey || Object.keys(chart.data[0])[1];

  return (
    <div className="my-4 rounded-xl border bg-card p-4 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            data={chart.data}
            dataKey={valueKey}
            nameKey={nameKey}
            cx="50%"
            cy="50%"
            outerRadius={100}
            innerRadius={50}
            paddingAngle={2}
            label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
            labelLine={{ strokeWidth: 1 }}
          >
            {chart.data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid hsl(var(--border))",
              backgroundColor: "hsl(var(--card))",
              fontSize: "12px",
            }}
          />
          <Legend wrapperStyle={{ fontSize: "12px" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
});
PieChartBlock.displayName = "PieChartBlock";

const RadarChartBlock = memo(({ raw }: { raw: string }) => {
  const chart = useMemo(() => parseChartData(raw), [raw]);
  if (!chart) return <FallbackBlock raw={raw} />;

  const subjectKey = chart.xKey || chart.nameKey || Object.keys(chart.data[0])[0];
  const valueKeys =
    chart.yKeys || Object.keys(chart.data[0]).filter((k) => k !== subjectKey);

  return (
    <div className="my-4 rounded-xl border bg-card p-4 shadow-sm">
      <ChartTitle title={chart.title} subtitle={chart.subtitle} />
      <ResponsiveContainer width="100%" height={280}>
        <RadarChart data={chart.data}>
          <PolarGrid className="opacity-30" />
          <PolarAngleAxis dataKey={subjectKey} tick={{ fontSize: 11 }} />
          <PolarRadiusAxis tick={{ fontSize: 10 }} />
          {valueKeys.map((key, i) => (
            <Radar
              key={key}
              name={key}
              dataKey={key}
              stroke={COLORS[i % COLORS.length]}
              fill={COLORS[i % COLORS.length]}
              fillOpacity={0.2}
            />
          ))}
          <Legend wrapperStyle={{ fontSize: "12px" }} />
          <Tooltip
            contentStyle={{
              borderRadius: "8px",
              border: "1px solid hsl(var(--border))",
              backgroundColor: "hsl(var(--card))",
              fontSize: "12px",
            }}
          />
        </RadarChart>
      </ResponsiveContainer>
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
