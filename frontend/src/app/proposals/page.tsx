"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FileText, Plus, Loader2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { proposalsApi, documentsApi } from "@/lib/api";
import type { Document, ProposalRequest } from "@/lib/types";

function ProposalCard({ proposal }: { proposal: Document }) {
  return (
    <Card className="hover:border-primary/50 transition-colors">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-5 w-5 text-primary" />
            <CardTitle className="text-base">{proposal.title}</CardTitle>
          </div>
          <Badge variant="outline">{proposal.format}</Badge>
        </div>
        <CardDescription>
          Created {new Date(proposal.created_at).toLocaleDateString('en-US', { timeZone: 'America/New_York' })}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
          {proposal.content.substring(0, 200)}...
        </p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" asChild>
            <a href={`/proposals/${proposal.id}`}>View</a>
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => documentsApi.export(proposal.id, "pdf")}
          >
            <Download className="h-4 w-4 mr-1" />
            Export
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function GenerateProposalDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState<ProposalRequest>({
    client_name: "",
    client_industry: "",
    engagement_type: "",
    scope_description: "",
    budget_range: "",
    timeline: "",
    additional_context: "",
  });

  const generateMutation = useMutation({
    mutationFn: proposalsApi.generate,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["proposals"] });
      setOpen(false);
      setFormData({
        client_name: "",
        client_industry: "",
        engagement_type: "",
        scope_description: "",
        budget_range: "",
        timeline: "",
        additional_context: "",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    generateMutation.mutate(formData);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Generate Proposal
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Generate New Proposal</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Client Name</label>
              <Input
                value={formData.client_name}
                onChange={(e) =>
                  setFormData({ ...formData, client_name: e.target.value })
                }
                placeholder="Acme Corp"
                required
              />
            </div>
            <div>
              <label className="text-sm font-medium">Industry</label>
              <Input
                value={formData.client_industry}
                onChange={(e) =>
                  setFormData({ ...formData, client_industry: e.target.value })
                }
                placeholder="Technology"
                required
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Engagement Type</label>
            <Input
              value={formData.engagement_type}
              onChange={(e) =>
                setFormData({ ...formData, engagement_type: e.target.value })
              }
              placeholder="Digital Transformation"
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium">Scope Description</label>
            <Textarea
              value={formData.scope_description}
              onChange={(e) =>
                setFormData({ ...formData, scope_description: e.target.value })
              }
              placeholder="Describe the project scope..."
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Budget Range</label>
              <Input
                value={formData.budget_range || ""}
                onChange={(e) =>
                  setFormData({ ...formData, budget_range: e.target.value })
                }
                placeholder="$100k - $500k"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Timeline</label>
              <Input
                value={formData.timeline || ""}
                onChange={(e) =>
                  setFormData({ ...formData, timeline: e.target.value })
                }
                placeholder="3-6 months"
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Additional Context</label>
            <Textarea
              value={formData.additional_context || ""}
              onChange={(e) =>
                setFormData({ ...formData, additional_context: e.target.value })
              }
              placeholder="Any additional information..."
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={generateMutation.isPending}>
              {generateMutation.isPending && (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              )}
              Generate
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export default function ProposalsPage() {
  const { data: proposals = [], isLoading } = useQuery({
    queryKey: ["proposals"],
    queryFn: () => proposalsApi.list(),
  });

  return (
    <div className="flex flex-col h-full">
      <div className="flex h-14 items-center justify-between border-b px-6">
        <h1 className="text-xl font-semibold">Proposals</h1>
        <GenerateProposalDialog />
      </div>

      <ScrollArea className="flex-1 p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : proposals.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
            <FileText className="h-12 w-12 mb-4 opacity-50" />
            <p className="text-lg font-medium">No proposals yet</p>
            <p className="text-sm">Generate your first proposal using AI agents</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {proposals.map((proposal) => (
              <ProposalCard key={proposal.id} proposal={proposal} />
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
