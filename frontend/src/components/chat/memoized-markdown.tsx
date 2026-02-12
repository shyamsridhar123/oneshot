import { marked } from "marked";
import { memo, useMemo, type ComponentType, type ReactNode, type HTMLAttributes, type ClassAttributes } from "react";
import ReactMarkdown, { type ExtraProps } from "react-markdown";
import {
  CHART_RENDERERS,
  PLATFORM_RENDERERS,
  METRIC_RENDERERS,
  CALLOUT_RENDERERS,
  COMPARISON_RENDERERS,
  CodeBlock,
} from "./rich-content";

// Merge all special code block renderers into a single lookup
const RICH_RENDERERS: Record<string, ComponentType<{ raw: string }>> = {
  ...CHART_RENDERERS,
  ...PLATFORM_RENDERERS,
  ...METRIC_RENDERERS,
  ...CALLOUT_RENDERERS,
  ...COMPARISON_RENDERERS,
};

type CodeProps = ClassAttributes<HTMLElement> & HTMLAttributes<HTMLElement> & ExtraProps;

/**
 * Custom `code` renderer for ReactMarkdown.
 * Detects fenced code blocks with a language tag like `chart-bar`, `platform-linkedin`, etc.
 * and routes them to the matching rich component. Regular code gets syntax highlighting.
 */
function CustomCode({ className, children, ...rest }: CodeProps) {
  const match = /language-(\S+)/.exec(className || "");
  const lang = match ? match[1] : undefined;
  const text = String(children).replace(/\n$/, "");

  // Inline code (no language class, short text)
  if (!lang && !className) {
    return (
      <code
        className="rounded bg-muted px-1.5 py-0.5 text-[13px] font-mono text-foreground"
        {...rest}
      >
        {children}
      </code>
    );
  }

  // Check if this is a rich content block
  if (lang) {
    const Renderer = RICH_RENDERERS[lang];
    if (Renderer) {
      return <Renderer raw={text} />;
    }
  }

  // Regular code block with syntax highlighting
  return <CodeBlock language={lang}>{text}</CodeBlock>;
}

/**
 * Custom styled table components for Tailwind-styled markdown tables
 */
function StyledTable({ children }: { children?: ReactNode }) {
  return (
    <div className="my-3 overflow-x-auto rounded-lg border">
      <table className="w-full text-sm">{children}</table>
    </div>
  );
}

function StyledThead({ children }: { children?: ReactNode }) {
  return <thead className="bg-muted/50 border-b">{children}</thead>;
}

function StyledTh({ children }: { children?: ReactNode }) {
  return (
    <th className="px-4 py-2 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
      {children}
    </th>
  );
}

function StyledTd({ children }: { children?: ReactNode }) {
  return (
    <td className="px-4 py-2 text-sm text-foreground border-t">{children}</td>
  );
}

function StyledTr({ children }: { children?: ReactNode }) {
  return <tr className="hover:bg-muted/30 transition-colors">{children}</tr>;
}

/**
 * Custom link renderer to open external links in new tab
 */
function StyledLink({
  href,
  children,
}: {
  href?: string;
  children?: ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-primary underline underline-offset-2 hover:text-primary/80 transition-colors"
    >
      {children}
    </a>
  );
}

/**
 * Custom blockquote with left-border accent
 */
function StyledBlockquote({ children }: { children?: ReactNode }) {
  return (
    <blockquote className="my-3 border-l-4 border-primary/30 pl-4 italic text-muted-foreground">
      {children}
    </blockquote>
  );
}

// ReactMarkdown custom component overrides
const markdownComponents = {
  code: CustomCode,
  table: StyledTable,
  thead: StyledThead,
  th: StyledTh,
  td: StyledTd,
  tr: StyledTr,
  a: StyledLink,
  blockquote: StyledBlockquote,
};

function parseMarkdownIntoBlocks(markdown: string): string[] {
  const tokens = marked.lexer(markdown);
  return tokens.map((token) => token.raw);
}

const MemoizedMarkdownBlock = memo(
  ({ content }: { content: string }) => {
    return (
      <ReactMarkdown components={markdownComponents}>{content}</ReactMarkdown>
    );
  },
  (prevProps, nextProps) => prevProps.content === nextProps.content
);

MemoizedMarkdownBlock.displayName = "MemoizedMarkdownBlock";

export const MemoizedMarkdown = memo(
  ({ content, id }: { content: string; id: string }) => {
    const blocks = useMemo(() => parseMarkdownIntoBlocks(content), [content]);

    return blocks.map((block, index) => (
      <MemoizedMarkdownBlock content={block} key={`${id}-block_${index}`} />
    ));
  }
);

MemoizedMarkdown.displayName = "MemoizedMarkdown";
