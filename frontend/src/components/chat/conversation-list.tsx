"use client";

import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import type { Conversation } from "@/lib/types";
import { MessageSquare } from "lucide-react";

interface ConversationListProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
}

export function ConversationList({
  conversations,
  activeId,
  onSelect,
}: ConversationListProps) {
  if (conversations.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center p-4 text-muted-foreground">
        <div className="text-center text-sm">
          <MessageSquare className="mx-auto h-8 w-8 mb-2 opacity-50" />
          <p>No conversations yet</p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1">
      <div className="space-y-1 p-2">
        {conversations.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelect(conv.id)}
            className={cn(
              "w-full rounded-lg px-3 py-2 text-left text-sm transition-colors",
              activeId === conv.id
                ? "bg-primary/10 text-primary"
                : "hover:bg-muted"
            )}
          >
            <div className="font-medium truncate">
              {conv.title || "Untitled"}
            </div>
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <span>{conv.message_count} messages</span>
              <span>·</span>
              <span>{new Date(conv.updated_at).toLocaleDateString('en-US', { timeZone: 'America/New_York' })}</span>
            </div>
          </button>
        ))}
      </div>
    </ScrollArea>
  );
}
