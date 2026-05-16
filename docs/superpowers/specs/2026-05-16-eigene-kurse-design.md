# Spec — Eigene Kurse: Editor, Multi-Format-Material, optionales Quiz, optionales Zertifikat

**Datum:** 2026-05-16
**Status:** Draft (Brainstorming abgeschlossen, wartet auf User-Review)
**Scope:** Vier vertikale Slices, jeder einzeln launch-bar. Endzustand: Kunden legen unter `https://app.vaeren.de/kurse` eigene Kurse an, laden Material in allen relevanten Formaten hoch, lassen Quiz-Fragen vom LLM vorschlagen, rollen Welle aus, Mitarbeiter:innen durchlaufen Quiz oder Kenntnisnahme, erhalten optional ein Zertifikat.

---

## 1. Motivation

Heute existieren 20 von Vaeren vor-redaktionell aufbereitete Pflichtkurse (`pflichtunterweisung.seed_data`). Tenants können diese ausrollen, aber **keine eigenen Kurse anlegen**. Pilot-Kunden wollen aber:

- vorhandene Schulungsunterlagen (PDF, PPT, Video) im Tenant nutzen
- spezifische, nicht-generische Themen abdecken (z.B. „Sicherheitsunterweisung Halle 3 — Pressenlinie")
- Quiz-Pool und Zertifikat **optional** halten (manche Kurse sind reine Lese-Bestätigung)

Ohne diese Erweiterung bleibt Vaeren ein Katalog-Anbieter. Mit ihr wird es ein echtes Compliance-Werkzeug, das Bestandsunterlagen einbindet — das ist USP-relevant.

---

## 2. Lieferumfang & Slicing

Das Feature wird in **4 vertikale Slices** zerlegt, jeder einzeln Backend+Frontend+Tests+Migration+Deploy-fertig (Regel: `CLAUDE.md` → „Feature-Completion-Discipline"). Kein Slice bricht den bestehenden Standard-Katalog.

| # | Slice | Mehrwert nach Deploy |
|---|---|---|
| S1 | Kurs-Skelett (CRUD + Settings) | Kunde legt Kurse mit Stammdaten an (Quiz-Modus, Zertifikat-Schalter, Gültigkeit, Bestehensschwelle) |
| S2 | Modul-Editor (alle Formate) | Kunde fügt Module hinzu: Text/Markdown, PDF, Bild, Office (DOCX/PPTX, intern zu PDF konvertiert), Video-Upload, YouTube-Embed |
| S3 | Quiz-Pool + LLM-Vorschlag | Kunde legt Fragen manuell an oder lässt sie aus Material vorschlagen (HITL-Bestätigung, RDG-Layer-3) |
| S4 | Welle-Snapshot + neue Player-Modi | Beim Versand wird Kurs eingefroren; Mitarbeiter:in sieht Quiz / Kenntnisnahme / Kenntnisnahme+Min-Lesezeit; Zertifikat nur wenn Schalter aktiv |

**Out of Scope (bewusst):**

- Live-Collaboration / Mehrnutzer-Editing (single-editor reicht für KMU)
- Video-Streaming-Optimierung (HLS/DASH) — direktes MP4-Serving via Caddy genügt bis ~500 MB
- Whisper-Transkription für Video-Upload (zu komplex für MVP) — nur YouTube-Untertitel werden für LLM-Quiz genutzt
- OCR für Bild-Module (keine Quiz-Generierung aus Schaubildern)
- ClamAV-Virus-Scan (Schema-Isolation + MIME-Whitelist + Größenlimit als ausreichende Verteidigung im MVP; `scan_status`-Feld bleibt für Phase 2)
- Public-Kurs-Bibliothek (Tenants sehen nur eigene + Vaeren-Standard, kein Cross-Tenant-Teilen)
- Kurs-Klonen aus Standard-Katalog (Convenience-Feature für später)

---

## 3. Datenmodell

Alle Änderungen liegen in `backend/pflichtunterweisung/models.py`. Migrationen sind rückwärtskompatibel (alle neuen Felder mit Defaults).

### 3.1 `Kurs` — neue Felder

```python
class Kurs(models.Model):
    # ... bestehend: titel, beschreibung, gueltigkeit_monate, min_richtig_prozent,
    #     fragen_pro_quiz, aktiv, erstellt_am

    class QuizModus(models.TextChoices):
        QUIZ = "quiz", "Quiz"
        KENNTNISNAHME = "kenntnisnahme", "Kenntnisnahme"
        KENNTNISNAHME_LESEZEIT = "kenntnisnahme_lesezeit", "Kenntnisnahme + Min-Lesezeit"

    quiz_modus = models.CharField(max_length=30, choices=QuizModus.choices,
                                   default=QuizModus.QUIZ)
    mindest_lesezeit_s = models.PositiveIntegerField(default=0,
        help_text="Sekunden pro Modul, ab denen 'Kenntnisnahme' aktivierbar ist. "
                  "Nur ausgewertet bei quiz_modus=kenntnisnahme_lesezeit.")
    zertifikat_aktiv = models.BooleanField(default=True)
    eigentuemer_tenant = models.CharField(max_length=63, blank=True,
        help_text="Schema-Name des Tenants, der den Kurs angelegt hat. "
                  "Leer = Vaeren-Standardkatalog (read-only für Tenants im MVP).")
    erstellt_von = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="erstellte_kurse")
```

**Constraint:** `clean()` erzwingt:
- wenn `quiz_modus != QUIZ` → `fragen_pro_quiz = 0` und `min_richtig_prozent = 0` (UI versteckt diese Felder dann)
- wenn `quiz_modus == KENNTNISNAHME_LESEZEIT` → `mindest_lesezeit_s > 0`

### 3.2 `KursModul` — Discriminator + Asset-Verknüpfung

```python
class KursModul(models.Model):
    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE, related_name="module")
    titel = models.CharField(max_length=200)
    reihenfolge = models.PositiveSmallIntegerField(default=0)

    class Typ(models.TextChoices):
        TEXT = "text", "Text/Markdown"
        PDF = "pdf", "PDF"
        BILD = "bild", "Bild (PNG/JPG)"
        OFFICE = "office", "Office (DOCX/PPTX)"
        VIDEO_UPLOAD = "video_upload", "Video-Upload"
        VIDEO_YOUTUBE = "video_youtube", "YouTube-Embed"

    typ = models.CharField(max_length=20, choices=Typ.choices, default=Typ.TEXT)
    inhalt_md = models.TextField(blank=True,
        help_text="Markdown-Inhalt. Befüllt nur bei typ=TEXT.")
    youtube_url = models.URLField(blank=True,
        help_text="YouTube-Watch-URL. Befüllt nur bei typ=VIDEO_YOUTUBE.")
    asset = models.ForeignKey("KursAsset", null=True, blank=True,
        on_delete=models.PROTECT, related_name="module",
        help_text="Datei-Asset. Befüllt bei pdf/bild/office/video_upload.")
    transcript_cache = models.TextField(blank=True,
        help_text="Bei typ=VIDEO_YOUTUBE: Cache der YouTube-Untertitel (via "
                  "youtube-transcript-api). Befüllt durch Celery-Task, leer "
                  "wenn keine Untertitel verfügbar.")

    class Meta:
        ordering = ("reihenfolge", "id")
        unique_together = (("kurs", "reihenfolge"),)
```

**Constraint:** `clean()` erzwingt Konsistenz zwischen `typ` und Inhalts-Feld:
- `TEXT` → `inhalt_md` non-empty, asset+youtube_url leer
- `VIDEO_YOUTUBE` → `youtube_url` non-empty, asset+inhalt_md leer
- alle anderen → `asset` non-null, andere leer

Bestandsdaten (Seed-Katalog) sind alle `typ=TEXT` mit gefülltem `inhalt_md` → Migration setzt Default `TEXT` und passt nichts an.

### 3.3 `KursAsset` (neu)

```python
class KursAsset(models.Model):
    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE, related_name="assets")
    original_datei = models.FileField(upload_to="kurs-uploads/%Y/%m/")
    original_mime = models.CharField(max_length=100)
    original_size_bytes = models.PositiveIntegerField()

    konvertierte_pdf = models.FileField(upload_to="kurs-uploads/%Y/%m/",
                                         blank=True, null=True,
        help_text="Bei typ=office: von LibreOffice generierte PDF zur Browser-Anzeige.")

    class ScanStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CLEAN = "clean", "Clean"
        INFECTED = "infected", "Infected"
        ERROR = "error", "Error"
    scan_status = models.CharField(max_length=20, choices=ScanStatus.choices,
                                    default=ScanStatus.CLEAN,
        help_text="Im MVP immer 'clean' (kein ClamAV). Feld bleibt für Phase 2.")

    class KonvStatus(models.TextChoices):
        NOT_NEEDED = "not_needed", "Nicht nötig"
        PENDING = "pending", "Pending"
        DONE = "done", "Done"
        FAILED = "failed", "Fehlgeschlagen"
    konvertierung_status = models.CharField(max_length=20, choices=KonvStatus.choices,
                                             default=KonvStatus.NOT_NEEDED)

    extrahierter_text = models.TextField(blank=True,
        help_text="Plain-Text für LLM-Quiz-Generierung. Befüllt durch Celery-Task.")
    hochgeladen_am = models.DateTimeField(auto_now_add=True)
    hochgeladen_von = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         on_delete=models.PROTECT)
```

**Größen- und MIME-Limits** (im Serializer-Validator, nicht im Model):

| Typ | MIME-Whitelist | Max-Größe |
|---|---|---|
| pdf | `application/pdf` | 50 MB |
| bild | `image/png`, `image/jpeg` | 10 MB |
| office | `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/vnd.openxmlformats-officedocument.presentationml.presentation` | 50 MB |
| video_upload | `video/mp4` | 500 MB |

### 3.4 `FrageVorschlag` (neu, für S3)

```python
class FrageVorschlag(models.Model):
    """LLM-generierter Quiz-Vorschlag, wartet auf HITL-Bestätigung.
    Nach 'akzeptieren' wird der Vorschlag in eine echte Frage konvertiert.
    """
    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE,
                             related_name="vorschlaege")
    text = models.TextField()
    erklaerung = models.TextField(blank=True)
    optionen = models.JSONField(
        help_text="Liste {text, ist_korrekt} — analog zu AntwortOption, aber im Vorschlag-Stadium")
    quell_module = models.ManyToManyField(KursModul, related_name="basierte_vorschlaege",
        help_text="Aus welchen Modulen wurde dieser Vorschlag generiert?")
    erstellt_am = models.DateTimeField(auto_now_add=True)
    erstellt_von = models.ForeignKey(settings.AUTH_USER_MODEL,
                                      on_delete=models.PROTECT,
                                      related_name="erstellte_vorschlaege")
    llm_modell = models.CharField(max_length=100)
    llm_prompt_hash = models.CharField(max_length=64,
        help_text="SHA-256 des Prompts für Reproduzierbarkeit / Audit.")

    class Status(models.TextChoices):
        OFFEN = "offen", "Offen"
        AKZEPTIERT = "akzeptiert", "Akzeptiert"
        VERWORFEN = "verworfen", "Verworfen"
    status = models.CharField(max_length=20, choices=Status.choices,
                               default=Status.OFFEN)
    entschieden_am = models.DateTimeField(null=True, blank=True)
    entschieden_von = models.ForeignKey(settings.AUTH_USER_MODEL,
                                         null=True, blank=True,
                                         on_delete=models.PROTECT,
                                         related_name="entschiedene_vorschlaege")
    akzeptiert_als = models.ForeignKey(Frage, null=True, blank=True,
                                        on_delete=models.SET_NULL,
        help_text="Bei status=AKZEPTIERT: Verweis auf die daraus erzeugte Frage.")
```

### 3.5 `WelleSnapshot` (neu, für S4)

```python
class WelleSnapshot(models.Model):
    """JSON-Snapshot des kompletten Kurses zum Wellen-Versand-Zeitpunkt.
    Player liest ausschließlich hieraus, niemals aus Live-Kurs.

    Asset-Dateien werden in einen separaten immutable-Pfad kopiert.
    """
    welle = models.OneToOneField(SchulungsWelle, on_delete=models.CASCADE,
                                  related_name="snapshot")
    daten = models.JSONField(
        help_text="Vollständige Struktur: kurs-felder, module (in Reihenfolge), "
                  "fragen + optionen. Self-contained außer Asset-Dateien.")
    asset_pfad_map = models.JSONField(default=dict,
        help_text="{asset_id: snapshot_pfad} — Storage-Pfade der eingefrorenen Dateien.")
    erstellt_am = models.DateTimeField(auto_now_add=True)
```

**Verhalten:** `SchulungsWelle.mark_sent()` ruft zuerst `_create_snapshot()` auf, das:
1. Kurs+Module+Fragen+Optionen in `daten` serialisiert (DRF-Serializer im Snapshot-Format)
2. Pro `KursAsset` der referenzierten Module: Original-Datei + ggf. konvertierte-PDF nach `media/snapshots/welle-<id>/asset-<id>.<ext>` kopiert
3. `asset_pfad_map` befüllt mit den neuen Pfaden
4. Snapshot speichert; danach `mark_sent` setzt Status SENT

Player (`public-schulung.tsx` → `views.PublicSchulungAPI`) liest `welle.snapshot.daten` und löst Asset-URLs gegen `asset_pfad_map` auf. Live-Kurs wird vom Player **nie** angefasst.

### 3.6 ER-Diagramm (Textform)

```
Kurs ──< KursModul (typ-discriminator) ──>? KursAsset
  │                                       (asset bei pdf/bild/office/video_upload)
  ├──< Frage ──< AntwortOption
  ├──< FrageVorschlag (LLM-Draft)
  ├──< KursAsset (alle Assets dieses Kurses)
  └──< SchulungsWelle ──1:1── WelleSnapshot
                          │
                          └──< SchulungsTask ──< QuizAntwort
```

---

## 4. Slice 1 — Kurs-Skelett

**Ziel nach Deploy:** Kunde sieht in `/kurse` einen „+ Neuer Kurs"-Button, kann Kurs anlegen mit allen Settings, in Liste editieren/löschen. Noch kein Inhalt — der Kurs ist als „leer" markiert und kann noch nicht in einer Welle versendet werden.

### 4.1 Backend

- **Migration** `pflichtunterweisung/migrations/00XX_kurs_settings.py`:
  - `Kurs`: neue Felder (`quiz_modus`, `mindest_lesezeit_s`, `zertifikat_aktiv`, `eigentuemer_tenant`, `erstellt_von`)
  - Neue Models `KursAsset`, `FrageVorschlag`, `WelleSnapshot` werden in dieser Migration schon angelegt (leere Tables), damit S2–S4 ohne weitere Schema-Migrations auskommen
- **Serializer** `KursSerializer`: Felder ergänzen, `clean()`-Logik via `validate()`-Methode (z.B. `quiz_modus=kenntnisnahme` → `fragen_pro_quiz` und `min_richtig_prozent` werden auf 0 gesetzt)
- **ViewSet** `KursViewSet`:
  - `list`, `retrieve` bereits da → bleibt
  - `create`, `update`, `partial_update`, `destroy` neu, mit Permission `can_edit_kurs` und Ownership-Check (`eigentuemer_tenant == request.tenant.schema_name`; Standard-Katalog-Kurse mit `eigentuemer_tenant=""` sind nicht editierbar)
  - `delete` weigert sich wenn aktive Welle existiert (`ProtectedError` aus `on_delete=PROTECT` von SchulungsWelle.kurs auf Kurs)
- **AuditLog**: `kurs.created`, `kurs.updated`, `kurs.deleted` automatisch via `core.audit.audit_action`-Decorator (Pattern existiert in Mitarbeiter-ViewSet)

### 4.2 Frontend

- `frontend/src/routes/kurse.tsx`:
  - Button „+ Neuer Kurs" oben rechts → navigiert zu `/kurse/neu`
  - Spalte „Eigentümer" (zeigt „Vaeren-Standard" oder „Eigener Kurs")
  - Edit/Löschen-Icons pro Zeile (nur sichtbar bei eigenen Kursen)
- `frontend/src/routes/kurs-form.tsx` (neu):
  - React-Hook-Form + Zod-Schema
  - Felder: Titel, Beschreibung, `quiz_modus` (Radio: Quiz / Kenntnisnahme / Kenntnisnahme+Lesezeit), bei Lesezeit: `mindest_lesezeit_s`, bei Quiz: `fragen_pro_quiz` + `min_richtig_prozent`, `gueltigkeit_monate`, `zertifikat_aktiv` (Checkbox), `aktiv` (Checkbox)
  - Speichern → Redirect zu `/kurse/<id>` (Detail-Page)
- `kurs-detail.tsx`: kleine Erweiterung — Edit/Löschen-Buttons sichtbar bei eigenen Kursen, Anzeige der neuen Settings (Quiz-Modus etc.)

### 4.3 Tests

- API-Test: tenant kann eigenen Kurs CRUD, kann Standard-Katalog NICHT editieren (HTTP 403)
- API-Test: löschen sperrt wenn aktive Welle hängt
- API-Test: Multi-Tenant-Isolation (Tenant A sieht Kurs von Tenant B nicht)
- Serializer-Test: `clean()`-Logik (Kenntnisnahme-Modus → Quiz-Felder auf 0)
- Storybook: `kurs-form` in den drei Quiz-Modi
- Playwright: KEIN neuer Spec in S1 (kommt erst in S4 als End-to-End)

---

## 5. Slice 2 — Modul-Editor (alle Formate)

**Ziel nach Deploy:** Im Kurs-Detail kann Kunde Module hinzufügen, jeden der 6 Typen, in Reihenfolge bringen (Drag), editieren, löschen. Material wird hochgeladen, scan/konvertiert (LibreOffice für Office), Text wird extrahiert. Mitarbeiter sieht im bestehenden Player schon die neuen Module (bei `quiz_modus=QUIZ` läuft alles wie heute — Player-Erweiterungen für Kenntnisnahme kommen erst in S4).

### 5.1 Backend

- **Serializer** `KursModulSerializer`: neue Felder (`typ`, `inhalt_md`, `youtube_url`, `asset_id`), `validate()` erzwingt Typ-Konsistenz
- **Serializer** `KursAssetSerializer`: read-only Output mit Download-URL (signiert per `core.signed_urls.sign_asset_url`, TTL 60 min, für Mitarbeiter-Player)
- **ViewSet** `KursModulViewSet`: nested unter Kurs (`/api/kurse/<id>/module/`), CRUD mit `can_edit_kurs`-Permission + Ownership-Check
- **ViewSet** `KursAssetViewSet`: Upload-Endpoint `POST /api/kurse/<id>/assets/`, akzeptiert multipart, validiert MIME+Größe, speichert Asset, triggert ggf. Celery-Tasks (`convert_office_to_pdf`, `extract_text_from_asset`)
- **Endpoint** für Reorder: `POST /api/kurse/<id>/module/reorder/` mit Body `[modul_id1, modul_id2, ...]`, atomar in Transaction
- **Celery-Task** `tasks.convert_office_to_pdf(asset_id)`:
  - subprocess-Aufruf an LibreOffice-Sidecar-Container (`docker exec libreoffice soffice --headless --convert-to pdf ...`)
  - Schreibt Ergebnis in `asset.konvertierte_pdf`, setzt Status DONE/FAILED
- **Celery-Task** `tasks.extract_text_from_asset(asset_id)`:
  - PDF → `pypdf.PdfReader.extract_text()` über alle Seiten
  - Office → erst konvertierte PDF abwarten (chord/group), dann wie PDF
  - Bild → kein OCR, `extrahierter_text=""` (leer ist OK, LLM-Vorschlag überspringt diese Module später)
  - Video-Upload → kein Whisper, `extrahierter_text=""`
  - YouTube → `youtube-transcript-api`-Aufruf, deutsche Untertitel bevorzugt, sonst englisch, sonst leer. Ergebnis nach `KursModul.transcript_cache` (nicht in KursAsset, da YouTube-Module kein Asset haben). Separater Celery-Task `extract_youtube_transcript(modul_id)`, wird beim Speichern eines YouTube-Moduls getriggert.
- **Anti-Pattern-Guard:** Modul-Lösch-Endpoint löscht das verknüpfte Asset nur, wenn kein anderes Modul (oder Snapshot) darauf verweist (`on_delete=PROTECT` macht das hart).

### 5.2 Infrastruktur

- **Neuer Sidecar-Service** in `infrastructure/docker-compose.yml`:
  ```yaml
  libreoffice:
    image: linuxserver/libreoffice:latest
    container_name: vaeren-libreoffice
    volumes:
      - vaeren-media:/media
    networks:
      - vaeren-net
    restart: unless-stopped
  ```
  Image ist ~1 GB — vertretbar, läuft idle ohne CPU/RAM-Druck. Celery-Worker ruft via `docker exec` ins gleiche Volume.
- **Caddy-Routing** für Media-Dateien: `app.vaeren.de/media/*` → Django serviert (intern existing pattern). Signierte URLs verhindern Direkt-Download ohne Login.

### 5.3 Frontend

- `kurs-detail.tsx`: neuer Tab/Block „Module" mit Liste + „+ Modul hinzufügen"
- `frontend/src/components/kurs-modul-form.tsx` (neu): Wizard-artige Auswahl
  - Schritt 1: Typ wählen (6 Kacheln mit Icons)
  - Schritt 2: typ-spezifische Felder:
    - TEXT → `@uiw/react-md-editor` (split-pane Markdown), Titel-Input darüber
    - PDF/BILD/OFFICE/VIDEO_UPLOAD → `react-dropzone`-Drop-Area, Upload-Progress, Preview nach Upload (PDF: `react-pdf`; Bild: `<img>`; Office: PDF-Preview der konvertierten Datei; Video: HTML5 `<video>`)
    - VIDEO_YOUTUBE → URL-Input mit Live-Embed-Preview
- `frontend/src/components/modul-liste.tsx` (neu): `@dnd-kit/core` für vertikales Drag-Reorder, Save bei Drop via `reorder`-Endpoint
- **WebSocket nicht nötig** — Upload-Progress über `axios onUploadProgress`; Konvertierungs-Status via React-Query-Polling alle 2s bis Status terminal

### 5.4 Tests

- API-Test: Upload-Pipeline mit gemockter LibreOffice (mock `subprocess.run`)
- API-Test: MIME-Whitelist greift (text/plain → 400)
- API-Test: Reorder-Endpoint atomar (bei Fehler kein partieller State)
- API-Test: Modul-Typ-Konsistenz (`clean()`)
- API-Test: Text-Extraktion (Fixture-PDF mit bekanntem Text → assertion)
- API-Test: Tenant A kann kein Asset von Tenant B downloaden (signierte URL ist tenant-bound)
- Storybook: `kurs-modul-form` pro Typ
- Storybook: `modul-liste` mit Drag-Interaction
- Playwright: Smoke „Upload PDF → erscheint in Modul-Liste"

### 5.5 LibreOffice-Konvertierungs-Tradeoff

LibreOffice-Sidecar bringt ~1 GB Image + 200-400 MB RAM-Idle. Alternative wäre eine externe Konvertierungs-API (cloudconvert.com), aber: Daten verlassen EU, Kosten, Vendor-Lock. **Entscheidung: Sidecar.** Wenn der RAM-Footprint auf CAX31 zum Problem wird (heute 16 GB, viel Headroom), kann man später auf On-Demand-Container-Start umstellen.

---

## 6. Slice 3 — Quiz-Pool + LLM-Vorschlag

**Ziel nach Deploy:** Im Kurs-Detail kann Kunde Fragen manuell anlegen (wie heute via Django-Admin, jetzt im UI) UND einen „Fragen aus Material vorschlagen lassen"-Button drücken. LLM (Reasoning-Modell) liest `extrahierter_text` aller Module, schlägt Fragen vor (Vorschlag-Tabelle), Kunde reviewt jeden Vorschlag (Akzeptieren / Ändern / Verwerfen), Akzeptierte werden zu echten `Frage`-Einträgen.

### 6.1 Backend

- **Serializer** `FrageSerializer` + `AntwortOptionSerializer`: bestehen schon (read in `kurs-detail.tsx`), brauchen Write-Endpoints
- **ViewSet** `FrageViewSet`: nested unter Kurs, CRUD mit `can_edit_kurs`. AntwortOptionen nested als JSON-Array im Frage-Body (`optionen: [{text, ist_korrekt, reihenfolge}]`)
- **ViewSet** `FrageVorschlagViewSet`:
  - `POST /api/kurse/<id>/vorschlaege/generieren/` → triggert Celery-Task, Response 202 mit Job-ID; Frontend polled
  - `GET /api/kurse/<id>/vorschlaege/` → Liste offener Vorschläge
  - `POST /api/vorschlaege/<id>/akzeptieren/` → erzeugt `Frage`+`AntwortOption`-Einträge in einer Transaction, setzt Vorschlag-Status AKZEPTIERT
  - `POST /api/vorschlaege/<id>/verwerfen/` → Status VERWORFEN
  - PATCH-Endpoint zum Editieren des Vorschlags vor Akzeptanz
- **Celery-Task** `tasks.generiere_fragen_vorschlaege(kurs_id, user_id, anzahl=10)`:
  1. Sammle Lehrtext aus allen Modulen via Helper `_modul_text(modul)`:
     - TEXT → `modul.inhalt_md`
     - PDF/OFFICE → `modul.asset.extrahierter_text`
     - VIDEO_YOUTUBE → `modul.transcript_cache`
     - BILD / VIDEO_UPLOAD → leer (kein OCR/Whisper im MVP)
  2. Wenn leer → Fehler an User („Bitte erst Material mit Text hochladen")
  3. Prompt-Template:
     ```
     Du bist Lehr-Designer für eine Pflichtunterweisung mittelständischer Industrie-MA.
     Auf Basis des folgenden Lern-Materials erstelle {anzahl} Single-Choice-Quiz-Fragen.

     KRITISCH (RDG-Layer-1):
     - Verwende Vorschlags-Sprache, keine rechtsverbindlichen Formulierungen
     - Keine Phrasen wie "Sie müssen", "ist verpflichtend laut Gesetz §..."
     - Jede Frage hat 4 Optionen, genau 1 ist korrekt
     - Erklärung pro Frage in 1-2 Sätzen, warum die richtige Antwort richtig ist

     Material:
     ---
     {text}
     ---

     Antworte als JSON-Array: [{"text": "...", "optionen": [{"text": "...", "ist_korrekt": true}, ...], "erklaerung": "..."}, ...]
     ```
  4. Modell: `OPENROUTER_MODEL_REASONING` (nvidia/nemotron-3-super-120b-a12b:free)
  5. Output durch `core.llm_validator.validate_output()` (RDG-Layer-2) gegen verbotene Phrasen
  6. Parse JSON, lege `FrageVorschlag`-Einträge an, verknüpfe `quell_module`
  7. Notifikation an User „N Vorschläge bereit zur Review" (über bestehendes Notification-System)

### 6.2 Frontend

- `frontend/src/routes/kurs-detail.tsx`: neuer Tab „Fragen-Pool"
  - Liste bestehender Fragen mit Inline-Edit + Löschen
  - Button „+ Frage manuell anlegen" → `frage-form.tsx`
  - Button „Vorschläge aus Material generieren" (disabled wenn kein Modul mit Text vorhanden)
  - Bei laufender Generierung: Spinner + Status-Text („LLM denkt … Modell: Nemotron-120B")
- `frontend/src/routes/vorschlaege-review.tsx` (neu):
  - Listet offene Vorschläge eines Kurses, einer pro Card
  - Pro Card: Frage-Text + Optionen (korrekte grün), Erklärung, Quell-Module-Badges
  - 3 Buttons: „Akzeptieren wie ist", „Ändern dann akzeptieren" (öffnet Inline-Editor), „Verwerfen"
  - Banner oben: „Vorschläge sind LLM-generiert. Sie prüfen jeden Vorschlag, bevor er produktiv wird (RDG-Layer-3)."

### 6.3 RDG-Layer-Anwendung

- **Layer 1 (Prompt):** explizite Vorschlags-Sprache erzwingen (siehe Template oben)
- **Layer 2 (Output-Validator):** `core/llm_validator.py::validate_output()` filtert verbotene Phrasen; bei Treffer wird der Vorschlag **nicht** persistiert, sondern ein Audit-Log-Eintrag erzeugt und User informiert „Vorschlag hat Compliance-Check nicht bestanden, bitte manuell anlegen"
- **Layer 3 (HITL):** Mensch-Bestätigungs-Gate vor Promotion zu `Frage`. Auto-Promotion ist code-mäßig nicht möglich (separater Endpoint, kein Ein-Klick-Bulk-Akzeptieren im MVP — bewusst, um Click-Through-Müdigkeit zu vermeiden)

### 6.4 Tests

- API-Test: Generieren-Endpoint mit gemocktem LLM-Response (responses-lib), assert Vorschläge angelegt
- API-Test: Vorschlag mit verbotener Phrase → wird verworfen, AuditLog-Eintrag
- API-Test: Akzeptieren-Endpoint atomar (Frage+Optionen in einer Transaction)
- API-Test: Verwerfen löscht keine Daten (Audit-Trail bleibt)
- API-Test: Tenant kann nur eigene Vorschläge sehen
- Storybook: `vorschlaege-review` mit 3 Beispiel-Cards
- Playwright: KEIN neuer Spec in S3 (kommt in S4)

---

## 7. Slice 4 — Welle-Snapshot + Player-Modi

**Ziel nach Deploy:** Welle versenden → Snapshot. Mitarbeiter-Player respektiert `quiz_modus` (Quiz / Kenntnisnahme / Kenntnisnahme+Lesezeit), Zertifikat-Generierung respektiert `zertifikat_aktiv`. Standard-Kurse aus Seed-Katalog (alle `quiz_modus=QUIZ`, `zertifikat_aktiv=True`) verhalten sich identisch zu heute — keine Regression.

### 7.1 Backend

- **Method** `SchulungsWelle.mark_sent()` erweitern: erzeugt `WelleSnapshot` (siehe §3.5) BEVOR Status auf SENT geht, in einer Transaction
- **Helper** `pflichtunterweisung/snapshots.py::create_snapshot(welle)`:
  - DRF-Serializer mit allen Modul-Inhalten (inkl. `inhalt_md`, `youtube_url`, Asset-Referenzen) und Frage-Pool
  - File-Copy für Assets: `shutil.copy2(asset.original_datei.path, snapshot_path)`, gleich für `konvertierte_pdf`
  - `asset_pfad_map` mit Relative-Pfaden (für portable Backups)
- **View** `PublicSchulungAPI` (existing für Public-Quiz):
  - Liest jetzt aus `welle.snapshot.daten` statt aus `welle.kurs`
  - Asset-URLs werden über `asset_pfad_map` aufgelöst (signed URLs gegen snapshot-Pfade)
- **View** `PublicSchulungAbschlussAPI`:
  - Bei `quiz_modus=QUIZ`: bestehende Logik (Antworten auswerten, Bestehensgrenze)
  - Bei `quiz_modus=KENNTNISNAHME`: nur Validierung dass alle Module „besucht" wurden (Frontend trackt + sendet `besuchte_module: [ids]`)
  - Bei `quiz_modus=KENNTNISNAHME_LESEZEIT`: zusätzlich serverseitige Mindest-Zeit-Validierung (`abgeschlossen_am - gestartet_am >= mindest_lesezeit_s * len(snapshot.daten["module"])`, d.h. Mindest-Lesezeit pro Modul × Anzahl Module im Snapshot)
- **PDF-Generator** `pdf.py::generate_zertifikat`: prüft `snapshot.daten["zertifikat_aktiv"]`; wenn False, gibt None zurück, Abschluss-Screen zeigt keinen Download-Button
- **Migration:** Bestandsdaten — bei allen bereits SENT-Wellen ohne Snapshot wird ein „retro-Snapshot" aus dem aktuellen Kurs-Stand erzeugt (Backfill-Skript in der Migration). Risiko: wenn der Kurs in der Zwischenzeit editiert wurde, ist der Snapshot nicht historisch korrekt — aber bei den 1-2 Demo-Wellen unkritisch. Dokumentiert als „best effort backfill für Bestandswellen".

### 7.2 Frontend

- `frontend/src/routes/public-schulung.tsx`: erweitern mit Modus-Switch
  - Quiz-Modus: bestehende UI
  - Kenntnisnahme: Module sequentiell, „Weiter"-Button, am Ende „Ich habe das gelesen und verstanden"-Button
  - Kenntnisnahme+Lesezeit: zusätzlich Countdown-Timer pro Modul, „Weiter" disabled bis Timer abgelaufen; Visibility-API pausiert Timer bei Tab-Wechsel (anti-cheat)
- Asset-Rendering im Player:
  - PDF: `react-pdf` (gleiche Lib wie im Editor)
  - Bild: `<img>`
  - Office: PDF-Preview der konvertierten Datei
  - Video-Upload: HTML5 `<video controls>`
  - YouTube: standard Embed-iframe
- Abschluss-Screen: zeigt Download-Button für Zertifikat nur wenn `zertifikat_aktiv`

### 7.3 Tests

- API-Test: Snapshot ist immutable — nach Versand Edit am Kurs ändert nichts an Welle (Player gibt alte Inhalte zurück)
- API-Test: Snapshot kopiert Asset-Dateien korrekt
- API-Test: Player bei `quiz_modus=KENNTNISNAHME` akzeptiert Abschluss ohne Quiz-Antworten
- API-Test: Mindest-Lesezeit-Check serverseitig (zu schneller Abschluss → 400)
- API-Test: Zertifikat-Generator gibt None bei `zertifikat_aktiv=False`
- API-Test: Multi-Tenant — Tenant A kann keinen Snapshot von Tenant B abrufen
- Storybook: Player in allen 3 Modi
- **Playwright (neu, auf main):** `tenant-erstellt-eigenen-kurs.spec.ts` — kompletter Flow Login → Kurs anlegen → Modul (Markdown + PDF + YouTube) hinzufügen → Quiz-Vorschlag generieren (gemockt) → akzeptieren → Welle anlegen → versenden → öffentlicher Player → Abschluss → Zertifikat

---

## 8. Architektur-Entscheidungen

| Entscheidung | Begründung |
|---|---|
| Modul-Discriminator statt CustomEditor-Node (TipTap) | Variante-C-Pragmatismus: Solo-Builder-Aufwand minimieren, jeder Modul-Typ ist eigenständig testbar. TipTap kann später nachgerüstet werden ohne Datenmodell-Bruch. |
| `FrageVorschlag` separate Tabelle (statt `Frage.draft=True`) | Live-`Frage` bleibt invariant „production-ready". Vorschlag-Audit-Trail (Modell, Prompt-Hash, Entscheider) ohne Polluting der Live-Daten. |
| `WelleSnapshot` als JSONField (statt voll-relationale Snapshot-Tabellen) | Snapshot ist read-only und self-contained; relationaler Snapshot würde Modell-Duplikation erzwingen. JSON-Snapshot ist robust gegen künftige Schema-Änderungen. |
| Asset-Dateien beim Snapshot **kopieren** (nicht referenzieren) | Garantiert Immutability: Snapshot bleibt valide auch wenn Kunde später Asset im Live-Kurs löscht. Storage-Kosten vertretbar (Welle ~50–200 MB). |
| LibreOffice als Sidecar-Container | EU-Datenhaltung, keine externe Abhängigkeit, kein Vendor-Lock. RAM-Footprint akzeptabel. |
| Kein ClamAV im MVP | Schema-Isolation begrenzt Blast-Radius auf eigenen Tenant. MIME-Whitelist + Size-Limit + Snapshot-Audit-Trail als Mehrschicht-Verteidigung. `scan_status`-Feld vorhanden für Phase 2. |
| Kein OCR/Whisper im MVP | Komplexität vs. MVP-Nutzen: Kunde kann YouTube-Untertitel oder Text-Modul daneben legen. |
| Reasoning-Modell für Quiz-Vorschlag | Quiz-Generation ist schwierig (4 plausible Distraktoren + 1 korrekt + erklärbar). Fast-Modell produziert zu generische/falsche Fragen. |
| Polling statt WebSocket für Status-Updates | Wir haben kein WebSocket-Setup; React-Query-Polling alle 2s reicht für 30-60s Konvertierungen + LLM-Calls. |
| Kein Bulk-Akzeptieren von Vorschlägen | HITL-Gate ernst nehmen (RDG-Layer-3) — Klick-Müdigkeit darf nicht zu Auto-Approval-Verhalten verleiten. |

---

## 9. Test-Strategie & CI-Gates

Pro Slice gilt das 4-Schichten-Setup aus CLAUDE.md:

1. **API-Integration-Tests**: pytest-django mit `responses` für LLM-Mock, `unittest.mock.patch` für `subprocess.run` (LibreOffice). Ziel: 90 % Branch-Coverage in Business-Logik der jeweiligen Slice. `--cov-fail-under=80` bleibt global, neues Modul muss diese Schwelle nicht senken.
2. **OpenAPI-Schema-Sync**: `make schema` muss nach jedem Slice ohne Diff in main durchlaufen; CI-Job `schema-sync` schlägt sonst fehl.
3. **Storybook + Interaction-Tests**: pro neuem Komponent (Form, Liste, Player-Mode) ein Story-File. CI-Job rendert headless via Playwright-CT.
4. **Playwright E2E**: ein neuer Spec in S4 (siehe §7.3), nur auf main-Branch ausgeführt.

**Kritische Tests, die nicht fehlen dürfen** (sonst CI-Fail):

- Multi-Tenant-Isolation für jeden neuen Endpoint (Standard-Test-Helper `assert_tenant_isolation` aus `core/tests/conftest.py`)
- Welle-Snapshot-Immutability-Test (S4)
- RDG-Layer-2-Output-Validator-Test mit Sample „verboten" + Sample „erlaubt" (S3)
- LLM-Mock — niemals echter Call in Tests (siehe CLAUDE.md Anti-Patterns)

---

## 10. Migration & Deployment

Pro Slice:

1. Migration generieren (`make migrations`), Review-Diff
2. Lokal `make test` grün
3. Lokal `make schema` ohne Diff
4. Commit + Push (Vaeren erlaubt Direkt-Merge nach main, kein PR — siehe Memory `feedback_merge_to_main`)
5. `./deploy.sh` von Konrads Laptop
6. Smoke-Check via Live-Demo-Tenant: das in dieser Slice neu hinzugekommene Feature manuell durchspielen
7. **Slice gilt erst als „abgeschlossen", wenn alle 6 Punkte erledigt sind** (Feature-Completion-Discipline aus CLAUDE.md)

**Reihenfolge zwingend:** S1 → S2 → S3 → S4. Kein paralleles Arbeiten an mehreren Slices.

**Backwards-Compat-Check vor jedem Deploy:**
- Standard-Katalog-Kurse (`eigentuemer_tenant=""`) bleiben lesbar
- Bestehende Wellen funktionieren weiter
- `seed_kurs_katalog`-Command läuft ohne Fehler

---

## 11. Risiken & Mitigations

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|---|---|---|---|
| LibreOffice-Konvertierung scheitert bei exotischen PPTX | Mittel | Niedrig (User sieht Fehler-Status, kann PDF stattdessen hochladen) | Klare Fehler-Meldung, Re-Upload als PDF als Workaround |
| LLM-Quiz-Vorschläge inhaltlich falsch | Mittel-Hoch | Mittel (User merkt's beim HITL-Review) | Layer-3-HITL erzwingt manuelle Bestätigung, keine Bulk-Aktion, „Verwerfen" hat keine Strafkosten |
| Storage-Volumen explodiert bei Video-Uploads | Mittel | Mittel | 500 MB Limit pro Asset, Cron-Job warnt bei `vaeren-media >5 GB` (separater Sub-Spec später) |
| Snapshot-Backfill verfälscht historische Wellen | Niedrig (nur 1-2 Demo-Wellen) | Niedrig | Dokumentiert als „best effort", in echtem Pilot-Betrieb haben alle Wellen Snapshots ab S4-Deploy |
| MIME-Spoofing umgeht Whitelist | Niedrig | Niedrig (Schema-isoliert) | Python-Magic (libmagic) zusätzlich zur Browser-MIME-Angabe |
| dnd-kit-Bugs bei Touch-Devices | Mittel | Niedrig (Editor primär Desktop) | Mobile-Sperre auf Editor-Routes („Bitte am PC nutzen"-Banner) |

---

## 12. Offene Punkte für künftige Phasen (nicht MVP)

- ClamAV-Sidecar für Virus-Scan, `scan_status`-Pipeline aktivieren
- Whisper-Transkription für Video-Uploads → ermöglicht LLM-Quiz auch aus Video
- OCR (Tesseract) für Bild-Module
- Kurs-Klonen aus Standard-Katalog (Convenience)
- Public-Kurs-Bibliothek (Cross-Tenant-Sharing)
- TipTap-Editor wenn Pilot mehr Polish fordert
- HLS-Streaming für große Videos
- Bulk-Aktionen auf Vorschlag-Review (mit zusätzlichem Confirm-Step, um Click-Through-Müdigkeit zu verhindern)

---

## 13. Akzeptanz-Kriterien (gesamt)

Das Feature gilt als abgeschlossen, wenn:

- [ ] Alle 4 Slices nach §10 deployed sind
- [ ] Demo-Tenant hat mindestens 1 eigenen Kurs aller 6 Modul-Typen
- [ ] Eine Demo-Welle eines eigenen Kurses ist erfolgreich von einem Demo-Mitarbeiter durchlaufen
- [ ] LLM-Vorschlag wurde an mindestens 1 PDF erfolgreich getestet (manueller Review)
- [ ] Zertifikat-aus / Quiz-aus-Pfad wurde an einem Demo-Kurs verifiziert
- [ ] Playwright-E2E-Spec aus §7.3 läuft auf main grün
- [ ] CI-Gate `--cov-fail-under=80` bleibt grün
- [ ] OpenAPI-Schema-Sync bleibt grün
- [ ] Backup-Restore-Test (restic) zeigt, dass `vaeren-media` und Snapshot-Files konsistent restauriert werden
