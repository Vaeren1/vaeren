/**
 * Redaktions-Dashboard für Vaeren-Superuser.
 *
 * Listet alle NewsPosts (alle Status), zeigt Verifier-Issues + Notbremse,
 * erlaubt publish/unpublish/pin/edit-Aktionen.
 */

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  GEO_LABEL,
  KATEGORIE_LABEL,
  type NewsPostAdmin,
  type NewsPostKategorie,
  type NewsPostStatus,
  RELEVANZ_LABEL,
  STATUS_COLOR,
  STATUS_LABEL,
  TYPE_LABEL,
  useNewsPost,
  useNewsPostList,
  usePatchNewsPost,
  usePublishNewsPost,
  useRedaktionRuns,
  useTogglePinNewsPost,
  useUnpublishNewsPost,
} from "@/lib/api/redaktion";
import { cn } from "@/lib/utils";
import {
  AlertTriangle,
  ExternalLink,
  Pin,
  PinOff,
  ScrollText,
  Search,
} from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

const STATUS_FILTERS: Array<{ v: NewsPostStatus | ""; label: string }> = [
  { v: "", label: "Alle" },
  { v: "published", label: "Live" },
  { v: "hold", label: "Hold" },
  { v: "pending_verify", label: "In Verifikation" },
  { v: "unpublished", label: "Zurückgezogen" },
];

const KATEGORIE_FILTERS: Array<{ v: NewsPostKategorie | ""; label: string }> = [
  { v: "", label: "Alle Kategorien" },
  ...(Object.entries(KATEGORIE_LABEL) as Array<[NewsPostKategorie, string]>).map(
    ([v, label]) => ({ v, label }),
  ),
];

export function RedaktionPage() {
  const [status, setStatus] = useState<NewsPostStatus | "">("");
  const [kategorie, setKategorie] = useState<NewsPostKategorie | "">("");
  const [search, setSearch] = useState("");
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);

  const { data: posts, isLoading } = useNewsPostList({
    status: status || undefined,
    kategorie: kategorie || undefined,
    search: search || undefined,
  });

  const { data: runs } = useRedaktionRuns();

  return (
    <div className="flex flex-col gap-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl tracking-tight">Redaktion</h1>
          <p className="text-sm text-muted-foreground mt-1">
            News-Posts pflegen, Verifier-Halluzinationen prüfen,
            zurückziehen oder anpinnen.
          </p>
        </div>
        {runs && runs.length > 0 && (
          <div className="text-right text-xs text-muted-foreground">
            <div>Letzter Pipeline-Lauf:</div>
            <div className="font-medium text-foreground">
              {new Date(runs[0].started_at).toLocaleString("de-DE")}
            </div>
            <div>
              {runs[0].published} published · {runs[0].held} hold ·{" "}
              {runs[0].curator_items_out} curated
            </div>
          </div>
        )}
      </header>

      {/* Filter-Leiste */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-medium">Filter</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-3">
          <div className="flex flex-wrap gap-2">
            {STATUS_FILTERS.map((s) => (
              <Button
                key={s.v}
                size="sm"
                variant={status === s.v ? "default" : "outline"}
                onClick={() => setStatus(s.v)}
              >
                {s.label}
              </Button>
            ))}
          </div>
          <div className="ml-auto flex items-center gap-2">
            <select
              value={kategorie}
              onChange={(e) => setKategorie(e.target.value as NewsPostKategorie | "")}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              {KATEGORIE_FILTERS.map((k) => (
                <option key={k.v} value={k.v}>
                  {k.label}
                </option>
              ))}
            </select>
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Volltextsuche…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 h-9 w-64"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Hauptliste */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {isLoading ? "lädt…" : `${posts?.length ?? 0} Beiträge`}
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {posts && posts.length === 0 && (
            <div className="text-center py-12 text-muted-foreground text-sm">
              Keine Beiträge zu diesen Filtern.
            </div>
          )}
          <ul className="divide-y">
            {posts?.map((p) => (
              <PostRow
                key={p.id}
                post={p}
                onSelect={() => setSelectedSlug(p.slug)}
                isSelected={selectedSlug === p.slug}
              />
            ))}
          </ul>
        </CardContent>
      </Card>

      {/* Detail-Panel */}
      {selectedSlug && (
        <PostDetail
          slug={selectedSlug}
          onClose={() => setSelectedSlug(null)}
        />
      )}
    </div>
  );
}

