/**
 * Asset-Preview pro Modul-Typ. Wird im Editor und im Player verwendet.
 *
 * S2b: PDF via iframe (Browser-native, kein react-pdf-Worker noetig)
 * S2c: Bild via <img>
 * S2d: Office → konvertierte PDF (gleich wie S2b)
 * S2e: Video-Upload via <video controls>, YouTube via iframe-Embed
 */
import { useKursAsset } from "@/lib/api/schulungen";
import { Loader2 } from "lucide-react";

export function AssetPreview({ assetId }: { assetId: number }) {
  const { data: asset, isLoading } = useKursAsset(assetId);

  if (isLoading || !asset) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" /> Lade Asset…
      </div>
    );
  }

  const url = asset.download_url;
  if (!url) {
    return <p className="text-sm text-destructive">Asset nicht abrufbar.</p>;
  }

  const mime = asset.original_mime;

  // PDF (auch konvertierte Office)
  if (
    mime === "application/pdf" ||
    asset.konvertierung_status === "done"
  ) {
    return (
      <iframe
        src={url}
        title="PDF-Vorschau"
        className="h-[600px] w-full rounded border"
      />
    );
  }

  if (mime === "image/png" || mime === "image/jpeg") {
    return (
      <img
        src={url}
        alt="Modul-Bild"
        className="max-h-[600px] w-auto rounded border"
      />
    );
  }

  if (mime === "video/mp4") {
    return (
      <video
        src={url}
        controls
        className="w-full rounded border"
        style={{ maxHeight: 600 }}
      >
        <track kind="captions" />
      </video>
    );
  }

  // Office (konvertierung_status != done): zeigen wir Download-Hinweis
  if (
    mime ===
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
    mime ===
      "application/vnd.openxmlformats-officedocument.presentationml.presentation"
  ) {
    const label =
      asset.konvertierung_status === "pending"
        ? "Konvertierung zu PDF läuft…"
        : asset.konvertierung_status === "failed"
          ? "Konvertierung fehlgeschlagen — Download-Original verfügbar:"
          : "Original-Office-Datei:";
    return (
      <div className="rounded border bg-muted/30 p-4 text-sm">
        <p>{label}</p>
        <a
          href={url}
          className="text-primary underline"
          target="_blank"
          rel="noopener noreferrer"
        >
          Download
        </a>
      </div>
    );
  }

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="text-sm underline"
    >
      Download ({mime})
    </a>
  );
}
