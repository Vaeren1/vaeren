/**
 * OEM-Fragebogen — Upload (Feature 4, G1).
 *
 * Drag-&-Drop ODER Datei-Picker → multipart-Upload via `fragebogen.upload`
 * → Backend erkennt Format/Tier + extrahiert Fragen → Weiterleitung in den
 * seiten-basierten Review.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { fragebogen } from "@/lib/api/fragebogen";
import { cn } from "@/lib/utils";
import { useMutation } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

export function FragebogenUploadPage() {
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement>(null);
  const [datei, setDatei] = useState<File | null>(null);
  const [quelleOem, setQuelleOem] = useState("");
  const [dragOver, setDragOver] = useState(false);

  const mutation = useMutation({
    mutationFn: () => {
      if (!datei) throw new Error("Keine Datei gewählt.");
      return fragebogen.upload(datei, quelleOem);
    },
    onSuccess: (fb) => {
      navigate(`/fragebogen/${fb.id}/review`);
    },
  });

  function onFiles(files: FileList | null) {
    if (files && files.length > 0) {
      setDatei(files[0]);
    }
  }

  return (
    <Card className="max-w-2xl">
      <CardHeader>
        <CardTitle>Fragebogen hochladen</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Unterstützt: Excel (.xlsx), ausfüllbares PDF, Word (.docx) sowie
          unstrukturierte PDFs. Vaeren erkennt das Format automatisch.
        </p>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Drop-Zone + Datei-Picker */}
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            onFiles(e.dataTransfer.files);
          }}
          className={cn(
            "flex w-full flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-10 text-center transition-colors",
            dragOver
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/30 hover:border-muted-foreground/50",
          )}
        >
          <span className="text-sm font-medium">
            {datei
              ? datei.name
              : "Datei hierher ziehen oder klicken zum Auswählen"}
          </span>
          {datei && (
            <span className="text-xs text-muted-foreground">
              {(datei.size / 1024).toFixed(0)} KB
            </span>
          )}
          {!datei && (
            <span className="text-xs text-muted-foreground">
              .xlsx · .pdf · .docx
            </span>
          )}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.pdf,.docx"
          className="hidden"
          onChange={(e) => onFiles(e.target.files)}
        />

        <div className="space-y-1.5">
          <Label htmlFor="quelle-oem">OEM / Auftraggeber (optional)</Label>
          <Input
            id="quelle-oem"
            placeholder="z. B. Volkswagen AG"
            value={quelleOem}
            onChange={(e) => setQuelleOem(e.target.value)}
          />
        </div>

        {mutation.isError && (
          <p className="text-sm text-destructive">
            Upload fehlgeschlagen: {(mutation.error as Error).message}
          </p>
        )}

        <div className="flex justify-end gap-2">
          <Button
            variant="outline"
            type="button"
            onClick={() => navigate("/fragebogen")}
          >
            Abbrechen
          </Button>
          <Button
            type="button"
            disabled={!datei || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {mutation.isPending ? "Lade hoch …" : "Hochladen & analysieren"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
