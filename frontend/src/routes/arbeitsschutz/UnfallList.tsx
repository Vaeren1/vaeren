/**
 * Arbeitsunfall-Liste + Modal-Form zum Melden.
 *
 * DSGVO Art. 9: nur GF / QM / CB dürfen Unfälle erfassen.
 * Inhalt-Felder werden at-rest verschlüsselt (Backend, Fernet).
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  bgGemeldet,
  createUnfall,
  listArbeitsbereiche,
  listTaetigkeiten,
  listUnfaelle,
  unfallStatistik,
  type Arbeitsbereich,
  type Taetigkeit,
  type Unfall,
  type UnfallSchwere,
} from "@/lib/api/arbeitsschutz";
import { useMitarbeiterList } from "@/lib/api/mitarbeiter";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

const SCHWERE_LABEL: Record<UnfallSchwere, string> = {
  bagatell: "Bagatell",
  leicht: "Leicht",
  meldepflichtig: "Meldepflichtig",
  schwer: "Schwer",
  toedlich: "Tödlich",
  fast_unfall: "Beinahe-Unfall",
};

const SCHWERE_COLOR: Record<UnfallSchwere, string> = {
  bagatell: "text-slate-700",
  leicht: "text-amber-700",
  meldepflichtig: "text-rose-700",
  schwer: "text-rose-800 font-semibold",
  toedlich: "text-red-900 font-bold",
  fast_unfall: "text-sky-700",
};

const SCHWERE_VALUES: UnfallSchwere[] = [
  "bagatell",
  "leicht",
  "meldepflichtig",
  "schwer",
  "toedlich",
  "fast_unfall",
];

const ERLAUBTE_ROLLEN = new Set([
  "geschaeftsfuehrer",
  "qm_leiter",
  "compliance_beauftragter",
]);

export function UnfallListPage() {
  const qc = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const darfMelden = user?.tenant_role
    ? ERLAUBTE_ROLLEN.has(user.tenant_role)
    : false;

  const list = useQuery({ queryKey: ["as-unfaelle"], queryFn: listUnfaelle });
  const stat = useQuery({ queryKey: ["as-unfall-stat"], queryFn: unfallStatistik });

  const [showForm, setShowForm] = useState(false);
  const [bgForm, setBgForm] = useState<{ id: number; aktenzeichen: string } | null>(
    null,
  );

  const createMut = useMutation({
    mutationFn: createUnfall,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["as-unfaelle"] });
      qc.invalidateQueries({ queryKey: ["as-unfall-stat"] });
      toast.success("Unfall erfasst.");
      setShowForm(false);
    },
    onError: (e: unknown) => {
      const msg = e instanceof Error ? e.message : "Erfassen fehlgeschlagen";
      toast.error(msg);
    },
  });

  const bgMut = useMutation({
    mutationFn: (vars: { id: number; aktenzeichen: string }) =>
      bgGemeldet(vars.id, { bg_aktenzeichen: vars.aktenzeichen }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["as-unfaelle"] });
      toast.success("Als BG-gemeldet markiert.");
      setBgForm(null);
    },
    onError: () => toast.error("Speichern fehlgeschlagen."),
  });

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">YTD gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stat.data?.ytd_total ?? "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">YTD meldepfl.</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-rose-700">
              {stat.data?.ytd_meldepflichtig ?? "—"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">YTD schwer</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stat.data?.ytd_schwer ?? "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Ausfalltage YTD</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stat.data?.ytd_ausfalltage ?? "—"}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Arbeitsunfälle</CardTitle>
              <p className="text-xs text-muted-foreground">
                Inhalt verschlüsselt at-rest · DSGVO Art. 9. Klarname nur in
                Detail-Ansicht.
              </p>
            </div>
            {darfMelden && (
              <Button onClick={() => setShowForm(true)}>+ Unfall melden</Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {list.data && list.data.results.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Bisher keine Unfälle erfasst. Im Fall der Fälle: sofort hier eintragen.
            </p>
          )}
          {list.data && list.data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Datum</TableHead>
                  <TableHead>Bereich</TableHead>
                  <TableHead>Schwere</TableHead>
                  <TableHead>Ausfalltage</TableHead>
                  <TableHead>BG-Meldung</TableHead>
                  <TableHead>Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {list.data.results.map((u) => (
                  <TableRow key={u.id}>
                    <TableCell>{new Date(u.datum).toLocaleDateString("de-DE")}</TableCell>
                    <TableCell>{u.arbeitsbereich_name}</TableCell>
                    <TableCell className={SCHWERE_COLOR[u.schwere]}>
                      {SCHWERE_LABEL[u.schwere]}
                    </TableCell>
                    <TableCell>{u.ausfalltage}</TableCell>
                    <TableCell className="text-xs">
                      {u.bg_gemeldet_am
                        ? `gemeldet ${u.bg_gemeldet_am}`
                        : u.bg_meldung_pflicht
                          ? `Frist ${u.bg_meldefrist}`
                          : "—"}
                    </TableCell>
                    <TableCell>
                      {darfMelden && u.bg_meldung_pflicht && !u.bg_gemeldet_am && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            setBgForm({ id: u.id, aktenzeichen: "" })
                          }
                        >
                          BG-Meldung erfassen
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {showForm && (
        <UnfallForm
          onCancel={() => setShowForm(false)}
          onSubmit={(payload) => createMut.mutate(payload)}
          isPending={createMut.isPending}
        />
      )}

      {bgForm && (
        <BgMeldungDialog
          aktenzeichen={bgForm.aktenzeichen}
          onChange={(a) => setBgForm({ ...bgForm, aktenzeichen: a })}
          onCancel={() => setBgForm(null)}
          onConfirm={() =>
            bgMut.mutate({ id: bgForm.id, aktenzeichen: bgForm.aktenzeichen })
          }
          isPending={bgMut.isPending}
        />
      )}
    </div>
  );
}

// =========================================================================
// Unfall-Form (Modal)
// =========================================================================

function meldefristHinweis(schwere: UnfallSchwere): {
  text: string;
  color: string;
} {
  switch (schwere) {
    case "bagatell":
    case "leicht":
    case "fast_unfall":
      return { text: "Keine BG-Meldepflicht.", color: "bg-slate-50 text-slate-700" };
    case "meldepflichtig":
      return {
        text: "BG-Meldefrist: 3 Werktage (§193 SGB VII).",
        color: "bg-amber-50 text-amber-900",
      };
    case "schwer":
      return {
        text: "⚠ Sofortige BG-Meldung erforderlich (Ausfall > 3 Tage oder schwere Verletzung).",
        color: "bg-rose-50 text-rose-900 font-medium",
      };
    case "toedlich":
      return {
        text: "⚠ Sofortige BG-Meldung erforderlich + StA-Meldung. Tatort sichern!",
        color: "bg-red-100 text-red-900 font-semibold",
      };
  }
}

function UnfallForm({
  onCancel,
  onSubmit,
  isPending,
}: {
  onCancel: () => void;
  onSubmit: (payload: Partial<Unfall>) => void;
  isPending: boolean;
}) {
  const bereiche = useQuery({
    queryKey: ["as-arbeitsbereiche"],
    queryFn: listArbeitsbereiche,
  });
  const taetigkeiten = useQuery({
    queryKey: ["as-taetigkeiten"],
    queryFn: listTaetigkeiten,
  });
  const mitarbeiter = useMitarbeiterList();

  const [datum, setDatum] = useState(new Date().toISOString().slice(0, 16));
  const [arbeitsbereichId, setArbeitsbereichId] = useState<number | "">("");
  const [taetigkeitId, setTaetigkeitId] = useState<number | "">("");
  const [schwere, setSchwere] = useState<UnfallSchwere>("leicht");
  const [ausfalltage, setAusfalltage] = useState<number>(0);
  const [betroffenerIntern, setBetroffenerIntern] = useState<number | "">("");
  const [betroffenerName, setBetroffenerName] = useState("");
  const [beschreibung, setBeschreibung] = useState("");
  const [verletzungsart, setVerletzungsart] = useState("");

  const taetigkeitenGefiltert: Taetigkeit[] =
    taetigkeiten.data?.results.filter((t) =>
      arbeitsbereichId === "" ? true : t.arbeitsbereich === arbeitsbereichId,
    ) ?? [];

  const hinweis = meldefristHinweis(schwere);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (arbeitsbereichId === "") {
      toast.error("Arbeitsbereich ist Pflicht.");
      return;
    }
    if (!beschreibung.trim()) {
      toast.error("Beschreibung ist Pflicht.");
      return;
    }
    onSubmit({
      datum,
      arbeitsbereich: Number(arbeitsbereichId) as unknown as Unfall["arbeitsbereich"],
      taetigkeit: taetigkeitId === "" ? null : Number(taetigkeitId),
      schwere,
      ausfalltage,
      betroffener_intern:
        betroffenerIntern === "" ? null : Number(betroffenerIntern),
      betroffener_name: betroffenerName,
      beschreibung,
      verletzungsart,
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4">
      <form
        className="w-[720px] max-w-full max-h-[90vh] overflow-y-auto rounded-md bg-white p-6 shadow-xl"
        onSubmit={handleSubmit}
      >
        <h2 className="mb-1 text-lg font-semibold">Arbeitsunfall melden</h2>
        <p className="text-xs text-muted-foreground">
          DSGVO Art. 9: Gesundheitsdaten. Inhaltsfelder (Name, Beschreibung,
          Verletzungsart) werden at-rest verschlüsselt gespeichert.
        </p>

        <div className="my-3 grid grid-cols-2 gap-3">
          <div>
            <Label>Datum & Uhrzeit</Label>
            <Input
              type="datetime-local"
              value={datum}
              onChange={(e) => setDatum(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Schwere</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={schwere}
              onChange={(e) => setSchwere(e.target.value as UnfallSchwere)}
            >
              {SCHWERE_VALUES.map((s) => (
                <option key={s} value={s}>
                  {SCHWERE_LABEL[s]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Arbeitsbereich</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={arbeitsbereichId}
              onChange={(e) => {
                setArbeitsbereichId(e.target.value ? Number(e.target.value) : "");
                setTaetigkeitId("");
              }}
              required
            >
              <option value="">— bitte wählen —</option>
              {bereiche.data?.results.map((b: Arbeitsbereich) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Tätigkeit (optional)</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={taetigkeitId}
              onChange={(e) =>
                setTaetigkeitId(e.target.value ? Number(e.target.value) : "")
              }
              disabled={arbeitsbereichId === ""}
            >
              <option value="">— keine zugeordnet —</option>
              {taetigkeitenGefiltert.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Ausfalltage</Label>
            <Input
              type="number"
              min={0}
              value={ausfalltage}
              onChange={(e) => setAusfalltage(Number(e.target.value))}
            />
          </div>
          <div>
            <Label>Betroffener (intern)</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={betroffenerIntern}
              onChange={(e) =>
                setBetroffenerIntern(e.target.value ? Number(e.target.value) : "")
              }
            >
              <option value="">— extern / unbekannt —</option>
              {mitarbeiter.data?.results.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.vorname} {m.nachname}
                </option>
              ))}
            </select>
          </div>
        </div>

        {betroffenerIntern === "" && (
          <div className="mb-3">
            <Label>Klarname (extern, optional, verschlüsselt)</Label>
            <Input
              value={betroffenerName}
              onChange={(e) => setBetroffenerName(e.target.value)}
              placeholder="Z. B. Leiharbeiter / Besucher"
            />
          </div>
        )}

        <div className="mb-3">
          <Label>Beschreibung *</Label>
          <textarea
            className="w-full rounded border px-3 py-2 text-sm"
            rows={4}
            value={beschreibung}
            onChange={(e) => setBeschreibung(e.target.value)}
            placeholder="Hergang, Zeitpunkt, Beteiligte, Sachverhalt…"
            required
          />
        </div>

        <div className="mb-3">
          <Label>Verletzungsart (optional, verschlüsselt)</Label>
          <textarea
            className="w-full rounded border px-3 py-2 text-sm"
            rows={2}
            value={verletzungsart}
            onChange={(e) => setVerletzungsart(e.target.value)}
            placeholder="Z. B. Schnittwunde linke Hand, Verstauchung…"
          />
        </div>

        <div className={"rounded p-3 text-sm " + hinweis.color}>
          <strong>Frist-Hinweis:</strong> {hinweis.text}
        </div>

        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            {isPending ? "speichert…" : "Unfall erfassen"}
          </Button>
        </div>
      </form>
    </div>
  );
}

function BgMeldungDialog({
  aktenzeichen,
  onChange,
  onCancel,
  onConfirm,
  isPending,
}: {
  aktenzeichen: string;
  onChange: (a: string) => void;
  onCancel: () => void;
  onConfirm: () => void;
  isPending: boolean;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4">
      <form
        className="w-[480px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onConfirm();
        }}
      >
        <h2 className="mb-2 text-lg font-semibold">Als BG-gemeldet markieren</h2>
        <p className="text-sm text-muted-foreground">
          Bestätigt, dass eine Meldung an die zuständige Berufsgenossenschaft
          erfolgt ist.
        </p>
        <div className="mt-3">
          <Label>BG-Aktenzeichen (optional)</Label>
          <Input
            value={aktenzeichen}
            onChange={(e) => onChange(e.target.value)}
            placeholder="z. B. BGHM-2026-12345"
          />
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Als gemeldet markieren
          </Button>
        </div>
      </form>
    </div>
  );
}
