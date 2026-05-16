import { useState } from "react";

interface Props {
  zitation: string;
}

export default function ZitationsBox({ zitation }: Props) {
  const [copied, setCopied] = useState(false);

  function copy() {
    navigator.clipboard.writeText(zitation).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  return (
    <aside className="mt-10 p-5 border border-line rounded-lg bg-paper-soft/40 no-print">
      <div className="text-xs uppercase tracking-widest text-ink-muted font-medium mb-2">
        Zitieren
      </div>
      <p className="text-sm text-ink-soft mb-3 leading-relaxed italic">{zitation}</p>
      <button
        onClick={copy}
        className="text-xs px-3 py-1.5 border border-line bg-paper rounded hover:border-brand hover:text-brand"
        type="button"
      >
        {copied ? "Kopiert" : "Zitation kopieren"}
      </button>
    </aside>
  );
}
