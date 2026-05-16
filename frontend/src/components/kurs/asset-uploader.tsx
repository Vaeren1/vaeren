/**
 * Asset-Uploader fuer Kurs-Module (Slice 2b/c/e).
 *
 * Bietet drag-drop + file-picker, zeigt Upload-Progress optimistisch,
 * pollt nach Upload den Compression-Status. Aufrufer entscheidet ueber
 * `accept` welche MIME-Types erlaubt sind.
 */
import { type KursAsset, uploadAsset, useKursAsset } from "@/lib/api/schulungen";
import { Loader2, Upload } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export function AssetUploader({
  kursId,
  accept,
  maxBytes,
  currentAssetId,
  onUploaded,
  hint,
}: {
  kursId: number;
  accept: string; // z.B. "application/pdf" oder "image/*"
  maxBytes: number;
  currentAssetId: number | null;
  onUploaded: (asset: KursAsset) => void;
  hint?: string;
}) {
  const [uploading, setUploading] = useState(false);
  const asset = useKursAsset(currentAssetId);

  const handleFile = async (file: File) => {
    if (file.size > maxBytes) {
      toast.error(
        `Datei zu groß (${(file.size / 1024 / 1024).toFixed(1)} MB). Limit: ${(maxBytes / 1024 / 1024).toFixed(0)} MB.`,
      );
      return;
    }
    setUploading(true);
    try {
      const a = await uploadAsset(kursId, file);
      toast.success("Hochgeladen — Komprimierung läuft im Hintergrund.");
      onUploaded(a);
    } catch (e) {
      toast.error(`Upload fehlgeschlagen: ${(e as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-2">
      <label className="block">
        <div className="flex cursor-pointer items-center justify-center gap-2 rounded border-2 border-dashed border-input p-6 text-sm text-muted-foreground hover:bg-muted/30">
          {uploading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" /> Lade hoch…
            </>
          ) : (
            <>
              <Upload className="h-4 w-4" />
              {currentAssetId ? "Andere Datei wählen" : "Datei wählen oder hier ablegen"}
            </>
          )}
        </div>
        <input
          type="file"
          accept={accept}
          className="hidden"
          disabled={uploading}
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handleFile(f);
            e.target.value = ""; // re-upload same file possible
          }}
        />
      </label>
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}

      {currentAssetId && asset.data && (
        <AssetStatusBadge asset={asset.data} />
      )}
    </div>
  );
}

function AssetStatusBadge({ asset }: { asset: KursAsset }) {
  const orig = (asset.original_size_bytes / 1024 / 1024).toFixed(2);
  const comp = asset.compressed_size_bytes
    ? (asset.compressed_size_bytes / 1024 / 1024).toFixed(2)
    : null;
  const savings = asset.compressed_size_bytes
    ? (1 - asset.compressed_size_bytes / asset.original_size_bytes) * 100
    : 0;

  let statusLabel = "";
  let statusColor = "bg-slate-100 text-slate-700";
  switch (asset.compression_status) {
    case "pending":
      statusLabel = "Komprimierung läuft…";
      statusColor = "bg-amber-50 text-amber-900";
      break;
    case "done":
      statusLabel = `Komprimiert (–${savings.toFixed(0)} %)`;
      statusColor = "bg-emerald-50 text-emerald-900";
      break;
    case "skipped":
      statusLabel = "Bereits klein genug — keine Komprimierung";
      break;
    case "not_needed":
      statusLabel = "—";
      break;
    case "failed":
      statusLabel = "Komprimierung fehlgeschlagen (Original bleibt verfügbar)";
      statusColor = "bg-red-50 text-red-900";
      break;
  }

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`rounded px-2 py-0.5 ${statusColor}`}>{statusLabel}</span>
      <span className="text-muted-foreground">
        {orig} MB
        {comp && asset.compression_status === "done" ? ` → ${comp} MB` : ""}
      </span>
      {asset.download_url && (
        <a
          href={asset.download_url}
          target="_blank"
          rel="noopener noreferrer"
          className="underline"
        >
          Download
        </a>
      )}
    </div>
  );
}
