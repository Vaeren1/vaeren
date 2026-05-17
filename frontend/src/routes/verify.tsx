/**
 * Public Verify-Page — kein Auth, vom Auditor extern aufrufbar.
 *
 * Form: Mappe-ID + File-Hash → Authentizität-Check via /api/audit-export/verify/.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { verifyMappe, type VerifyResponse } from "@/lib/api/audit_export";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

export function VerifyPage() {
  const [params] = useSearchParams();
  const [mappeId, setMappeId] = useState(params.get("mappe") || "");
  const [fileHash, setFileHash] = useState(params.get("hash") || "");
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const doVerify = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await verifyMappe({
        mappe_id: mappeId.trim(),
        file_sha256: fileHash.trim(),
      });
      setResult(r);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // Auto-verify wenn beide Query-Params gesetzt sind
  useEffect(() => {
    if (
      params.get("mappe") &&
      params.get("hash") &&
      mappeId &&
      fileHash &&
      result === null &&
      !loading
    ) {
      doVerify();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="mx-auto max-w-xl py-8 px-4">
      <h1 className="text-2xl font-semibold mb-2">Vaeren Audit-Mappe verifizieren</h1>
      <p className="text-sm text-muted-foreground mb-6">
        Geben Sie die Mappe-ID und den SHA-256-Hash des ZIP-Bundles ein, um die
        Authentizität gegen Vaeren zu prüfen. Diese Seite ist öffentlich
        erreichbar — Vaeren gibt nur die Tenant-ID und den Norm-Scope zurück,
        keine vertraulichen Daten.
      </p>

      <Card>
        <CardHeader>
          <CardTitle>Mappe prüfen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="mappe">Mappe-ID</Label>
            <Input
              id="mappe"
              value={mappeId}
              onChange={(e) => setMappeId(e.target.value)}
              placeholder="VAE-2026-0517-A3F2"
            />
          </div>
          <div>
            <Label htmlFor="hash">SHA-256 des Bundle-ZIPs</Label>
            <Input
              id="hash"
              value={fileHash}
              onChange={(e) => setFileHash(e.target.value)}
              placeholder="64 Hex-Zeichen"
              className="font-mono"
            />
          </div>
          <Button
            disabled={loading || !mappeId || !fileHash}
            onClick={doVerify}
          >
            {loading ? "Prüfe …" : "Verifizieren"}
          </Button>

          {error && <p className="text-destructive text-sm">{error}</p>}

          {result && (
            <div
              className={`mt-4 rounded border p-4 ${
                result.verified
                  ? "border-emerald-300 bg-emerald-50"
                  : "border-rose-300 bg-rose-50"
              }`}
            >
              {result.verified ? (
                <>
                  <p className="font-semibold text-emerald-800">
                    ✓ Authentisch
                  </p>
                  <dl className="mt-2 text-sm space-y-1">
                    <div>
                      <dt className="inline text-muted-foreground">Tenant:</dt>{" "}
                      <dd className="inline font-mono">{result.tenant}</dd>
                    </div>
                    <div>
                      <dt className="inline text-muted-foreground">
                        Norm-Scope:
                      </dt>{" "}
                      <dd className="inline">
                        {(result.norm_scope || []).join(", ")}
                      </dd>
                    </div>
                    <div>
                      <dt className="inline text-muted-foreground">
                        Generiert:
                      </dt>{" "}
                      <dd className="inline">{result.generated_at}</dd>
                    </div>
                  </dl>
                </>
              ) : (
                <>
                  <p className="font-semibold text-rose-800">
                    ✗ Nicht verifizierbar
                  </p>
                  <p className="text-sm mt-1">
                    Grund: <code>{result.reason}</code>
                  </p>
                  {result.reason === "hash_mismatch" && (
                    <p className="text-xs mt-2 text-muted-foreground">
                      Der ZIP-Hash stimmt nicht mit der bei Vaeren hinterlegten
                      Signatur überein. Möglicherweise wurde die Datei
                      verändert.
                    </p>
                  )}
                  {result.reason === "mappe_unknown" && (
                    <p className="text-xs mt-2 text-muted-foreground">
                      Diese Mappe-ID ist Vaeren nicht bekannt.
                    </p>
                  )}
                </>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