// --- Row in der Liste ------------------------------------------------------

function PostRow({
  post,
  onSelect,
  isSelected,
}: {
  post: NewsPostAdmin;
  onSelect: () => void;
  isSelected: boolean;
}) {
  const publishMut = usePublishNewsPost();
  const unpublishMut = useUnpublishNewsPost();
  const pinMut = useTogglePinNewsPost();

  const handlePublish = () =>
    publishMut.mutate(post.slug, {
      onSuccess: () => toast.success(`„${post.titel}" ist live.`),
      onError: () => toast.error("Publish fehlgeschlagen."),
    });
  const handleUnpublish = () =>
    unpublishMut.mutate(post.slug, {
      onSuccess: () => toast.success(`„${post.titel}" zurückgezogen.`),
      onError: () => toast.error("Unpublish fehlgeschlagen."),
    });
  const handlePin = () =>
    pinMut.mutate(post.slug, {
      onSuccess: (data) =>
        toast.success(data.pinned ? "Angepinnt." : "Pin entfernt."),
    });

  return (
    <li
      className={cn(
        "p-4 flex items-start gap-4 hover:bg-muted/50 cursor-pointer",
        isSelected && "bg-muted/40",
      )}
      onClick={onSelect}
    >
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2 mb-1">
          <span
            className={cn(
              "px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wide font-medium",
              STATUS_COLOR[post.status],
            )}
          >
            {STATUS_LABEL[post.status]}
          </span>
          <span className="px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wide bg-muted text-muted-foreground">
            {KATEGORIE_LABEL[post.kategorie]}
          </span>
          <span className="text-[10px] uppercase tracking-wide text-muted-foreground">
            {GEO_LABEL[post.geo]} · {TYPE_LABEL[post.type]} ·{" "}
            {RELEVANZ_LABEL[post.relevanz]}
          </span>
          {post.pinned && (
            <span className="text-[10px] uppercase tracking-wide text-amber-700 font-medium">
              <Pin className="inline h-3 w-3 mr-0.5" />
              angepinnt
            </span>
          )}
          {post.status === "hold" && (
            <span className="text-[10px] uppercase tracking-wide text-amber-700 font-medium">
              <AlertTriangle className="inline h-3 w-3 mr-0.5" />
              Verifier: {post.verifier_issues?.length ?? 0} Issue(s)
              {post.verifier_confidence != null &&
                ` · conf ${post.verifier_confidence.toFixed(2)}`}
            </span>
          )}
        </div>
        <h3 className="font-serif text-base font-medium leading-tight">
          {post.titel}
        </h3>
        <p className="text-sm text-muted-foreground line-clamp-1 mt-0.5">
          {post.lead}
        </p>
        <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
          {post.candidate_quelle && (
            <span>Quelle: {post.candidate_quelle}</span>
          )}
          {post.published_at && (
            <span>
              Live seit {new Date(post.published_at).toLocaleDateString("de-DE")}
            </span>
          )}
          {post.expires_at && (
            <span>
              läuft ab {new Date(post.expires_at).toLocaleDateString("de-DE")}
            </span>
          )}
        </div>
      </div>
      <div
        className="flex flex-col gap-1.5 shrink-0"
        onClick={(e) => e.stopPropagation()}
      >
        {post.status !== "published" && (
          <Button
            size="sm"
            variant="default"
            onClick={handlePublish}
            disabled={publishMut.isPending}
          >
            Publish
          </Button>
        )}
        {post.status === "published" && (
          <Button
            size="sm"
            variant="outline"
            onClick={handleUnpublish}
            disabled={unpublishMut.isPending}
          >
            Zurückziehen
          </Button>
        )}
        <Button
          size="sm"
          variant="ghost"
          onClick={handlePin}
          disabled={pinMut.isPending}
          title={post.pinned ? "Pin entfernen" : "Anpinnen"}
        >
          {post.pinned ? (
            <PinOff className="h-4 w-4" />
          ) : (
            <Pin className="h-4 w-4" />
          )}
        </Button>
      </div>
    </li>
  );
}

// --- Detail-Panel ----------------------------------------------------------

