"use client";

import { memo, useMemo } from "react";
import { Heart, MessageCircle, Repeat2, Share, Bookmark, MoreHorizontal, ThumbsUp, Send as SendIcon } from "lucide-react";

interface PlatformContent {
  author?: string;
  handle?: string;
  avatar?: string;
  content: string;
  hashtags?: string[];
  imageDescription?: string;
  metrics?: {
    likes?: number;
    comments?: number;
    shares?: number;
    reposts?: number;
    impressions?: number;
  };
}

function parsePlatformContent(raw: string): PlatformContent | null {
  try {
    return JSON.parse(raw);
  } catch {
    // If JSON parse fails, treat the entire raw string as content
    return { content: raw };
  }
}

function formatNumber(n: number): string {
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`;
  return n.toString();
}

// --- LinkedIn Preview ---
const LinkedInPreview = memo(({ raw }: { raw: string }) => {
  const data = useMemo(() => parsePlatformContent(raw), [raw]);
  if (!data) return null;

  const author = data.author || "Your Brand";
  const handle = data.handle || "your-brand";

  return (
    <div className="my-4 max-w-[520px] rounded-xl border bg-card shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 pt-4 pb-2">
        <div className="h-12 w-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-white font-bold text-lg shrink-0">
          {author.charAt(0)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1">
            <span className="font-semibold text-sm text-foreground truncate">{author}</span>
            <span className="text-xs text-muted-foreground">- 1st</span>
          </div>
          <p className="text-xs text-muted-foreground truncate">@{handle}</p>
          <p className="text-xs text-muted-foreground">Just now - <span className="inline-block">🌐</span></p>
        </div>
        <MoreHorizontal className="h-5 w-5 text-muted-foreground shrink-0" />
      </div>

      {/* Content */}
      <div className="px-4 py-2">
        <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">{data.content}</p>
        {data.hashtags && data.hashtags.length > 0 && (
          <p className="mt-2 text-sm text-blue-600 dark:text-blue-400">
            {data.hashtags.map((h) => (h.startsWith("#") ? h : `#${h}`)).join(" ")}
          </p>
        )}
      </div>

      {/* Image placeholder */}
      {data.imageDescription && (
        <div className="mx-4 mb-3 rounded-lg bg-gradient-to-br from-slate-100 to-slate-200 dark:from-slate-800 dark:to-slate-700 h-48 flex items-center justify-center">
          <span className="text-xs text-muted-foreground italic px-4 text-center">{data.imageDescription}</span>
        </div>
      )}

      {/* Metrics bar */}
      {data.metrics && (
        <div className="flex items-center justify-between px-4 py-1.5 text-xs text-muted-foreground border-b">
          <div className="flex items-center gap-1">
            <span className="inline-flex items-center justify-center h-4 w-4 rounded-full bg-blue-500 text-[8px] text-white">👍</span>
            <span>{formatNumber(data.metrics.likes || 0)}</span>
          </div>
          <div className="flex gap-3">
            <span>{formatNumber(data.metrics.comments || 0)} comments</span>
            <span>{formatNumber(data.metrics.shares || 0)} reposts</span>
          </div>
        </div>
      )}

      {/* Action bar */}
      <div className="flex items-center justify-around px-2 py-1">
        {[
          { icon: ThumbsUp, label: "Like" },
          { icon: MessageCircle, label: "Comment" },
          { icon: Repeat2, label: "Repost" },
          { icon: SendIcon, label: "Send" },
        ].map(({ icon: Icon, label }) => (
          <button key={label} className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-muted-foreground hover:bg-muted/50 transition-colors">
            <Icon className="h-4 w-4" />
            <span className="text-xs font-medium">{label}</span>
          </button>
        ))}
      </div>

      {/* Platform badge */}
      <div className="px-4 py-1.5 bg-muted/30 border-t">
        <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">LinkedIn Preview</span>
      </div>
    </div>
  );
});
LinkedInPreview.displayName = "LinkedInPreview";

