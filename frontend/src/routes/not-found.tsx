import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-24 text-center">
      <p className="text-5xl font-bold text-muted-foreground">404</p>
      <h1 className="text-xl font-semibold">Seite nicht gefunden</h1>
      <p className="max-w-md text-sm text-muted-foreground">
        Diese Seite existiert nicht (mehr). Möglicherweise wurde der Link
        geändert oder der Eintrag entfernt.
      </p>
      <Link to="/" className="text-sm font-medium text-primary underline">
        Zurück zum Dashboard
      </Link>
    </div>
  );
}
