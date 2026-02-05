"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Search, Loader2, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { researchApi } from "@/lib/api";

export default function ResearchPage() {
  const [query, setQuery] = useState("");
  const [companyName, setCompanyName] = useState("");

  const researchMutation = useMutation({
    mutationFn: researchApi.query,
  });

  const briefingMutation = useMutation({
    mutationFn: researchApi.briefing,
  });

  return (
    <div className="flex flex-col h-full">
      <div className="flex h-14 items-center border-b px-6">
        <h1 className="text-xl font-semibold">Research</h1>
      </div>

      <div className="flex-1 p-6">
        <Tabs defaultValue="query" className="w-full">
          <TabsList className="mb-6">
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
                  <Card className="mt-4 bg-muted/50">
                    <CardContent className="pt-4">
                      <p className="text-sm">
                        <strong>Status:</strong> {researchMutation.data.status}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {researchMutation.data.message}
                      </p>
                    </CardContent>
                  </Card>
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
                    briefingMutation.mutate({ company_name: companyName })
                  }
                  disabled={!companyName.trim() || briefingMutation.isPending}
                >
                  {briefingMutation.isPending && (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  )}
                  Generate Briefing
                </Button>

                {briefingMutation.data && (
                  <Card className="mt-4 bg-muted/50">
                    <CardContent className="pt-4">
                      <p className="text-sm">
                        <strong>Company:</strong> {briefingMutation.data.company_name}
                      </p>
                      <p className="text-sm">
                        <strong>Status:</strong> {briefingMutation.data.status}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {briefingMutation.data.message}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
