"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart3, Activity, Zap, Clock, Loader2, TrendingUp,
} from "lucide-react";
import {
  Bar, BarChart, Pie, PieChart, Cell, XAxis, YAxis, CartesianGrid,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent,
  type ChartConfig,
} from "@/components/ui/chart";
import { analyticsApi } from "@/lib/api";
import { TraceWaterfall } from "@/components/chat/trace-waterfall";
import type { AgentTrace, AgentName } from "@/lib/types";

// ── Agent color system (CSS values for charts + Tailwind classes for badges) ──

const agentChartColors: Record<AgentName, string> = {
  orchestrator: "oklch(0.627 0.265 303.9)",
  strategist: "oklch(0.488 0.243 264.376)",
  researcher: "oklch(0.696 0.17 162.48)",
  analyst: "oklch(0.646 0.222 41.116)",
  scribe: "oklch(0.645 0.246 16.439)",
  advisor: "oklch(0.6 0.118 184.704)",
  memory: "oklch(0.828 0.189 84.429)",
};

const agentBadgeColors: Record<AgentName, string> = {
  orchestrator: "bg-purple-500",
  strategist: "bg-blue-500",
  researcher: "bg-green-500",
  analyst: "bg-orange-500",
  scribe: "bg-pink-500",
  advisor: "bg-cyan-500",
  memory: "bg-yellow-500",
};

// ── Sub-components ──

function TraceRow({ trace }: { trace: AgentTrace }) {
  const statusColor = {
    completed: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
    failed: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
    running: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
  }[trace.status] || "bg-muted text-muted-foreground";

  const duration = trace.completed_at
    ? new Date(trace.completed_at).getTime() -
      new Date(trace.started_at).getTime()
    : null;

  return (
    <div className="flex items-center gap-4 rounded-lg border p-3 hover:bg-muted/50 transition-colors">
      <div className={`h-2 w-2 rounded-full ${agentBadgeColors[trace.agent_name]}`} />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium capitalize">{trace.agent_name}</span>
          {trace.task_type && (
            <span className="text-sm text-muted-foreground">• {trace.task_type}</span>
          )}
        </div>
        <div className="text-xs text-muted-foreground">
          {new Date(trace.started_at).toLocaleString("en-US", { timeZone: "America/New_York" })}
        </div>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        {duration !== null && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Clock className="h-3 w-3" />
            {(duration / 1000).toFixed(1)}s
          </div>
        )}
        {trace.tokens_used > 0 && (
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Zap className="h-3 w-3" />
            {trace.tokens_used.toLocaleString()}
          </div>
        )}
        <Badge variant="outline" className={statusColor}>
          {trace.status}
        </Badge>
      </div>
    </div>
  );
}

function MetricsCard({
  title,
  value,
  description,
  icon: Icon,
  trend,
}: {
  title: string;
  value: string | number;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  trend?: string;
}) {
  return (
    <Card className="relative overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className="rounded-md bg-muted p-1.5">
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold tracking-tight">{value}</div>
        <div className="flex items-center gap-1 mt-1">
          {trend && (
            <span className="flex items-center gap-0.5 text-xs font-medium text-emerald-600 dark:text-emerald-400">
              <TrendingUp className="h-3 w-3" />
              {trend}
            </span>
          )}
          <p className="text-xs text-muted-foreground">{description}</p>
        </div>
      </CardContent>
    </Card>
  );
}

// ── Main page ──

