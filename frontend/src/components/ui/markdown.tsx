/**
 * Markdown-Renderer für Schulungs-Lerninhalte.
 *
 * Standard-Konfiguration: GitHub-Flavored Markdown (Tabellen, Listen,
 * Checkboxen). Sicher: react-markdown rendert AST direkt, kein
 * dangerouslySetInnerHTML — XSS-Schutz inklusive. Eingebettete URLs
 * werden zu safe anchor tags. Roh-HTML im Markdown wird NICHT gerendert.
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
    <div
      className={cn(
        "prose prose-sm max-w-none",
        "prose-headings:font-semibold prose-headings:tracking-tight",
        "prose-h2:mt-4 prose-h2:mb-2 prose-h2:text-base",
        "prose-h3:mt-3 prose-h3:mb-1 prose-h3:text-sm",
        "prose-p:my-2 prose-p:leading-relaxed",
        "prose-ul:my-2 prose-li:my-0.5",
        "prose-strong:font-semibold prose-strong:text-foreground",
        "prose-table:my-3 prose-th:bg-muted prose-th:px-2 prose-th:py-1",
        "prose-td:border prose-td:px-2 prose-td:py-1 prose-th:border",
        "prose-code:bg-muted prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:text-xs",
        className,
      )}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{source}</ReactMarkdown>
    </div>
  );
}
