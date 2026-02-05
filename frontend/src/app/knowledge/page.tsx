"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { BookOpen, Search, Loader2, Tag } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { knowledgeApi } from "@/lib/api";
import type { KnowledgeItem } from "@/lib/types";

function KnowledgeCard({ item }: { item: KnowledgeItem }) {
  return (
    <Card className="hover:border-primary/50 transition-colors">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">{item.title}</CardTitle>
          {item.score !== undefined && (
            <Badge variant="secondary">{Math.round(item.score * 100)}%</Badge>
          )}
        </div>
        <CardDescription className="flex items-center gap-2">
          <Badge variant="outline">{item.category}</Badge>
          {item.industry && <Badge variant="outline">{item.industry}</Badge>}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground line-clamp-4 mb-3">
          {item.content}
        </p>
        {item.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {item.tags.slice(0, 5).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                <Tag className="h-3 w-3 mr-1" />
                {tag}
              </Badge>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default function KnowledgePage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<KnowledgeItem[]>([]);

  const { data: knowledgeItems = [], isLoading } = useQuery({
    queryKey: ["knowledge"],
    queryFn: () => knowledgeApi.list(),
  });

  const searchMutation = useMutation({
    mutationFn: knowledgeApi.search,
    onSuccess: (results) => {
      setSearchResults(results);
    },
  });

  const handleSearch = () => {
    if (searchQuery.trim()) {
      searchMutation.mutate({ query: searchQuery, limit: 10 });
    }
  };

  const displayItems = searchResults.length > 0 ? searchResults : knowledgeItems;

  return (
    <div className="flex flex-col h-full">
      <div className="flex h-14 items-center border-b px-6">
        <h1 className="text-xl font-semibold">Knowledge Base</h1>
      </div>

      <div className="border-b p-4">
        <div className="flex gap-2 max-w-xl">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Search knowledge base..."
              className="pl-9"
            />
          </div>
          <Button
            onClick={handleSearch}
            disabled={!searchQuery.trim() || searchMutation.isPending}
          >
            {searchMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Search"
            )}
          </Button>
          {searchResults.length > 0 && (
            <Button
              variant="outline"
              onClick={() => {
                setSearchResults([]);
                setSearchQuery("");
              }}
            >
              Clear
            </Button>
          )}
        </div>
      </div>

      <ScrollArea className="flex-1 p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : displayItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
            <BookOpen className="h-12 w-12 mb-4 opacity-50" />
            <p className="text-lg font-medium">No knowledge items found</p>
            <p className="text-sm">
              {searchQuery
                ? "Try a different search term"
                : "Add knowledge to your base"}
            </p>
          </div>
        ) : (
          <>
            {searchResults.length > 0 && (
              <p className="text-sm text-muted-foreground mb-4">
                Found {searchResults.length} results for &quot;{searchQuery}&quot;
              </p>
            )}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {displayItems.map((item) => (
                <KnowledgeCard key={item.id} item={item} />
              ))}
            </div>
          </>
        )}
      </ScrollArea>
    </div>
  );
}