export default function AnalyticsPage() {
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ["metrics", "day"],
    queryFn: () => analyticsApi.metrics("day"),
  });

  const { data: traces = [], isLoading: tracesLoading } = useQuery({
    queryKey: ["traces"],
    queryFn: () => analyticsApi.traces(),
  });

  const totalTokens = metrics?.agent_stats.reduce(
    (sum, stat) => sum + stat.avg_tokens * stat.executions,
    0
  ) || 0;

  const avgResponseTime = traces.length > 0
    ? traces.reduce((sum, t) => {
        if (t.completed_at) {
          return sum + (new Date(t.completed_at).getTime() - new Date(t.started_at).getTime());
        }
        return sum;
      }, 0) / traces.filter(t => t.completed_at).length
    : 0;

  // ── Derived chart data ──

  const executionChartConfig = useMemo<ChartConfig>(() => {
    const config: ChartConfig = {};
    metrics?.agent_stats.forEach((stat) => {
      config[stat.agent] = {
        label: stat.agent.charAt(0).toUpperCase() + stat.agent.slice(1),
        color: agentChartColors[stat.agent],
      };
    });
    return config;
  }, [metrics]);

  const executionBarData = useMemo(() => {
    return (metrics?.agent_stats ?? []).map((stat) => ({
      agent: stat.agent.charAt(0).toUpperCase() + stat.agent.slice(1),
      executions: stat.executions,
      fill: agentChartColors[stat.agent],
    }));
  }, [metrics]);

  const tokenPieData = useMemo(() => {
    return (metrics?.agent_stats ?? []).map((stat) => ({
      agent: stat.agent.charAt(0).toUpperCase() + stat.agent.slice(1),
      tokens: Math.round(stat.avg_tokens * stat.executions),
      fill: agentChartColors[stat.agent],
    }));
  }, [metrics]);

  const tokenPieConfig = useMemo<ChartConfig>(() => {
    const config: ChartConfig = {
      tokens: { label: "Tokens" },
    };
    metrics?.agent_stats.forEach((stat) => {
      config[stat.agent.charAt(0).toUpperCase() + stat.agent.slice(1)] = {
        label: stat.agent.charAt(0).toUpperCase() + stat.agent.slice(1),
        color: agentChartColors[stat.agent],
      };
    });
    return config;
  }, [metrics]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex h-14 items-center border-b px-6">
        <h1 className="text-xl font-semibold">Analytics</h1>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="p-6 space-y-6">
          {metricsLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <>
              {/* ── Metrics Cards ── */}
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <MetricsCard
                  title="Total Executions"
                  value={metrics?.total_executions || 0}
                  description="last 24 hours"
                  icon={Activity}
                />
                <MetricsCard
                  title="Active Agents"
                  value={metrics?.agent_stats.length || 0}
                  description="with activity"
                  icon={BarChart3}
                />
                <MetricsCard
                  title="Total Tokens"
                  value={Math.round(totalTokens).toLocaleString()}
                  description="used today"
                  icon={Zap}
                />
                <MetricsCard
                  title="Avg Response Time"
                  value={`${(avgResponseTime / 1000).toFixed(1)}s`}
                  description="per task"
                  icon={Clock}
                />
              </div>

              {/* ── Charts Row ── */}
              <div className="grid gap-6 lg:grid-cols-5">
                {/* Bar Chart – Executions per Agent */}
                <Card className="lg:col-span-3">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      Agent Executions
                    </CardTitle>
                    <CardDescription>
                      Task runs per agent in the last 24 hours
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {executionBarData.length === 0 ? (
                      <p className="text-center text-sm text-muted-foreground py-12">
                        No execution data yet
                      </p>
                    ) : (
                      <ChartContainer config={executionChartConfig} className="h-[280px] w-full">
                        <BarChart
                          accessibilityLayer
                          data={executionBarData}
                          layout="vertical"
                          margin={{ left: 4, right: 16 }}
                        >
                          <CartesianGrid horizontal={false} />
                          <YAxis
                            dataKey="agent"
                            type="category"
                            tickLine={false}
                            axisLine={false}
                            width={90}
                            tick={{ fontSize: 12 }}
                          />
                          <XAxis type="number" hide />
                          <ChartTooltip
                            cursor={{ fill: "var(--color-muted)", opacity: 0.3 }}
                            content={
                              <ChartTooltipContent
                                indicator="line"
                                nameKey="agent"
                                formatter={(value) => [`${value} runs`, "Executions"]}
                              />
                            }
                          />
                          <Bar
                            dataKey="executions"
                            radius={[0, 6, 6, 0]}
                            barSize={24}
                          />
                        </BarChart>
                      </ChartContainer>
                    )}
                  </CardContent>
                </Card>

                {/* Pie Chart – Token Distribution */}
                <Card className="lg:col-span-2">
                  <CardHeader>
                    <CardTitle>Token Distribution</CardTitle>
                    <CardDescription>
                      Token usage share by agent
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {tokenPieData.length === 0 || totalTokens === 0 ? (
                      <p className="text-center text-sm text-muted-foreground py-12">
                        No token data yet
                      </p>
                    ) : (
                      <ChartContainer config={tokenPieConfig} className="mx-auto aspect-square h-[280px]">
                        <PieChart>
                          <ChartTooltip
                            content={
                              <ChartTooltipContent
                                nameKey="agent"
                                formatter={(value) => [`${Number(value).toLocaleString()} tokens`, ""]}
                              />
                            }
                          />
                          <Pie
                            data={tokenPieData}
                            dataKey="tokens"
                            nameKey="agent"
                            cx="50%"
                            cy="50%"
                            innerRadius={55}
                            outerRadius={90}
                            paddingAngle={3}
                            strokeWidth={2}
                            stroke="var(--background)"
                          >
                            {tokenPieData.map((entry) => (
                              <Cell key={entry.agent} fill={entry.fill} />
                            ))}
                          </Pie>
                          <ChartLegend
                            content={<ChartLegendContent nameKey="agent" />}
                            className="flex-wrap gap-2 text-xs"
                          />
                        </PieChart>
                      </ChartContainer>
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* ── Trace Waterfall ── */}
              {traces.some((t) => t.parent_trace_id) && (
                <TraceWaterfall traces={traces.slice(0, 20)} />
              )}

              {/* ── Traces ── */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Traces</CardTitle>
                  <CardDescription>Detailed execution history</CardDescription>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="all">
                    <TabsList className="mb-4">
                      <TabsTrigger value="all">All</TabsTrigger>
                      <TabsTrigger value="completed">Completed</TabsTrigger>
                      <TabsTrigger value="failed">Failed</TabsTrigger>
                    </TabsList>

                    <TabsContent value="all">
                      {tracesLoading ? (
                        <div className="flex justify-center py-8">
                          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                        </div>
                      ) : traces.length === 0 ? (
                        <p className="text-center text-muted-foreground py-8">
                          No traces yet
                        </p>
                      ) : (
                        <div className="space-y-2">
                          {traces.slice(0, 20).map((trace) => (
                            <TraceRow key={trace.id} trace={trace} />
                          ))}
                        </div>
                      )}
                    </TabsContent>

                    <TabsContent value="completed">
                      <div className="space-y-2">
                        {traces
                          .filter((t) => t.status === "completed")
                          .slice(0, 20)
                          .map((trace) => (
                            <TraceRow key={trace.id} trace={trace} />
                          ))}
                      </div>
                    </TabsContent>

                    <TabsContent value="failed">
                      <div className="space-y-2">
                        {traces
                          .filter((t) => t.status === "failed")
                          .slice(0, 20)
                          .map((trace) => (
                            <TraceRow key={trace.id} trace={trace} />
                          ))}
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
