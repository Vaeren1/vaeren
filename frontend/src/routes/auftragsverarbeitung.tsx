/**
 * Auftragsverarbeitung (DSGVO Art. 28): Liste der AVV-Verträge.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  type AVVStatus,
  type Drittlandstatus,
  createVerarbeiter,
  listVerarbeiter,
} from "@/lib/api/auftragsverarbeitung";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

const DRITTLAND_LABEL: Record<Drittlandstatus, string> = {
  eu_ewr: "EU/EWR",
  angemessenheit: "Drittland (Angemessenheit)",
  scc: "Drittland (SCC)",
  bcr: "Drittland (BCR)",
  kritisch: "Drittland (kritisch)",
};

const STATUS_LABEL: Record<AVVStatus, string> = {
  offen: "AVV offen",
  aktiv: "AVV aktiv",
  beendet: "Beendet",
  pruefung: "In Prüfung",
};

export function AVVListPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["avv"],
    queryFn: listVerarbeiter,
  });
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState("");
  const [land, setLand] = useState("Deutschland");
  const [drittland, setDrittland] = useState<Drittlandstatus>("eu_ewr");
  const [notizen, setNotizen] = useState("");

  const create = useMutation({
    mutationFn: createVerarbeiter,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["avv"] });
      setName("");
      setLand("Deutschland");
      setDrittland("eu_ewr");
      setNotizen("");
      setShowForm(false);
      toast.success("Auftragsverarbeiter erfasst.");
    },
    onError: () => toast.error("Speichern fehlgeschlagen."),
  });

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Auftragsverarbeitung</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              DSGVO Art. 28: Verträge mit externen Verarbeitern (Hosting, Mail, Analytics, etc.).
            </p>
          </div>
          <Button onClick={() => setShowForm(!showForm)}>
            {showForm ? "Abbrechen" : "+ Verarbeiter erfassen"}
          </Button>
        </CardHeader>
        {showForm && (
          <CardContent className="space-y-3 border-t pt-4">
            <div className="grid md:grid-cols-2 gap-3">
              <div className="space-y-1.5">
                <Label htmlFor="avv_name">Name</Label>
                <Input id="avv_name" value={name} onChange={(e) => setName(e.target.value)} />
              </div>
              <div className="space-y-1.5">
                <Label htmlFor="avv_land">Rechtssitz-Land</Label>
                <Input id="avv_land" value={land} onChange={(e) => setLand(e.target.value)} />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="avv_drittland">Drittland-Status</Label>
              <select
                id="avv_drittland"
                value={drittland}
                onChange={(e) => setDrittland(e.target.value as Drittlandstatus)}
                className="w-full px-3 py-2 border rounded"
              >
                {Object.entries(DRITTLAND_LABEL).map(([v, l]) => (
                  <option key={v} value={v}>{l}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="avv_notizen">Notizen</Label>
              <Textarea
                id="avv_notizen"
                rows={2}
                value={notizen}
                onChange={(e) => setNotizen(e.target.value)}
              />
            </div>
            <Button
              onClick={() => create.mutate({ name, rechtssitz_land: land, drittland, notizen })}
              disabled={!name || create.isPending}
            >
              Erfassen
            </Button>
          </CardContent>
        )}
      </Card>

      {isLoading && <p>Lade …</p>}
      {data && data.results.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-muted-foreground">
            Noch keine Auftragsverarbeiter erfasst. Klassiker zum Start: Hosting-Anbieter, Mail-Provider,
            Buchhaltungs-Cloud, CRM, Analytics, Backup-Lösung.
          </CardContent>
        </Card>
      )}
      {data &&
        data.results.map((v) => (
          <Card key={v.id}>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-base">
                  <Link to={`/avv/${v.id}`} className="underline">
                    {v.name}
                  </Link>
                </CardTitle>
                <p className="text-xs text-muted-foreground">
                  {v.rechtssitz_land} · {DRITTLAND_LABEL[v.drittland]}
                </p>
              </div>
              <div className="text-right text-sm">
                <p className={v.benoetigt_handlung ? "text-amber-700" : "text-emerald-700"}>
                  {STATUS_LABEL[v.status]} {v.benoetigt_handlung && "(Handlung)"}
                </p>
                {v.avv_endet_am && (
                  <p className="text-xs text-muted-foreground">endet: {v.avv_endet_am}</p>
                )}
              </div>
            </CardHeader>
          </Card>
        ))}
    </div>
  );
}
