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
      <div className="flex flex-1 items-center justify-center p-4 text-muted-foreground/50">
        <div className="text-center text-xs">
          <MessageSquare className="mx-auto h-6 w-6 mb-2 opacity-30" />
          <p>No conversations</p>
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
              "group w-full rounded-xl px-3 py-2.5 text-left text-sm transition-all duration-200 relative overflow-hidden",
              activeId === conv.id
                ? "bg-violet-500/10 border border-violet-500/20 shadow-sm shadow-violet-500/5"
                : "border border-transparent hover:bg-white/[0.04] hover:border-white/[0.06]"
            )}
          >
            {activeId === conv.id && (
              <div className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-0.5 rounded-full bg-gradient-to-b from-violet-400 to-blue-400" />
            )}
            <div className={cn(
              "font-medium truncate text-xs",
              activeId === conv.id ? "text-violet-300" : "text-foreground/70 group-hover:text-foreground/90"
            )}>
              {conv.title || "Untitled"}
            </div>
            <div className="flex items-center gap-1.5 mt-1 text-[10px] text-muted-foreground/40">
              <span>{conv.message_count} msgs</span>
              <span className="h-0.5 w-0.5 rounded-full bg-muted-foreground/30" />
              <span>{new Date(conv.updated_at).toLocaleDateString("en-US", { timeZone: "America/New_York", month: "short", day: "numeric" })}</span>
            </div>
          </button>
        ))}
      </div>
    </ScrollArea>
  );
}
