"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { FileText, Loader2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { proposalsApi, documentsApi } from "@/lib/api";
import type { Document } from "@/lib/types";

function ProposalCard({ proposal }: { proposal: Document }) {
  const [viewOpen, setViewOpen] = useState(false);

  async function handleExport() {
    const response = await documentsApi.export(proposal.id, "markdown");
    if (!response.ok) return;
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    const disposition = response.headers.get("Content-Disposition");
    const filename = disposition?.match(/filename="(.+)"/)?.[1] ?? `${proposal.title}.md`;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  return (
    <>
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
            <Button variant="outline" size="sm" onClick={() => setViewOpen(true)}>
              View
            </Button>
            <Button variant="outline" size="sm" onClick={handleExport}>
              <Download className="h-4 w-4 mr-1" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Dialog open={viewOpen} onOpenChange={setViewOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>{proposal.title}</DialogTitle>
          </DialogHeader>
          <ScrollArea className="max-h-[60vh] pr-4">
            <div className="prose prose-sm dark:prose-invert whitespace-pre-wrap">
              {proposal.content}
            </div>
          </ScrollArea>
        </DialogContent>
      </Dialog>
    </>
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
