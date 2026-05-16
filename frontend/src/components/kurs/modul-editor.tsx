/**
 * Modul-Editor (Slice 2a+). Liste der Module eines Kurses, Drag-Reorder,
 * Inline-Anlegen/Editieren. Slice 2a unterstuetzt nur typ=text — andere
 * Typen werden im Picker als „kommt bald" angezeigt.
 */
import { AssetPreview } from "@/components/kurs/asset-preview";
import { AssetUploader } from "@/components/kurs/asset-uploader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Markdown } from "@/components/ui/markdown";
import {
  type KursAsset,
  type KursModul,
  MODUL_TYP_LABEL,
  type ModulTyp,
  useCreateModul,
  useDeleteModul,
  useReorderModule,
  useUpdateModul,
} from "@/lib/api/schulungen";
import {
  DndContext,
  type DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Eye, GripVertical, Pencil, Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

// Schrittweise nach Sub-Slice freischalten. S2a: text. S2b: + pdf. S2c: + bild.
// S2d: + office. S2e: + video_upload + video_youtube.
const SUPPORTED_TYPES: ModulTyp[] = ["text", "pdf", "bild"];

const ASSET_TYPE_CONFIG: Partial<
  Record<ModulTyp, { accept: string; maxBytes: number; hint: string }>
> = {
  pdf: {
    accept: "application/pdf",
    maxBytes: 50 * 1024 * 1024,
    hint: "PDF bis 50 MB. Große Dateien werden automatisch komprimiert.",
  },
  bild: {
    accept: "image/png,image/jpeg",
    maxBytes: 10 * 1024 * 1024,
    hint: "PNG oder JPG bis 10 MB. Werden auf 2048 px / JPEG q=85 komprimiert.",
  },
  office: {
    accept:
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.presentationml.presentation",
    maxBytes: 50 * 1024 * 1024,
    hint: "DOCX oder PPTX bis 50 MB. Werden serverseitig zu PDF konvertiert.",
  },
  video_upload: {
    accept: "video/mp4",
    maxBytes: 500 * 1024 * 1024,
    hint: "MP4 bis 500 MB. Werden auf 1080p / CRF 23 transkodiert.",
  },
};

export function ModulEditor({
  kursId,
  module,
  readonly = false,
}: {
  kursId: number;
  module: KursModul[];
  readonly?: boolean;
}) {
  const [orderedIds, setOrderedIds] = useState<number[]>(() =>
    [...module].sort((a, b) => a.reihenfolge - b.reihenfolge).map((m) => m.id),
  );
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showCreate, setShowCreate] = useState(false);

  // Sync local order when server module list changes (after create/delete)
  useEffect(() => {
    const sorted = [...module]
      .sort((a, b) => a.reihenfolge - b.reihenfolge)
      .map((m) => m.id);
    setOrderedIds(sorted);
  }, [module]);

  const reorder = useReorderModule();
  const del = useDeleteModul();
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const byId = new Map(module.map((m) => [m.id, m]));
  const ordered = orderedIds.map((id) => byId.get(id)).filter(Boolean) as KursModul[];

  const onDragEnd = (e: DragEndEvent) => {
    const { active, over } = e;
    if (!over || active.id === over.id) return;
    const oldIdx = orderedIds.indexOf(Number(active.id));
    const newIdx = orderedIds.indexOf(Number(over.id));
    const next = arrayMove(orderedIds, oldIdx, newIdx);
    setOrderedIds(next);
    reorder.mutate(
      { kurs: kursId, modul_ids: next },
      {
        onError: () => {
          toast.error("Reihenfolge konnte nicht gespeichert werden.");
          setOrderedIds(orderedIds);
        },
      },
    );
  };

  const handleDelete = (id: number, titel: string) => {
    if (!window.confirm(`Modul „${titel}" wirklich löschen?`)) return;
    del.mutate(
      { id, kursId },
      {
        onSuccess: () => toast.success("Modul gelöscht."),
        onError: () => toast.error("Löschen fehlgeschlagen."),
      },
    );
  };

  if (readonly) {
    return (
      <div className="space-y-3">
        {ordered.map((m, idx) => (
          <ModulPreview key={m.id} modul={m} index={idx + 1} />
        ))}
        {ordered.length === 0 && (
          <p className="text-sm text-muted-foreground">Noch keine Module.</p>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragEnd={onDragEnd}
      >
        <SortableContext items={orderedIds} strategy={verticalListSortingStrategy}>
          {ordered.map((m, idx) =>
            editingId === m.id ? (
              <ModulFormCard
                key={m.id}
                kursId={kursId}
                existing={m}
                onClose={() => setEditingId(null)}
              />
            ) : (
              <SortableModulCard
                key={m.id}
                modul={m}
                index={idx + 1}
                onEdit={() => setEditingId(m.id)}
                onDelete={() => handleDelete(m.id, m.titel)}
              />
            ),
          )}
        </SortableContext>
      </DndContext>

      {showCreate ? (
        <ModulFormCard
          kursId={kursId}
          newOrder={ordered.length}
          onClose={() => setShowCreate(false)}
        />
      ) : (
        <Button variant="outline" onClick={() => setShowCreate(true)}>
          <Plus className="mr-1 h-4 w-4" /> Neues Modul
        </Button>
      )}
    </div>
  );
}

function SortableModulCard({
  modul,
  index,
  onEdit,
  onDelete,
}: {
  modul: KursModul;
  index: number;
  onEdit: () => void;
  onDelete: () => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } =
    useSortable({ id: modul.id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };
  return (
    <div
      ref={setNodeRef}
      style={style}
      className="rounded border bg-card p-3 shadow-sm"
    >
      <div className="flex items-start gap-2">
        <button
          type="button"
          className="cursor-grab touch-none p-1 text-muted-foreground hover:text-foreground active:cursor-grabbing"
          aria-label="Verschieben"
          {...attributes}
          {...listeners}
        >
          <GripVertical className="h-4 w-4" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-muted-foreground">
            <span>Modul {index}</span>
            <span className="rounded bg-slate-100 px-1.5 py-0.5 normal-case">
              {MODUL_TYP_LABEL[modul.typ]}
            </span>
          </div>
          <h4 className="mt-1 font-medium">{modul.titel}</h4>
          {modul.typ === "text" && (
            <div className="mt-2 line-clamp-3 text-sm text-muted-foreground">
              <Markdown source={modul.inhalt_md.slice(0, 280)} />
            </div>
          )}
          {modul.typ !== "text" &&
            modul.typ !== "video_youtube" &&
            modul.asset && (
              <div className="mt-2 text-xs text-muted-foreground">
                Asset #{modul.asset} verknüpft.
              </div>
            )}
          {modul.typ === "video_youtube" && modul.youtube_url && (
            <div className="mt-2 line-clamp-1 text-xs text-muted-foreground">
              {modul.youtube_url}
            </div>
          )}
        </div>
        <div className="flex gap-1">
          <Button
            size="icon"
            variant="ghost"
            aria-label="Bearbeiten"
            onClick={onEdit}
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            size="icon"
            variant="ghost"
            aria-label="Löschen"
            onClick={onDelete}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function ModulPreview({ modul, index }: { modul: KursModul; index: number }) {
  return (
    <div className="rounded border bg-muted/30 p-4">
      <div className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">
        Modul {index} · {MODUL_TYP_LABEL[modul.typ]}
      </div>
      <h3 className="mb-2 text-sm font-semibold">{modul.titel}</h3>
      {modul.typ === "text" && <Markdown source={modul.inhalt_md} />}
      {modul.typ === "video_youtube" && modul.youtube_url && (
        <YouTubeEmbed url={modul.youtube_url} />
      )}
      {modul.asset != null &&
        modul.typ !== "text" &&
        modul.typ !== "video_youtube" && <AssetPreview assetId={modul.asset} />}
    </div>
  );
}

function YouTubeEmbed({ url }: { url: string }) {
  const id = extractYouTubeId(url);
  if (!id) return <p className="text-sm text-destructive">Ungültige YouTube-URL.</p>;
  return (
    <div className="aspect-video w-full">
      <iframe
        className="h-full w-full rounded"
        src={`https://www.youtube.com/embed/${id}`}
        title="YouTube"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      />
    </div>
  );
}

function extractYouTubeId(url: string): string | null {
  try {
    const u = new URL(url);
    if (u.hostname.includes("youtu.be")) return u.pathname.slice(1);
    if (u.hostname.includes("youtube.com")) {
      const v = u.searchParams.get("v");
      if (v) return v;
      const parts = u.pathname.split("/");
      const embedIdx = parts.indexOf("embed");
      if (embedIdx >= 0 && parts[embedIdx + 1]) return parts[embedIdx + 1];
    }
  } catch {
    return null;
  }
  return null;
}

function ModulFormCard({
  kursId,
  existing,
  newOrder,
  onClose,
}: {
  kursId: number;
  existing?: KursModul;
  newOrder?: number;
  onClose: () => void;
}) {
  const [typ, setTyp] = useState<ModulTyp>(existing?.typ ?? "text");
  const [titel, setTitel] = useState(existing?.titel ?? "");
  const [inhalt, setInhalt] = useState(existing?.inhalt_md ?? "");
  const [youtubeUrl, setYoutubeUrl] = useState(existing?.youtube_url ?? "");
  const [assetId, setAssetId] = useState<number | null>(existing?.asset ?? null);
  const create = useCreateModul();
  const update = useUpdateModul();

  const handleAssetUploaded = (a: KursAsset) => setAssetId(a.id);

  const save = () => {
    if (!titel.trim()) {
      toast.error("Titel ist Pflicht.");
      return;
    }
    if (typ === "text" && !inhalt.trim()) {
      toast.error("Inhalt ist bei Text-Modulen Pflicht.");
      return;
    }
    if (typ === "video_youtube" && !youtubeUrl.trim()) {
      toast.error("YouTube-URL ist Pflicht.");
      return;
    }
    if (
      typ !== "text" &&
      typ !== "video_youtube" &&
      assetId == null
    ) {
      toast.error("Bitte zuerst eine Datei hochladen.");
      return;
    }
    const payload = {
      kurs: kursId,
      titel: titel.trim(),
      typ,
      inhalt_md: typ === "text" ? inhalt : "",
      youtube_url: typ === "video_youtube" ? youtubeUrl.trim() : "",
      asset:
        typ === "text" || typ === "video_youtube" ? null : assetId,
      reihenfolge: existing?.reihenfolge ?? newOrder ?? 0,
    };
    if (existing) {
      update.mutate(
        { id: existing.id, payload },
        {
          onSuccess: () => {
            toast.success("Modul gespeichert.");
            onClose();
          },
          onError: () => toast.error("Speichern fehlgeschlagen."),
        },
      );
    } else {
      create.mutate(payload, {
        onSuccess: () => {
          toast.success("Modul angelegt.");
          onClose();
        },
        onError: () => toast.error("Anlegen fehlgeschlagen."),
      });
    }
  };

  return (
    <div className="space-y-3 rounded border bg-card p-3 shadow-sm">
      <div>
        <Label>Modul-Typ</Label>
        <div className="mt-1 flex flex-wrap gap-2">
          {(
            Object.entries(MODUL_TYP_LABEL) as [ModulTyp, string][]
          ).map(([value, label]) => {
            const enabled = SUPPORTED_TYPES.includes(value);
            return (
              <button
                key={value}
                type="button"
                onClick={() => enabled && setTyp(value)}
                disabled={!enabled}
                className={
                  typ === value
                    ? "rounded border-2 border-primary bg-primary/5 px-3 py-1 text-sm font-medium"
                    : enabled
                      ? "rounded border px-3 py-1 text-sm hover:bg-slate-50"
                      : "cursor-not-allowed rounded border px-3 py-1 text-sm text-muted-foreground opacity-50"
                }
              >
                {label}
                {!enabled && " — bald"}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <Label htmlFor="modul-titel">Titel *</Label>
        <Input
          id="modul-titel"
          value={titel}
          onChange={(e) => setTitel(e.target.value)}
          placeholder="z.B. Grundbegriffe"
        />
      </div>

      {typ !== "text" && typ !== "video_youtube" && ASSET_TYPE_CONFIG[typ] && (
        <div>
          <Label>Datei *</Label>
          <AssetUploader
            kursId={kursId}
            accept={ASSET_TYPE_CONFIG[typ]!.accept}
            maxBytes={ASSET_TYPE_CONFIG[typ]!.maxBytes}
            currentAssetId={assetId}
            onUploaded={handleAssetUploaded}
            hint={ASSET_TYPE_CONFIG[typ]!.hint}
          />
        </div>
      )}

      {typ === "video_youtube" && (
        <div>
          <Label htmlFor="yt-url">YouTube-URL *</Label>
          <Input
            id="yt-url"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            placeholder="https://www.youtube.com/watch?v=…"
          />
        </div>
      )}

      {typ === "text" && (
        <div>
          <Label htmlFor="modul-inhalt">Inhalt (Markdown) *</Label>
          <div className="mt-1 grid grid-cols-1 gap-2 md:grid-cols-2">
            <textarea
              id="modul-inhalt"
              value={inhalt}
              onChange={(e) => setInhalt(e.target.value)}
              rows={14}
              placeholder="## Lernziel&#10;&#10;Was die Teilnehmer:in nach diesem Modul wissen sollte.&#10;&#10;## Inhalte&#10;&#10;- Punkt 1&#10;- Punkt 2"
              className="w-full rounded border border-input bg-background p-2 font-mono text-sm"
            />
            <div className="rounded border border-input bg-muted/30 p-3 text-sm">
              <div className="mb-2 flex items-center gap-1 text-xs uppercase tracking-wide text-muted-foreground">
                <Eye className="h-3 w-3" /> Vorschau
              </div>
              {inhalt.trim() ? (
                <Markdown source={inhalt} />
              ) : (
                <p className="italic text-muted-foreground">Noch nichts.</p>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={onClose}>
          Abbrechen
        </Button>
        <Button onClick={save} disabled={create.isPending || update.isPending}>
          {existing ? "Speichern" : "Anlegen"}
        </Button>
      </div>
    </div>
  );
}
