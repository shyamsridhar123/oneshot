"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Send, Plus, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar } from "@/components/ui/avatar";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { chatApi } from "@/lib/api";
import { useStore, EMPTY_MESSAGES } from "@/lib/store";
import { useAgentWebSocket } from "@/lib/websocket";
import type { Message, Conversation } from "@/lib/types";
import { ConversationList } from "./conversation-list";
import { v4 as uuidv4 } from "uuid";

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 max-w-[85%]",
        isUser ? "ml-auto flex-row-reverse" : ""
      )}
    >
      <Avatar
        className={cn(
          "h-8 w-8 shrink-0 flex items-center justify-center text-sm font-medium",
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        )}
      >
        {isUser ? "U" : "F"}
      </Avatar>
      <div
        className={cn(
          "rounded-lg px-4 py-2 text-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground"
        )}
      >
        <div className="whitespace-pre-wrap">{message.content}</div>
        <div
          className={cn(
            "mt-1 text-xs",
            isUser ? "text-primary-foreground/70" : "text-muted-foreground"
          )}
        >
          {new Date(message.created_at).toLocaleTimeString('en-US', { timeZone: 'America/New_York' })}
        </div>
      </div>
    </div>
  );
}

function MessageSkeleton() {
  return (
    <div className="flex gap-3">
      <Skeleton className="h-8 w-8 rounded-full" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-48" />
        <Skeleton className="h-4 w-32" />
      </div>
    </div>
  );
}

export function ChatInterface() {
  const queryClient = useQueryClient();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState("");

  // Select store state with individual selectors to avoid unnecessary re-renders
  const activeConversationId = useStore((s) => s.activeConversationId);
  const setActiveConversation = useStore((s) => s.setActiveConversation);
  const setConversations = useStore((s) => s.setConversations);
  const addConversation = useStore((s) => s.addConversation);
  const setMessages = useStore((s) => s.setMessages);
  const addMessage = useStore((s) => s.addMessage);
  const isLoading = useStore((s) => s.isLoading);
  const setLoading = useStore((s) => s.setLoading);

  // Get messages for active conversation only
  const messages = useStore((s) =>
    s.activeConversationId
      ? s.messages[s.activeConversationId] ?? EMPTY_MESSAGES
      : EMPTY_MESSAGES
  );

  // Connect WebSocket when conversation is active
  useAgentWebSocket(activeConversationId, {
    onAgentCompleted: (data) => {
      // Only refetch messages when orchestrator completes (final step)
      // This prevents premature refetches that could overwrite optimistic updates
      if (data.agent_name === "orchestrator" && activeConversationId) {
        setTimeout(() => {
          queryClient.invalidateQueries({
            queryKey: ["messages", activeConversationId],
          });
        }, 100);
      }
    },
  });

  // Fetch conversations
  const { data: conversations = [] } = useQuery({
    queryKey: ["conversations"],
    queryFn: () => chatApi.listConversations(),
  });

  useEffect(() => {
    setConversations(conversations);
  }, [conversations, setConversations]);

  // Fetch messages for active conversation
  const { data: loadedMessages, isLoading: messagesLoading } = useQuery({
    queryKey: ["messages", activeConversationId],
    queryFn: () =>
      activeConversationId
        ? chatApi.listMessages(activeConversationId)
        : Promise.resolve([]),
    enabled: !!activeConversationId,
  });

  useEffect(() => {
    // Only sync from server if we have loaded messages and not currently loading/sending
    // This prevents overwriting optimistic updates during active operations
    if (loadedMessages && activeConversationId && !isLoading) {
      setMessages(activeConversationId, loadedMessages);
    }
  }, [loadedMessages, activeConversationId, setMessages, isLoading]);

  // Send message mutation
  const sendMutation = useMutation({
    mutationFn: async ({
      conversationId,
      content,
    }: {
      conversationId: string;
      content: string;
    }) => {
      return chatApi.sendMessage(conversationId, { content });
    },
    onSuccess: (response, { conversationId }) => {
      addMessage(conversationId, response);
      setLoading(false);
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
    onError: () => {
      setLoading(false);
    },
  });

  // Auto-scroll on new messages
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleNewConversation = useCallback(() => {
    const newId = uuidv4();
    const newConv: Conversation = {
      id: newId,
      title: "New Conversation",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      metadata: {},
      message_count: 0,
    };
    addConversation(newConv);
    setActiveConversation(newId);
  }, [addConversation, setActiveConversation]);

  const handleSend = useCallback(() => {
    const content = input.trim();
    if (!content) return;

    let conversationId = activeConversationId;

    // Create new conversation if none active
    if (!conversationId) {
      conversationId = uuidv4();
      const newConv: Conversation = {
        id: conversationId,
        title: content.slice(0, 50) + (content.length > 50 ? "..." : ""),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        metadata: {},
        message_count: 0,
      };
      addConversation(newConv);
      setActiveConversation(conversationId);
    }

    // Add optimistic user message
    const userMessage: Message = {
      id: uuidv4(),
      conversation_id: conversationId,
      role: "user",
      content,
      created_at: new Date().toISOString(),
      metadata: {},
    };
    addMessage(conversationId, userMessage);
    setInput("");
    setLoading(true);

    sendMutation.mutate({ conversationId, content });
  }, [
    input,
    activeConversationId,
    addConversation,
    setActiveConversation,
    addMessage,
    setLoading,
    sendMutation,
  ]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-full">
      {/* Conversation sidebar */}
      <div className="hidden md:flex w-64 flex-col border-r">
        <div className="flex h-14 items-center justify-between border-b px-4">
          <h2 className="font-semibold">Conversations</h2>
          <Button variant="ghost" size="icon" onClick={handleNewConversation}>
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <ConversationList
          conversations={conversations}
          activeId={activeConversationId}
          onSelect={setActiveConversation}
        />
      </div>

      {/* Chat area */}
      <div className="flex flex-1 flex-col">
        {/* Header */}
        <div className="flex h-14 items-center border-b px-4">
          <h1 className="font-semibold">
            {activeConversationId
              ? conversations.find((c) => c.id === activeConversationId)
                  ?.title || "Chat"
              : "New Chat"}
          </h1>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-4" ref={scrollRef}>
          <div className="space-y-4">
            {messagesLoading ? (
              <>
                <MessageSkeleton />
                <MessageSkeleton />
              </>
            ) : messages.length === 0 ? (
              <div className="flex h-full items-center justify-center text-muted-foreground">
                <div className="text-center">
                  <p className="text-lg font-medium">Welcome to Federation</p>
                  <p className="text-sm">
                    Start a conversation with our AI agents
                  </p>
                </div>
              </div>
            ) : (
              messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
            )}

            {isLoading && (
              <div className="flex gap-3">
                <Avatar className="h-8 w-8 shrink-0 flex items-center justify-center bg-muted text-sm font-medium">
                  F
                </Avatar>
                <div className="flex items-center gap-2 rounded-lg bg-muted px-4 py-2 text-sm">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Agents are working...</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask Federation anything..."
              className="min-h-[44px] max-h-32 resize-none"
              disabled={isLoading}
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              size="icon"
              className="shrink-0"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}