// --- Twitter/X Preview ---
const TwitterPreview = memo(({ raw }: { raw: string }) => {
  const data = useMemo(() => parsePlatformContent(raw), [raw]);
  if (!data) return null;

  const author = data.author || "Your Brand";
  const handle = data.handle || "yourbrand";

  // Split content by newlines to detect thread format
  const tweets = data.content.split(/\n---\n|\n\n(?=\d+\/)/);

  return (
    <div className="my-4 max-w-[520px] space-y-2">
      {tweets.map((tweet, idx) => (
        <div key={idx} className="rounded-xl border bg-card shadow-sm overflow-hidden">
          {/* Header */}
          <div className="flex items-start gap-3 px-4 pt-3 pb-0">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-gray-800 to-gray-900 dark:from-gray-200 dark:to-gray-300 flex items-center justify-center text-white dark:text-gray-900 font-bold text-sm shrink-0">
              {author.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1">
                <span className="font-bold text-sm text-foreground truncate">{author}</span>
                <svg className="h-4 w-4 text-blue-500 shrink-0" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.5 12.5c0-1.58-.875-2.95-2.148-3.6.154-.435.238-.905.238-1.4 0-2.21-1.71-3.998-3.818-3.998-.47 0-.92.084-1.336.25C14.818 2.415 13.51 1.5 12 1.5s-2.816.917-3.437 2.25c-.415-.165-.866-.25-1.336-.25-2.11 0-3.818 1.79-3.818 4 0 .494.083.964.237 1.4-1.272.65-2.147 2.018-2.147 3.6 0 1.495.782 2.798 1.942 3.486-.02.17-.032.34-.032.514 0 2.21 1.708 4 3.818 4 .47 0 .92-.086 1.335-.25.62 1.334 1.926 2.25 3.437 2.25 1.512 0 2.818-.916 3.437-2.25.415.163.865.248 1.336.248 2.11 0 3.818-1.79 3.818-4 0-.174-.012-.344-.033-.513 1.158-.687 1.943-1.99 1.943-3.484zm-6.616-3.334l-4.334 6.5c-.145.217-.382.334-.625.334-.143 0-.288-.04-.416-.126l-.115-.094-2.415-2.415c-.293-.293-.293-.768 0-1.06s.768-.294 1.06 0l1.77 1.767 3.825-5.74c.23-.345.696-.436 1.04-.207.346.23.44.696.21 1.04z" />
                </svg>
              </div>
              <p className="text-xs text-muted-foreground">@{handle}</p>
            </div>
            <MoreHorizontal className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
          </div>

          {/* Content */}
          <div className="px-4 py-2">
            <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">{tweet.trim()}</p>
          </div>

          {/* Thread indicator */}
          {tweets.length > 1 && (
            <div className="px-4 pb-1">
              <span className="text-xs text-blue-500 font-medium">{idx + 1}/{tweets.length}</span>
            </div>
          )}

          {/* Time */}
          <div className="px-4 pb-2">
            <span className="text-xs text-muted-foreground">Just now</span>
          </div>

          {/* Metrics */}
          {idx === 0 && data.metrics && (
            <div className="flex items-center gap-4 px-4 py-2 text-xs text-muted-foreground border-t">
              {data.metrics.impressions && <span><strong className="text-foreground">{formatNumber(data.metrics.impressions)}</strong> Views</span>}
              {data.metrics.reposts && <span><strong className="text-foreground">{formatNumber(data.metrics.reposts)}</strong> Reposts</span>}
              {data.metrics.likes && <span><strong className="text-foreground">{formatNumber(data.metrics.likes)}</strong> Likes</span>}
            </div>
          )}

          {/* Action bar */}
          <div className="flex items-center justify-around px-2 py-1 border-t">
            {[
              { icon: MessageCircle, count: data.metrics?.comments },
              { icon: Repeat2, count: data.metrics?.reposts },
              { icon: Heart, count: data.metrics?.likes },
              { icon: Bookmark, count: undefined },
              { icon: Share, count: undefined },
            ].map(({ icon: Icon, count }, i) => (
              <button key={i} className="flex items-center gap-1 p-2 rounded-full text-muted-foreground hover:text-blue-500 hover:bg-blue-500/10 transition-colors">
                <Icon className="h-4 w-4" />
                {count !== undefined && <span className="text-xs">{formatNumber(count)}</span>}
              </button>
            ))}
          </div>

          {/* Platform badge */}
          <div className="px-4 py-1.5 bg-muted/30 border-t">
            <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">X / Twitter Preview</span>
          </div>
        </div>
      ))}
    </div>
  );
});
TwitterPreview.displayName = "TwitterPreview";

// --- Instagram Preview ---
const InstagramPreview = memo(({ raw }: { raw: string }) => {
  const data = useMemo(() => parsePlatformContent(raw), [raw]);
  if (!data) return null;

  const author = data.author || "yourbrand";

  return (
    <div className="my-4 max-w-[520px] rounded-xl border bg-card shadow-sm overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3">
        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-purple-500 via-pink-500 to-orange-400 flex items-center justify-center text-white font-bold text-xs shrink-0 ring-2 ring-pink-500/20">
          {author.charAt(0).toUpperCase()}
        </div>
        <span className="font-semibold text-sm text-foreground">{author}</span>
        <MoreHorizontal className="h-5 w-5 text-muted-foreground ml-auto" />
      </div>

      {/* Image placeholder */}
      <div className="bg-gradient-to-br from-purple-100 via-pink-50 to-orange-50 dark:from-purple-900/30 dark:via-pink-900/20 dark:to-orange-900/20 aspect-square flex items-center justify-center">
        <div className="text-center px-8">
          {data.imageDescription ? (
            <span className="text-sm text-muted-foreground italic">{data.imageDescription}</span>
          ) : (
            <span className="text-sm text-muted-foreground">Image content</span>
          )}
        </div>
      </div>

      {/* Action bar */}
      <div className="flex items-center justify-between px-4 py-2">
        <div className="flex items-center gap-4">
          <Heart className="h-6 w-6 text-foreground" />
          <MessageCircle className="h-6 w-6 text-foreground" />
          <SendIcon className="h-6 w-6 text-foreground" />
        </div>
        <Bookmark className="h-6 w-6 text-foreground" />
      </div>

      {/* Likes */}
      {data.metrics?.likes && (
        <div className="px-4 pb-1">
          <span className="text-sm font-semibold text-foreground">{formatNumber(data.metrics.likes)} likes</span>
        </div>
      )}

      {/* Caption */}
      <div className="px-4 pb-2">
        <p className="text-sm text-foreground">
          <span className="font-semibold">{author}</span>{" "}
          <span className="whitespace-pre-wrap">{data.content}</span>
        </p>
        {data.hashtags && data.hashtags.length > 0 && (
          <p className="mt-1 text-sm text-blue-600 dark:text-blue-400">
            {data.hashtags.map((h) => (h.startsWith("#") ? h : `#${h}`)).join(" ")}
          </p>
        )}
      </div>

      {/* Timestamp */}
      <div className="px-4 pb-3">
        <span className="text-[10px] text-muted-foreground uppercase">Just now</span>
      </div>

      {/* Platform badge */}
      <div className="px-4 py-1.5 bg-muted/30 border-t">
        <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider">Instagram Preview</span>
      </div>
    </div>
  );
});
InstagramPreview.displayName = "InstagramPreview";

export const PLATFORM_RENDERERS: Record<string, React.ComponentType<{ raw: string }>> = {
  "platform-linkedin": LinkedInPreview,
  "platform-twitter": TwitterPreview,
  "platform-x": TwitterPreview,
  "platform-instagram": InstagramPreview,
};
