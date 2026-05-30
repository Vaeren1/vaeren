/**
 * Onboarding-Wizard / Compliance-Radar (Feature 1, §3).
 *
 * 5-Schritt-Container. Hält den Schritt-State und ruft pro Schritt die API
 * (`@/lib/api/onboarding`). Erst-Login-Redirect verdrahtet in der
 * `RequireWizard`-Guard (siehe router.tsx).
 */
import { RadarScreen } from "@/components/wizard/RadarScreen";
import { StepAktivieren } from "@/components/wizard/StepAktivieren";
import { StepAnalyse } from "@/components/wizard/StepAnalyse";
import { StepBestaetigen } from "@/components/wizard/StepBestaetigen";
import { StepStart } from "@/components/wizard/StepStart";
import {
  type Profil,
  type RadarResult,
  onboarding,
} from "@/lib/api/onboarding";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

type Schritt = 1 | 2 | 3 | 4 | 5;

export function OnboardingWizardPage() {
  const [schritt, setSchritt] = useState<Schritt>(1);
  const [profil, setProfil] = useState<Profil | null>(null);
  const [radar, setRadar] = useState<RadarResult | null>(null);
  const [radarLaedt, setRadarLaedt] = useState(false);
  const navigate = useNavigate();

  const onBestaetigt = async (patch: Partial<Profil>) => {
    setRadarLaedt(true);
    try {
      await onboarding.speicherProfil(patch);
      const r = await onboarding.radar();
      setRadar(r);
      setSchritt(4);
    } catch {
      toast.error(
        "Radar konnte nicht berechnet werden. Bitte erneut versuchen.",
      );
    } finally {
      setRadarLaedt(false);
    }
  };

  const onAktiviert = async (keys: string[]) => {
    await onboarding.aktivieren(keys);
    toast.success("Module aktiviert.");
    navigate("/");
  };

  return (
    <div className="mx-auto max-w-3xl p-6">
      <ol className="mb-6 flex items-center gap-2 text-xs text-muted-foreground">
        {["Start", "Analyse", "Prüfen", "Radar", "Aktivieren"].map(
          (label, i) => (
            <li
              key={label}
              className={`rounded-full px-2.5 py-1 ${
                schritt === i + 1
                  ? "bg-primary text-primary-foreground"
                  : schritt > i + 1
                    ? "bg-emerald-100 text-emerald-800"
                    : "bg-secondary"
              }`}
            >
              {i + 1}. {label}
            </li>
          ),
        )}
      </ol>

      {schritt === 1 && (
        <StepStart
          onDone={(p) => {
            setProfil(p);
            setSchritt(2);
          }}
        />
      )}
      {schritt === 2 && profil && (
        <StepAnalyse profil={profil} onNext={() => setSchritt(3)} />
      )}
      {schritt === 3 && profil && (
        <StepBestaetigen
          profil={profil}
          onNext={onBestaetigt}
          laedt={radarLaedt}
        />
      )}
      {schritt === 4 && radar && (
        <RadarScreen
          radar={radar}
          firmenname={profil?.firmenname}
          onNext={() => setSchritt(5)}
        />
      )}
      {schritt === 5 && radar && (
        <StepAktivieren
          empfohlen={radar.empfohlene_module}
          onDone={onAktiviert}
        />
      )}
    </div>
  );
}