function PostDetail({
  slug,
  onClose,
}: {
  slug: string;
  onClose: () => void;
}) {
  const { data: post, isLoading } = useNewsPost(slug);
  const patchMut = usePatchNewsPost();
  const [editTitel, setEditTitel] = useState<string | null>(null);
  const [editLead, setEditLead] = useState<string | null>(null);
  const [editBody, setEditBody] = useState<string | null>(null);

  if (isLoading || !post) {
    return (
      <Card>
        <CardContent className="p-6 text-sm text-muted-foreground">
          Lade…
        </CardContent>
      </Card>
    );
  }

  const titel = editTitel ?? post.titel;
  const lead = editLead ?? post.lead;
  const body = editBody ?? post.body_html;
  const hasEdits =
    editTitel !== null || editLead !== null || editBody !== null;

  const handleSave = () => {
    const patch: Record<string, string> = {};
    if (editTitel !== null) patch.titel = editTitel;
    if (editLead !== null) patch.lead = editLead;
    if (editBody !== null) patch.body_html = editBody;
    patchMut.mutate(
      { slug, patch },
      {
        onSuccess: () => {
          setEditTitel(null);
          setEditLead(null);
          setEditBody(null);
          toast.success("Änderungen gespeichert.");
        },
        onError: () => toast.error("Speichern fehlgeschlagen."),
      },
    );
  };

  const handleDiscard = () => {
    setEditTitel(null);
    setEditLead(null);
    setEditBody(null);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-2">
        <div>
          <CardTitle className="font-serif text-lg">
            Beitrag bearbeiten
          </CardTitle>
          <CardDescription>
            Status:{" "}
            <span className="font-medium text-foreground">
              {STATUS_LABEL[post.status]}
            </span>
            {post.verifier_confidence != null && (
              <>
                {" "}· Verifier-Confidence{" "}
                <span className="font-mono">
                  {post.verifier_confidence.toFixed(2)}
                </span>
              </>
            )}
          </CardDescription>
        </div>
        <Button variant="ghost" size="sm" onClick={onClose}>
          schließen
        </Button>
      </CardHeader>
      <CardContent className="space-y-5">
        {post.verifier_issues && post.verifier_issues.length > 0 && (
          <div className="p-4 rounded-md bg-amber-50 border border-amber-200">
            <div className="flex items-center gap-2 text-amber-900 font-medium mb-2">
              <AlertTriangle className="h-4 w-4" />
              Verifier-Befunde
            </div>
            <ul className="text-sm text-amber-900 space-y-1.5">
              {post.verifier_issues.map((i, idx) => (
                <li key={idx} className="flex gap-2">
                  <span>•</span>
                  <span>{i}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div>
          <Label htmlFor="redaktion-titel" className="text-xs uppercase tracking-wide">
            Titel
          </Label>
          <Input
            id="redaktion-titel"
            value={titel}
            onChange={(e) => setEditTitel(e.target.value)}
            className="mt-1"
          />
        </div>

        <div>
          <Label htmlFor="redaktion-lead" className="text-xs uppercase tracking-wide">
            Lead
          </Label>
          <textarea
            id="redaktion-lead"
            value={lead}
            onChange={(e) => setEditLead(e.target.value)}
            rows={3}
            className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
        </div>

        <div>
          <Label htmlFor="redaktion-body" className="text-xs uppercase tracking-wide">
            Body (HTML)
          </Label>
          <textarea
            id="redaktion-body"
            value={body}
            onChange={(e) => setEditBody(e.target.value)}
            rows={12}
            className="mt-1 w-full font-mono text-xs rounded-md border border-input bg-background px-3 py-2"
          />
        </div>

        {post.source_links && post.source_links.length > 0 && (
          <div>
            <Label className="text-xs uppercase tracking-wide">Quellen</Label>
            <ul className="mt-1 space-y-1 text-sm">
              {post.source_links.map((s, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <ExternalLink className="h-3 w-3 text-muted-foreground" />
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline truncate"
                  >
                    {s.titel || s.url}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="flex items-center gap-2 pt-2 border-t">
          <a
            href={`https://vaeren.de/news/${post.slug}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline inline-flex items-center gap-1"
          >
            <ScrollText className="h-3.5 w-3.5" /> Live-Vorschau
          </a>
          <span className="text-xs text-muted-foreground ml-2">
            Slug: <span className="font-mono">{post.slug}</span>
          </span>
          <div className="ml-auto flex gap-2">
            {hasEdits && (
              <Button variant="outline" size="sm" onClick={handleDiscard}>
                Verwerfen
              </Button>
            )}
            <Button
              size="sm"
              onClick={handleSave}
              disabled={!hasEdits || patchMut.isPending}
            >
              Speichern
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
