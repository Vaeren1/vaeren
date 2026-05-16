/**
 * Markdown-Renderer für Schulungs-Lerninhalte.
 *
 * Per-Element-Klassen statt @tailwindcss/typography — letzteres ist nicht
 * installiert. Stil orientiert an der Pilot-HTML-Vorschau (Brandschutz #4):
 * deutliche H2-Akzentfarbe, Zebra-Tabellen, Bullets in Primärfarbe, klare
 * Absatzhierarchie.
 *
 * Sicherheit: react-markdown rendert AST direkt, kein dangerouslySetInnerHTML.
 * Roh-HTML im Markdown wird NICHT gerendert.
 */
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownProps {
  source: string;
  className?: string;
}

export function Markdown({ source, className }: MarkdownProps) {
  return (
    <div className={cn("text-foreground text-[15px]", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node: _n, ...props }) => (
            <h1
              className="mt-8 mb-4 pb-2 text-2xl font-bold tracking-tight border-b-2 border-primary first:mt-0"
              {...props}
            />
          ),
          h2: ({ node: _n, ...props }) => (
            <h2
              className="mt-8 mb-3 text-lg font-semibold tracking-tight text-primary first:mt-0"
              {...props}
            />
          ),
          h3: ({ node: _n, ...props }) => (
            <h3
              className="mt-5 mb-2 text-base font-semibold tracking-tight"
              {...props}
            />
          ),
          p: ({ node: _n, ...props }) => (
            <p className="my-3 leading-relaxed" {...props} />
          ),
          strong: ({ node: _n, ...props }) => (
            <strong className="font-semibold text-foreground" {...props} />
          ),
          em: ({ node: _n, ...props }) => (
            <em className="italic text-muted-foreground" {...props} />
          ),
          ul: ({ node: _n, ...props }) => (
            <ul
              className="my-3 pl-6 space-y-1 list-disc marker:text-primary"
              {...props}
            />
          ),
          ol: ({ node: _n, ...props }) => (
            <ol
              className="my-3 pl-6 space-y-1 list-decimal marker:text-primary marker:font-semibold"
              {...props}
            />
          ),
          li: ({ node: _n, ...props }) => (
            <li className="leading-relaxed pl-1" {...props} />
          ),
          table: ({ node: _n, ...props }) => (
            <div className="my-4 overflow-x-auto">
              <table
                className="w-full text-sm border-collapse border border-border"
                {...props}
              />
            </div>
          ),
          thead: ({ node: _n, ...props }) => (
            <thead className="bg-muted" {...props} />
          ),
          th: ({ node: _n, ...props }) => (
            <th
              className="text-left font-semibold px-3 py-2 border border-border border-b-2 border-b-primary"
              {...props}
            />
          ),
          td: ({ node: _n, ...props }) => (
            <td
              className="px-3 py-2 border border-border align-top"
              {...props}
            />
          ),
          tr: ({ node: _n, ...props }) => (
            <tr className="even:bg-muted/30" {...props} />
          ),
          code: ({ node: _n, ...props }) => (
            <code
              className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono"
              {...props}
            />
          ),
          hr: () => <hr className="my-6 border-border" />,
          a: ({ node: _n, ...props }) => (
            <a
              className="text-primary underline underline-offset-2 hover:no-underline"
              {...props}
            />
          ),
        }}
      >
        {source}
      </ReactMarkdown>
    </div>
  );
}
