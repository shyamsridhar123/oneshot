"use client";

import { useRef, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Search, Loader2, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { researchApi } from "@/lib/api";
import { TrendCard } from "@/components/research/trend-card";
import { useAgentWebSocket } from "@/lib/websocket";
import { v4 as uuidv4 } from "uuid";

export default function ResearchPage() {
  const [query, setQuery] = useState("");
  const [companyName, setCompanyName] = useState("");
  const researchCardId = useRef(uuidv4());
  const briefingCardId = useRef(uuidv4());

  // Stable session ID for WebSocket agent status updates
  const [sessionId] = useState(() => `research-${uuidv4()}`);

  // Connect WebSocket so AgentStatusPanel in the layout receives live events
  useAgentWebSocket(sessionId);

  const researchMutation = useMutation({
    mutationFn: researchApi.query,
    onMutate: () => {
      researchCardId.current = uuidv4();
    },
  });

  const briefingMutation = useMutation({
    mutationFn: researchApi.briefing,
    onMutate: () => {
      briefingCardId.current = uuidv4();
    },
  });

  return (
    <div className="flex flex-col h-full">
      <div className="flex h-14 items-center border-b px-4">
        <h1 className="text-lg font-semibold">Trends</h1>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <Tabs defaultValue="query" className="w-full">
          <TabsList className="mb-4">
            <TabsTrigger value="query">Research Query</TabsTrigger>
            <TabsTrigger value="briefing">Client Briefing</TabsTrigger>
          </TabsList>

          <TabsContent value="query">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Research Query
                </CardTitle>
                <CardDescription>
                  Ask our AI agents to research any topic, industry, or trend
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="What would you like to research? e.g., 'Latest trends in AI for healthcare' or 'Competitive analysis of cloud providers'"
                  className="min-h-32"
                />
                <div className="flex items-center gap-4">
                  <Button
                    onClick={() =>
                      researchMutation.mutate({
                        query,
                        research_type: "comprehensive",
                        session_id: sessionId,
                      })
                    }
                    disabled={!query.trim() || researchMutation.isPending}
                  >
                    {researchMutation.isPending && (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    )}
                    Start Research
                  </Button>
                  <div className="flex gap-2">
                    <Badge variant="outline">Web</Badge>
                    <Badge variant="outline">News</Badge>
                    <Badge variant="outline">Company Data</Badge>
                  </div>
                </div>

                {researchMutation.data && (
                  <div className="mt-4 animate-fade-in-up">
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
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="briefing">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Client Briefing
                </CardTitle>
                <CardDescription>
                  Generate a comprehensive briefing document for a client or prospect
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Company Name</label>
                  <Input
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    placeholder="e.g., Microsoft, Apple, Salesforce"
                  />
                </div>
                <Button
                  onClick={() =>
                    briefingMutation.mutate({
                      company_name: companyName,
                      session_id: sessionId,
                    })
                  }
                  disabled={!companyName.trim() || briefingMutation.isPending}
                >
                  {briefingMutation.isPending && (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  )}
                  Generate Briefing
                </Button>

                {briefingMutation.data && (
                  <div className="mt-4 animate-fade-in-up">
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
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
