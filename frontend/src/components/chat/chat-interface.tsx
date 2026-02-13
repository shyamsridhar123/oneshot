"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Send,
  Plus,
  Loader2,
  Sparkles,
  ArrowUp,
  MessageSquarePlus,
  Zap,
  PenLine,
  BarChart3,
  Globe,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { chatApi } from "@/lib/api";
import { useStore, EMPTY_MESSAGES } from "@/lib/store";
import { useAgentWebSocket } from "@/lib/websocket";
import type { Message, Conversation } from "@/lib/types";
import { ConversationList } from "./conversation-list";
import { MemoizedMarkdown } from "./memoized-markdown";
import { v4 as uuidv4 } from "uuid";

/* ─────────────────────────────────────────────
   Message Bubble — glassmorphic card design
   Inspired by: spline.design gradients, Framer Marketplace glass cards
   ───────────────────────────────────────────── */

function MessageBubble({
  message,
  isLatest,
}: {
  message: Message;
  isLatest: boolean;
}) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className={`flex gap-3 max-w-[80%] ml-auto flex-row-reverse animate-fade-in-up ${isLatest ? "" : "[animation-duration:0s]"}`}>
        {/* Gradient ring avatar */}
        <div className="relative h-8 w-8 shrink-0">
          <div className="absolute inset-0 rounded-full bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 opacity-60 blur-[2px]" />
          <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 text-xs font-semibold text-white shadow-lg shadow-indigo-500/20">
            U
          </div>
        </div>
        {/* Message card */}
        <div className="group relative overflow-hidden rounded-2xl rounded-tr-md">
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-white/10" />
          <div className="relative px-4 py-3 text-sm text-white">
            <div className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</div>
            <div className="mt-2 text-[10px] text-white/50 font-medium">
              {new Date(message.created_at).toLocaleTimeString("en-US", {
                timeZone: "America/New_York",
                hour: "numeric",
                minute: "2-digit",
              })}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex gap-3.5 animate-fade-in-up ${isLatest ? "" : "[animation-duration:0s]"}`}>
      {/* Glowing assistant avatar */}
      <div className="relative h-8 w-8 shrink-0 mt-0.5">
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-violet-500 to-cyan-400 opacity-40 blur-[3px] animate-pulse-glow" />
        <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 via-blue-500 to-cyan-400 text-xs font-bold text-white ring-2 ring-white/10">
          <Sparkles className="h-3.5 w-3.5" />
        </div>
      </div>
      {/* Glass card response */}
      <div className="flex-1 min-w-0 overflow-hidden group">
        <div className="relative overflow-hidden rounded-2xl rounded-tl-md border border-white/[0.08] bg-card/80 backdrop-blur-xl shadow-xl shadow-black/5 dark:shadow-black/20 px-5 py-4 transition-all duration-300 hover:border-white/[0.12] hover:shadow-2xl">
          {/* Subtle top gradient accent */}
          <div className="absolute top-0 left-4 right-4 h-px bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />
          <div className="prose prose-sm dark:prose-invert prose-p:my-1.5 prose-p:leading-relaxed prose-headings:mt-4 prose-headings:mb-1.5 prose-headings:leading-snug prose-h2:text-base prose-h2:font-bold prose-h3:text-sm prose-h3:font-semibold prose-h4:text-[13px] prose-h4:font-semibold prose-ul:my-1.5 prose-ol:my-1.5 prose-li:my-0.5 prose-li:leading-relaxed prose-pre:my-2 prose-blockquote:my-2 prose-hr:my-3 prose-strong:text-foreground max-w-none text-sm text-foreground/90 break-words [overflow-wrap:anywhere] overflow-x-auto">
            <MemoizedMarkdown content={message.content} id={message.id} />
          </div>
          <div className="mt-3 flex items-center gap-2 text-[10px] text-muted-foreground/50 font-medium">
            <span className="inline-block h-1 w-1 rounded-full bg-violet-400/60" />
            {new Date(message.created_at).toLocaleTimeString("en-US", {
              timeZone: "America/New_York",
              hour: "numeric",
              minute: "2-digit",
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

function MessageSkeleton() {
  return (
    <div className="flex gap-3.5 animate-fade-in">
      <div className="h-8 w-8 shrink-0 rounded-full bg-gradient-to-br from-violet-500/20 to-cyan-400/20 animate-pulse" />
      <div className="flex-1 space-y-3 rounded-2xl border border-white/[0.06] bg-card/60 backdrop-blur-xl p-5">
        <Skeleton className="h-3 w-3/4 rounded-full" />
        <Skeleton className="h-3 w-1/2 rounded-full" />
        <Skeleton className="h-3 w-2/3 rounded-full" />
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Quick Action Suggestions
   ───────────────────────────────────────────── */

const quickActions = [
  { icon: PenLine, label: "Draft a LinkedIn post", prompt: "Draft a professional LinkedIn post about our latest product launch" },
  { icon: Globe, label: "Research competitors", prompt: "Research our top 3 competitors' social media strategy" },
  { icon: BarChart3, label: "Analyze engagement", prompt: "Analyze our social media engagement metrics for the past month" },
  { icon: Zap, label: "Create campaign", prompt: "Create a multi-platform social media campaign for brand awareness" },
];

/* ─────────────────────────────────────────────
   Empty State — hero-style welcome
   Inspired by: brandsite.design typography, Spline mesh gradients
   ───────────────────────────────────────────── */

function EmptyState({ onAction }: { onAction: (prompt: string) => void }) {
  return (
    <div className="flex h-full items-center justify-center px-6">
      <div className="relative max-w-lg w-full text-center space-y-8">
        {/* Background glow */}
        <div className="absolute -top-20 left-1/2 -translate-x-1/2 h-40 w-80 rounded-full bg-gradient-to-r from-violet-500/15 via-blue-500/15 to-cyan-500/15 blur-3xl" />

        {/* Logo mark */}
        <div className="relative mx-auto flex h-16 w-16 items-center justify-center">
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-violet-500 to-cyan-400 opacity-20 blur-xl" />
          <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500/10 to-cyan-400/10 border border-white/[0.08] backdrop-blur-sm">
            <Sparkles className="h-7 w-7 text-violet-400" />
          </div>
        </div>

        <div className="relative space-y-3">
          <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-b from-foreground to-foreground/60 bg-clip-text text-transparent">
            What can I help you create?
          </h1>
          <p className="text-sm text-muted-foreground/70 max-w-sm mx-auto leading-relaxed">
            Describe what you need and I&apos;ll orchestrate a team of AI agents to research, strategize, write, and optimize your content.
          </p>
        </div>

        {/* Quick action cards */}
        <div className="relative grid grid-cols-2 gap-2.5">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.label}
                onClick={() => onAction(action.prompt)}
                className="group relative flex items-center gap-3 rounded-xl border border-white/[0.06] bg-card/50 backdrop-blur-sm px-4 py-3.5 text-left text-sm transition-all duration-200 hover:border-violet-500/20 hover:bg-violet-500/[0.04] hover:shadow-lg hover:shadow-violet-500/5"
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-violet-500/10 to-blue-500/10 text-violet-400 group-hover:from-violet-500/20 group-hover:to-blue-500/20 transition-colors">
                  <Icon className="h-4 w-4" />
                </div>
                <span className="text-muted-foreground group-hover:text-foreground transition-colors font-medium">
                  {action.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Thinking Indicator — animated glass card
   Inspired by: Spline loading states, Framer micro-interactions
   ───────────────────────────────────────────── */

function ThinkingIndicator() {
  return (
    <div className="flex gap-3.5 animate-fade-in-up">
      <div className="relative h-8 w-8 shrink-0 mt-0.5">
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-violet-500 to-cyan-400 opacity-50 blur-[3px] animate-pulse" />
        <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 via-blue-500 to-cyan-400 text-white ring-2 ring-white/10">
          <Sparkles className="h-3.5 w-3.5 animate-spin" style={{ animationDuration: "3s" }} />
        </div>
      </div>
      <div className="relative overflow-hidden rounded-2xl rounded-tl-md border border-white/[0.08] bg-card/60 backdrop-blur-xl px-5 py-4 shadow-lg">
        {/* Animated border beam */}
        <div className="absolute inset-0 rounded-2xl">
          <div className="absolute inset-[-1px] rounded-2xl bg-gradient-conic from-violet-500/40 via-transparent to-violet-500/40 animate-spin" style={{ animationDuration: "4s" }} />
          <div className="absolute inset-[1px] rounded-2xl bg-card/90 backdrop-blur-xl" />
        </div>
        <div className="relative flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="h-2 w-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: "0ms" }} />
            <span className="h-2 w-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "150ms" }} />
            <span className="h-2 w-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
          <span className="text-sm text-muted-foreground/70 font-medium">
            Agents are collaborating...
          </span>
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   Main Chat Interface
   ───────────────────────────────────────────── */

export function ChatInterface() {
  const queryClient = useQueryClient();
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [input, setInput] = useState("");
  const [inputFocused, setInputFocused] = useState(false);
  const streamingMsgIdRef = useRef<string | null>(null);

  const activeConversationId = useStore((s) => s.activeConversationId);
  const setActiveConversation = useStore((s) => s.setActiveConversation);
  const setConversations = useStore((s) => s.setConversations);
  const addConversation = useStore((s) => s.addConversation);
  const setMessages = useStore((s) => s.setMessages);
  const addMessage = useStore((s) => s.addMessage);
  const isLoading = useStore((s) => s.isLoading);
  const setLoading = useStore((s) => s.setLoading);
  const setStreaming = useStore((s) => s.setStreaming);
  const isStreaming = useStore((s) => s.isStreaming);

  const messages = useStore((s) =>
    s.activeConversationId
      ? s.messages[s.activeConversationId] ?? EMPTY_MESSAGES
      : EMPTY_MESSAGES
  );

  useAgentWebSocket(activeConversationId, {
    onAgentCompleted: (data) => {
      if (data.agent_name === "orchestrator" && activeConversationId) {
        setTimeout(() => {
          queryClient.invalidateQueries({
            queryKey: ["messages", activeConversationId],
          });
        }, 100);
      }
    },
  });

  const { data: conversations = [] } = useQuery({
    queryKey: ["conversations"],
    queryFn: () => chatApi.listConversations(),
  });

  useEffect(() => {
    setConversations(conversations);
  }, [conversations, setConversations]);

  const { data: loadedMessages, isLoading: messagesLoading } = useQuery({
    queryKey: ["messages", activeConversationId],
    queryFn: () =>
      activeConversationId
        ? chatApi.listMessages(activeConversationId)
        : Promise.resolve([]),
    enabled: !!activeConversationId,
  });

  useEffect(() => {
    if (loadedMessages && activeConversationId && !isLoading) {
      setMessages(activeConversationId, loadedMessages);
    }
  }, [loadedMessages, activeConversationId, setMessages, isLoading]);

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
      // If we created a streaming placeholder, update it with the final
      // server response (authoritative content). Otherwise add normally.
      const placeholderId = streamingMsgIdRef.current;
      if (placeholderId) {
        const state = useStore.getState();
        const msgs = state.messages[conversationId];
        if (msgs) {
          const updated = msgs.map((m) =>
            m.id === placeholderId
              ? { ...m, id: response.id, content: response.content, created_at: response.created_at }
              : m
          );
          state.setMessages(conversationId, updated);
        }
        streamingMsgIdRef.current = null;
      } else {
        addMessage(conversationId, response);
      }
      setStreaming(false, null);
      setLoading(false);
      queryClient.invalidateQueries({ queryKey: ["conversations"] });
    },
    onError: () => {
      streamingMsgIdRef.current = null;
      setStreaming(false, null);
      setLoading(false);
    },
  });

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

  const doSend = useCallback(
    (content: string) => {
      if (!content.trim()) return;

      let conversationId = activeConversationId;

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

      const userMessage: Message = {
        id: uuidv4(),
        conversation_id: conversationId,
        role: "user",
        content: content.trim(),
        created_at: new Date().toISOString(),
        metadata: {},
      };
      addMessage(conversationId, userMessage);

      // Add an empty assistant placeholder so stream.token events can append to it
      const placeholderId = uuidv4();
      streamingMsgIdRef.current = placeholderId;
      const placeholderMessage: Message = {
        id: placeholderId,
        conversation_id: conversationId,
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
        metadata: {},
      };
      addMessage(conversationId, placeholderMessage);

      setInput("");
      setLoading(true);
      setStreaming(true, placeholderId);

      sendMutation.mutate({ conversationId, content: content.trim() });
    },
    [
      activeConversationId,
      addConversation,
      setActiveConversation,
      addMessage,
      setLoading,
      sendMutation,
    ]
  );

  const handleSend = useCallback(() => {
    doSend(input);
  }, [input, doSend]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 160) + "px";
  };

  return (
    <div className="flex h-full overflow-hidden">
      {/* Conversation sidebar — frosted glass */}
      <div className="hidden md:flex w-56 shrink-0 flex-col border-r border-white/[0.06] bg-card/30 backdrop-blur-md overflow-hidden min-h-0">
        <div className="flex h-14 shrink-0 items-center justify-between border-b border-white/[0.06] px-4">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground/70">Chats</h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleNewConversation}
            className="h-7 w-7 rounded-lg hover:bg-violet-500/10 text-muted-foreground hover:text-violet-400 transition-colors"
          >
            <MessageSquarePlus className="h-4 w-4" />
          </Button>
        </div>
        <ConversationList
          conversations={conversations}
          activeId={activeConversationId}
          onSelect={setActiveConversation}
        />
      </div>

      {/* Chat area */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        {/* Header — minimal glass bar */}
        <div className="flex h-12 shrink-0 items-center border-b border-white/[0.06] px-5 bg-card/40 backdrop-blur-md">
          <div className="flex items-center gap-2.5">
            <div className="h-2 w-2 rounded-full bg-gradient-to-r from-violet-400 to-cyan-400" />
            <h1 className="text-sm font-semibold truncate text-foreground/90">
              {activeConversationId
                ? conversations.find((c) => c.id === activeConversationId)
                    ?.title || "Chat"
                : "New Chat"}
            </h1>
          </div>
        </div>

        {/* Messages — generous spacing, subtle grid bg */}
        <div
          className="flex-1 overflow-y-auto overflow-x-hidden"
          ref={scrollRef}
        >
          <div className="mx-auto max-w-3xl px-6 py-6">
            <div className="space-y-6">
              {messagesLoading ? (
                <>
                  <MessageSkeleton />
                  <MessageSkeleton />
                </>
              ) : messages.length === 0 ? (
                <EmptyState onAction={doSend} />
              ) : (
                messages.map((msg, i) =>
                  msg.role === "assistant" && !msg.content ? null : (
                    <MessageBubble
                      key={msg.id}
                      message={msg}
                      isLatest={i === messages.length - 1}
                    />
                  )
                )
              )}

              {isLoading && !isStreaming && <ThinkingIndicator />}
              {isLoading && isStreaming && messages.length > 0 && messages[messages.length - 1].content === "" && <ThinkingIndicator />}
            </div>
          </div>
        </div>

        {/* Input area — floating glass card */}
        <div className="shrink-0 px-6 pb-5 pt-2">
          <div className="mx-auto max-w-3xl">
            <div
              className={`relative rounded-2xl border transition-all duration-300 ${
                inputFocused
                  ? "border-violet-500/30 shadow-lg shadow-violet-500/5 bg-card/80"
                  : "border-white/[0.08] bg-card/50"
              } backdrop-blur-xl`}
            >
              {/* Focus glow */}
              {inputFocused && (
                <div className="absolute -inset-px rounded-2xl bg-gradient-to-r from-violet-500/20 via-blue-500/20 to-cyan-500/20 blur-sm -z-10" />
              )}
              <div className="flex items-end gap-2 p-3">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  onFocus={() => setInputFocused(true)}
                  onBlur={() => setInputFocused(false)}
                  placeholder="Describe the content you need..."
                  rows={1}
                  className="flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-foreground placeholder:text-muted-foreground/40 focus:outline-none"
                  style={{ maxHeight: "160px" }}
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  size="icon"
                  className="h-9 w-9 shrink-0 rounded-xl bg-gradient-to-r from-violet-500 to-blue-500 text-white shadow-lg shadow-violet-500/20 hover:shadow-xl hover:shadow-violet-500/30 hover:from-violet-600 hover:to-blue-600 disabled:opacity-30 disabled:shadow-none transition-all duration-200 border-0"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <ArrowUp className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <div className="flex items-center justify-between px-5 pb-2.5 text-[10px] text-muted-foreground/40">
                <span>Enter to send, Shift+Enter for new line</span>
                <span className="flex items-center gap-1">
                  <Sparkles className="h-2.5 w-2.5" />
                  7 agents ready
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
