"use client";

import { useQuery } from "@tanstack/react-query";
import { BarChart3, Activity, Zap, Clock, Loader2 } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { analyticsApi } from "@/lib/api";
import type { AgentTrace, AgentName } from "@/lib/types";

const agentColors: Record<AgentName, string> = {
  orchestrator: "bg-purple-500",
  strategist: "bg-blue-500",
  researcher: "bg-green-500",
  analyst: "bg-orange-500",
  scribe: "bg-pink-500",
  advisor: "bg-cyan-500",
  memory: "bg-yellow-500",
};

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
      <div
        className={`h-2 w-2 rounded-full ${agentColors[trace.agent_name]}`}
      />
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-medium capitalize">{trace.agent_name}</span>
          {trace.task_type && (
            <span className="text-sm text-muted-foreground">
              • {trace.task_type}
            </span>
          )}
        </div>
        <div className="text-xs text-muted-foreground">
          {new Date(trace.started_at).toLocaleString('en-US', { timeZone: 'America/New_York' })}
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
}: {
  title: string;
  value: string | number;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

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

  return (
    <div className="flex flex-col h-full">
      <div className="flex h-14 items-center border-b px-6">
        <h1 className="text-xl font-semibold">Analytics</h1>
      </div>

      <ScrollArea className="flex-1 p-6">
        {metricsLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <>
            {/* Metrics Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
              <MetricsCard
                title="Total Executions"
                value={metrics?.total_executions || 0}
                description="In the last 24 hours"
                icon={Activity}
              />
              <MetricsCard
                title="Active Agents"
                value={metrics?.agent_stats.length || 0}
                description="Agents with activity"
                icon={BarChart3}
              />
              <MetricsCard
                title="Total Tokens"
                value={Math.round(totalTokens).toLocaleString()}
                description="Tokens used today"
                icon={Zap}
              />
              <MetricsCard
                title="Avg Response Time"
                value={`${(avgResponseTime / 1000).toFixed(1)}s`}
                description="Average task duration"
                icon={Clock}
              />
            </div>

            {/* Agent Stats */}
            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Agent Performance</CardTitle>
                <CardDescription>
                  Execution stats per agent (last 24 hours)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {metrics?.agent_stats.map((stat) => (
                    <div key={stat.agent} className="flex items-center gap-4">
                      <div
                        className={`h-3 w-3 rounded-full ${agentColors[stat.agent]}`}
                      />
                      <span className="font-medium capitalize w-24">
                        {stat.agent}
                      </span>
                      <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full ${agentColors[stat.agent]}`}
                          style={{
                            width: `${(stat.executions / (metrics.total_executions || 1)) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground w-20 text-right">
                        {stat.executions} runs
                      </span>
                      <span className="text-sm text-muted-foreground w-28 text-right">
                        {Math.round(stat.avg_tokens * stat.executions).toLocaleString()} tokens
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Traces */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Traces</CardTitle>
                <CardDescription>
                  Detailed execution history
                </CardDescription>
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
      </ScrollArea>
    </div>
  );
}
