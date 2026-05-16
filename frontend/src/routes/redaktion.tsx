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
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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
  CheckCircle2,
  ExternalLink,
  Gauge,
  Pin,
  PinOff,
  ScrollText,
  Search,
  Sparkles,
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

      {/* Detail-Modal */}
      <Dialog
        open={!!selectedSlug}
        onOpenChange={(open) => !open && setSelectedSlug(null)}
      >
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          {selectedSlug && (
            <PostDetail
              slug={selectedSlug}
              onClose={() => setSelectedSlug(null)}
            />
          )}
        </DialogContent>
      </Dialog>
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
          {post.verifier_confidence != null && (
            <ConfidenceBadge
              confidence={post.verifier_confidence}
              issuesCount={post.verifier_issues?.length ?? 0}
              status={post.status}
            />
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
          {post.days_since_published != null && (
            <span>Live seit {post.days_since_published} Tagen</span>
          )}
          {post.days_until_expiry != null && post.status === "published" && (
            <span
              className={cn(
                post.days_until_expiry <= 7 && "text-amber-700 font-medium",
              )}
            >
              {post.days_until_expiry > 0
                ? `läuft in ${post.days_until_expiry} Tagen ab`
                : "abgelaufen"}
            </span>
          )}
          {post.lifetime_days != null && (
            <span>Standzeit: {post.lifetime_days} Tage</span>
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

  const [editMode, setEditMode] = useState(false);

  if (isLoading || !post) {
    return (
      <div className="p-6 text-sm text-muted-foreground">Lade…</div>
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
    <div className="space-y-5">
      <DialogHeader>
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <DialogTitle className="font-serif text-xl leading-snug">
              {titel}
            </DialogTitle>
            <DialogDescription className="mt-1">
              <span
                className={cn(
                  "inline-block px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wide font-medium mr-2",
                  STATUS_COLOR[post.status],
                )}
              >
                {STATUS_LABEL[post.status]}
              </span>
              {KATEGORIE_LABEL[post.kategorie]} · {GEO_LABEL[post.geo]} ·{" "}
              {TYPE_LABEL[post.type]} · {RELEVANZ_LABEL[post.relevanz]}
            </DialogDescription>
          </div>
          <Button
            variant={editMode ? "default" : "outline"}
            size="sm"
            onClick={() => setEditMode((m) => !m)}
          >
            {editMode ? "Vorschau" : "Bearbeiten"}
          </Button>
        </div>
      </DialogHeader>

      {/* Pipeline-Analyse: alle Daten der LLM-Stufen + Crawler */}
      <PipelineAnalyse post={post} />

      {post.verifier_issues && post.verifier_issues.length > 0 && (
        <div className="p-4 rounded-md bg-amber-50 border border-amber-200">
          <div className="flex items-center gap-2 text-amber-900 font-medium mb-2">
            <AlertTriangle className="h-4 w-4" />
            Verifier-Befunde ({post.verifier_issues.length})
          </div>
          <ul className="text-sm text-amber-900 space-y-1.5">
            {post.verifier_issues.map((i, idx) => (
              <li key={idx} className="flex gap-2">
                <span className="text-amber-700 font-mono mt-0.5">{idx + 1}.</span>
                <span>{i}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Editier- vs. Vorschau-Modus */}
      {editMode ? (
        <div className="space-y-4">
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
              rows={16}
              className="mt-1 w-full font-mono text-xs rounded-md border border-input bg-background px-3 py-2"
            />
          </div>
        </div>
      ) : (
        <article className="space-y-4 border-l-4 border-slate-200 pl-5 py-2">
          <div className="text-[10px] uppercase tracking-widest text-muted-foreground font-medium">
            Veröffentlichter Beitrag
          </div>
          <p className="font-serif text-lg leading-relaxed text-slate-800">
            {lead}
          </p>
          <div
            className="prose prose-sm prose-slate max-w-none [&_p]:my-3 [&_a]:text-primary [&_a]:underline"
            dangerouslySetInnerHTML={{ __html: body }}
          />
        </article>
      )}

      {post.candidate_titel && (
        <div className="p-4 rounded-md bg-slate-50 border border-slate-200">
          <div className="text-xs uppercase tracking-widest text-slate-700 font-medium mb-2">
            Roh-Quelle (vor LLM-Bearbeitung)
          </div>
          <div className="text-sm font-medium text-slate-900 mb-1">
            {post.candidate_titel}
          </div>
          {post.candidate_excerpt && (
            <p className="text-sm text-slate-600 leading-relaxed line-clamp-6">
              {post.candidate_excerpt}
            </p>
          )}
          {post.candidate_quell_url && (
            <a
              href={post.candidate_quell_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-primary hover:underline mt-2"
            >
              <ExternalLink className="h-3 w-3" />
              Original im neuen Tab öffnen
            </a>
          )}
        </div>
      )}

      {post.curator_begruendung && (
        <div className="p-4 rounded-md bg-indigo-50 border border-indigo-200">
          <div className="flex items-center gap-2 text-indigo-900 font-medium mb-2">
            <Sparkles className="h-4 w-4" />
            Curator-Begründung (warum wurde dieser Beitrag ausgewählt)
          </div>
          <p className="text-sm text-indigo-900 leading-relaxed">
            {post.curator_begruendung}
          </p>
        </div>
      )}

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

      <div className="flex items-center gap-2 pt-3 border-t">
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
          {editMode && (
            <Button
              size="sm"
              onClick={handleSave}
              disabled={!hasEdits || patchMut.isPending}
            >
              Speichern
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={onClose}>
            Schließen
          </Button>
        </div>
      </div>
    </div>
  );
}

// --- ConfidenceBadge: visualisiert den Verifier-Score ----------------

function ConfidenceBadge({
  confidence,
  issuesCount,
  status,
}: {
  confidence: number;
  issuesCount: number;
  status: NewsPostStatus;
}) {
  const pct = Math.round(confidence * 100);
  let toneClass = "bg-emerald-100 text-emerald-800 border-emerald-200";
  let icon = <CheckCircle2 className="inline h-3 w-3 mr-0.5" />;
  if (confidence < 0.75) {
    toneClass = "bg-rose-100 text-rose-800 border-rose-200";
    icon = <AlertTriangle className="inline h-3 w-3 mr-0.5" />;
  } else if (confidence < 0.9) {
    toneClass = "bg-amber-100 text-amber-800 border-amber-200";
    icon = <AlertTriangle className="inline h-3 w-3 mr-0.5" />;
  }
  return (
    <span
      className={cn(
        "px-2 py-0.5 rounded-full text-[10px] uppercase tracking-wide font-medium border",
        toneClass,
      )}
      title={`Verifier-Confidence ${pct} % · ${issuesCount} Issue(s) · Status: ${STATUS_LABEL[status]}`}
    >
      {icon}
      {pct}% Konfidenz
      {issuesCount > 0 && ` · ${issuesCount} Issue${issuesCount === 1 ? "" : "s"}`}
    </span>
  );
}

// --- PipelineAnalyse: kompakte Karte mit allen Pipeline-Daten --------

function PipelineAnalyse({ post }: { post: NewsPostAdmin }) {
  const conf = post.verifier_confidence;
  const confPct = conf != null ? Math.round(conf * 100) : null;
  let confColor = "bg-slate-200";
  if (conf != null) {
    if (conf >= 0.9) confColor = "bg-emerald-500";
    else if (conf >= 0.75) confColor = "bg-amber-500";
    else confColor = "bg-rose-500";
  }
  return (
    <div className="rounded-md border border-slate-200 bg-slate-50/70 overflow-hidden">
      <div className="px-4 py-2 border-b border-slate-200 bg-white">
        <div className="flex items-center gap-2 text-slate-700 font-medium text-sm">
          <Gauge className="h-4 w-4" />
          Pipeline-Analyse
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3 px-4 py-3 text-sm">
        {/* Verifier-Score als Bar */}
        <div className="md:col-span-2">
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
            <span className="uppercase tracking-wide">Verifier-Konfidenz</span>
            <span className="font-mono text-slate-900">
              {confPct != null ? `${confPct} %` : "n/a"}
              {confPct != null && (
                <span className="text-muted-foreground">
                  {" · Schwelle 90 %"}
                </span>
              )}
            </span>
          </div>
          <div className="h-2 w-full rounded-full bg-slate-200 overflow-hidden">
            <div
              className={cn("h-full transition-all", confColor)}
              style={{ width: `${confPct ?? 0}%` }}
            />
          </div>
          <div className="mt-1.5 text-xs text-muted-foreground">
            {conf == null
              ? "Verifier wurde noch nicht ausgeführt (Post manuell angelegt oder vom seed-Command erstellt)."
              : conf >= 0.9
                ? "Über Schwelle: automatisch published."
                : conf >= 0.75
                  ? "Knapp unter Schwelle: in Hold zur manuellen Sichtung."
                  : "Deutlich unter Schwelle: Verifier hat substantielle Issues gefunden."}
          </div>
        </div>

        {/* Issues-Count */}
        <Field label="Verifier-Issues">
          {post.verifier_issues && post.verifier_issues.length > 0 ? (
            <span className="text-amber-700 font-medium">
              {post.verifier_issues.length} Befund
              {post.verifier_issues.length === 1 ? "" : "e"}
            </span>
          ) : (
            <span className="text-emerald-700">keine</span>
          )}
        </Field>

        <Field label="Quelle">{post.candidate_quelle ?? "—"}</Field>

        <Field label="Crawl-Zeitpunkt">
          {post.candidate_fetched_at
            ? new Date(post.candidate_fetched_at).toLocaleString("de-DE")
            : "—"}
        </Field>

        <Field label="Veröffentlicht in Original-Quelle">
          {post.candidate_published_at_source
            ? new Date(post.candidate_published_at_source).toLocaleDateString(
                "de-DE",
              )
            : "—"}
        </Field>

        <Field label="Relevanz / Standzeit">
          {RELEVANZ_LABEL[post.relevanz]}
          {post.lifetime_days != null && ` · ${post.lifetime_days} Tage`}
        </Field>

        <Field label="Status">{STATUS_LABEL[post.status]}</Field>

        {post.published_at && (
          <Field label="Live seit">
            {new Date(post.published_at).toLocaleString("de-DE")}
            {post.days_since_published != null && (
              <span className="text-muted-foreground">
                {" · "}
                {post.days_since_published} Tag
                {post.days_since_published === 1 ? "" : "e"}
              </span>
            )}
          </Field>
        )}

        {post.expires_at && (
          <Field label="Läuft ab">
            {new Date(post.expires_at).toLocaleString("de-DE")}
            {post.days_until_expiry != null && (
              <span
                className={cn(
                  "ml-1",
                  post.days_until_expiry <= 7
                    ? "text-amber-700 font-medium"
                    : "text-muted-foreground",
                )}
              >
                {" · "}
                {post.days_until_expiry > 0
                  ? `in ${post.days_until_expiry} Tag${post.days_until_expiry === 1 ? "" : "en"}`
                  : "abgelaufen"}
              </span>
            )}
          </Field>
        )}

        <Field label="Beitrag-Slug">
          <span className="font-mono text-xs">{post.slug}</span>
        </Field>

        <Field label="Notbremse-URL (Token)">
          <a
            href={post.notbremse_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary hover:underline font-mono text-xs break-all"
          >
            {post.notbremse_url}
          </a>
        </Field>
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-widest text-muted-foreground mb-0.5">
        {label}
      </div>
      <div className="text-sm text-slate-900">{children}</div>
    </div>
  );
}
