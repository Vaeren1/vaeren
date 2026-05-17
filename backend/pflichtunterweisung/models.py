"""Pflichtunterweisungs-Modul. Sprint 4 (Spec §12).

Datenmodell pro Spec §5 + Sprint-4-Plan §2:
- Kurs (Vorlage), KursModul (Lerninhalt), Frage + AntwortOption (Single-Choice-Quiz)
- SchulungsWelle (Roll-Out an n Mitarbeiter), SchulungsTask (= ein Mitarbeiter x eine Welle, polymorph aus ComplianceTask)
- QuizAntwort (eine Antwort pro Frage je Task)
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import ComplianceTask, Mitarbeiter


class Kurs(models.Model):
    """Kurs-Vorlage. Mehrfach in Wellen verwendbar."""

    class QuizModus(models.TextChoices):
        QUIZ = "quiz", "Quiz"
        KENNTNISNAHME = "kenntnisnahme", "Kenntnisnahme"
        KENNTNISNAHME_LESEZEIT = "kenntnisnahme_lesezeit", "Kenntnisnahme + Min-Lesezeit"

    class Kategorie(models.TextChoices):
        ARBEITSSCHUTZ = "arbeitsschutz", "Arbeitsschutz"
        BRANDSCHUTZ = "brandschutz", "Brand- & Erste Hilfe"
        GEFAHRSTOFFE = "gefahrstoffe", "Gefahrstoffe & Maschinen"
        DATENSCHUTZ = "datenschutz", "Datenschutz & IT"
        COMPLIANCE = "compliance", "Compliance & Recht"
        UMWELT = "umwelt", "Umwelt & Qualität"
        SONSTIGES = "sonstiges", "Sonstiges"

    titel = models.CharField(max_length=200)
    beschreibung = models.TextField(blank=True)
    gueltigkeit_monate = models.PositiveSmallIntegerField(
        default=12, help_text="Wie lange ist das Zertifikat gültig?"
    )
    min_richtig_prozent = models.PositiveSmallIntegerField(
        default=80, help_text="Bestehensschwelle (Prozent richtig)"
    )
    fragen_pro_quiz = models.PositiveSmallIntegerField(
        default=10,
        help_text=(
            "Anzahl Fragen pro Quiz-Durchlauf, zufällig aus fragen-Pool gezogen "
            "und pro SchulungsTask persistiert. Muss <= fragen.count() sein."
        ),
    )
    quiz_modus = models.CharField(
        max_length=30,
        choices=QuizModus.choices,
        default=QuizModus.QUIZ,
        help_text="Bestimmt, was der Mitarbeiter im Player macht.",
    )
    mindest_lesezeit_s = models.PositiveIntegerField(
        default=0,
        help_text=(
            "Sekunden pro Modul, ab denen 'Kenntnisnahme' aktivierbar ist. "
            "Nur ausgewertet bei quiz_modus=kenntnisnahme_lesezeit."
        ),
    )
    zertifikat_aktiv = models.BooleanField(
        default=True,
        help_text="Wenn False, wird bei Abschluss kein PDF-Zertifikat generiert.",
    )
    kategorie = models.CharField(
        max_length=30,
        choices=Kategorie.choices,
        default=Kategorie.SONSTIGES,
        help_text="Thematische Einordnung fuer die Kurs-Bibliothek-Gruppierung.",
    )
    eigentuemer_tenant = models.CharField(
        max_length=63,
        blank=True,
        help_text=(
            "Schema-Name des Tenants, der den Kurs erstellt hat. "
            "Leer = Vaeren-Standardkatalog (read-only für Tenants)."
        ),
    )
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="erstellte_kurse",
    )
    aktiv = models.BooleanField(default=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-erstellt_am",)
        verbose_name = "Kurs"
        verbose_name_plural = "Kurse"

    def __str__(self) -> str:
        return self.titel

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.quiz_modus != self.QuizModus.QUIZ:
            if self.fragen_pro_quiz != 0:
                raise ValidationError(
                    {"fragen_pro_quiz": "Muss 0 sein wenn quiz_modus != quiz."}
                )
            if self.min_richtig_prozent != 0:
                raise ValidationError(
                    {"min_richtig_prozent": "Muss 0 sein wenn quiz_modus != quiz."}
                )
        if (
            self.quiz_modus == self.QuizModus.KENNTNISNAHME_LESEZEIT
            and self.mindest_lesezeit_s <= 0
        ):
            raise ValidationError(
                {"mindest_lesezeit_s": "Muss > 0 sein wenn quiz_modus=kenntnisnahme_lesezeit."}
            )

    @property
    def ist_standardkatalog(self) -> bool:
        return self.eigentuemer_tenant == ""


class KursModul(models.Model):
    """Lerninhalt-Block in einem Kurs.

    Discriminator-Pattern: `typ` bestimmt, welche Felder gefuellt sind.
    Slice 2a: nur TEXT/Markdown. 2b+: pdf, bild, office, video_upload,
    video_youtube via KursAsset oder youtube_url.
    """

    class Typ(models.TextChoices):
        TEXT = "text", "Text/Markdown"
        PDF = "pdf", "PDF"
        BILD = "bild", "Bild (PNG/JPG)"
        OFFICE = "office", "Office (DOCX/PPTX)"
        VIDEO_UPLOAD = "video_upload", "Video-Upload"
        VIDEO_YOUTUBE = "video_youtube", "YouTube-Embed"

    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE, related_name="module")
    titel = models.CharField(max_length=200)
    reihenfolge = models.PositiveSmallIntegerField(default=0)
    typ = models.CharField(
        max_length=20, choices=Typ.choices, default=Typ.TEXT,
        help_text="Modul-Typ — bestimmt welches Inhalts-Feld gefuellt ist.",
    )
    inhalt_md = models.TextField(
        blank=True,
        help_text="Markdown-Lerninhalt. Befuellt nur bei typ=TEXT.",
    )
    youtube_url = models.URLField(
        blank=True,
        help_text="YouTube-Watch-URL. Befuellt nur bei typ=VIDEO_YOUTUBE.",
    )
    asset = models.ForeignKey(
        "KursAsset", null=True, blank=True, on_delete=models.PROTECT,
        related_name="module",
        help_text="Datei-Asset. Befuellt bei pdf/bild/office/video_upload.",
    )
    transcript_cache = models.TextField(
        blank=True,
        help_text=(
            "Cache fuer YouTube-Untertitel oder Audio-Transkript "
            "(spaeter via youtube-transcript-api). Nur fuer LLM-Quiz."
        ),
    )

    class Meta:
        ordering = ("reihenfolge", "id")
        unique_together = (("kurs", "reihenfolge"),)
        verbose_name = "Kurs-Modul"
        verbose_name_plural = "Kurs-Module"

    def __str__(self) -> str:
        return f"{self.kurs.titel} / {self.titel}"

    def clean(self) -> None:
        from django.core.exceptions import ValidationError

        if self.typ == self.Typ.TEXT:
            if not (self.inhalt_md or "").strip():
                raise ValidationError({"inhalt_md": "Pflicht bei typ=text."})
            if self.asset_id or self.youtube_url:
                raise ValidationError(
                    "Bei typ=text duerfen asset und youtube_url nicht gesetzt sein."
                )
        elif self.typ == self.Typ.VIDEO_YOUTUBE:
            if not self.youtube_url:
                raise ValidationError({"youtube_url": "Pflicht bei typ=video_youtube."})
            if self.asset_id or (self.inhalt_md or "").strip():
                raise ValidationError(
                    "Bei typ=video_youtube duerfen asset und inhalt_md nicht gesetzt sein."
                )
        else:  # pdf, bild, office, video_upload
            if not self.asset_id:
                raise ValidationError({"asset": f"Pflicht bei typ={self.typ}."})
            if self.youtube_url or (self.inhalt_md or "").strip():
                raise ValidationError(
                    f"Bei typ={self.typ} duerfen youtube_url und inhalt_md nicht gesetzt sein."
                )


class KursAsset(models.Model):
    """Datei-Asset, das von KursModul referenziert wird.

    Slice 2a: leere Tabelle, kein Upload-Endpoint. 2b+ aktivieren das.
    """

    class ScanStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CLEAN = "clean", "Clean"
        INFECTED = "infected", "Infected"
        ERROR = "error", "Error"

    class KonvStatus(models.TextChoices):
        NOT_NEEDED = "not_needed", "Nicht noetig"
        PENDING = "pending", "Pending"
        DONE = "done", "Done"
        FAILED = "failed", "Fehlgeschlagen"

    class CompressionStatus(models.TextChoices):
        NOT_NEEDED = "not_needed", "Nicht noetig"
        PENDING = "pending", "Pending"
        DONE = "done", "Done"
        SKIPPED = "skipped", "Skipped (kein Gewinn)"
        FAILED = "failed", "Fehlgeschlagen"

    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE, related_name="assets")
    original_datei = models.FileField(upload_to="kurs-uploads/%Y/%m/")
    original_mime = models.CharField(max_length=100)
    original_size_bytes = models.PositiveBigIntegerField()
    konvertierte_pdf = models.FileField(
        upload_to="kurs-uploads/%Y/%m/", blank=True, null=True,
        help_text="Bei typ=office: LibreOffice-konvertierte PDF zur Browser-Anzeige.",
    )
    scan_status = models.CharField(
        max_length=20, choices=ScanStatus.choices, default=ScanStatus.CLEAN,
        help_text="Im MVP immer 'clean'. Feld bleibt fuer Phase 2 (ClamAV).",
    )
    konvertierung_status = models.CharField(
        max_length=20, choices=KonvStatus.choices, default=KonvStatus.NOT_NEEDED,
    )
    compression_status = models.CharField(
        max_length=20, choices=CompressionStatus.choices, default=CompressionStatus.NOT_NEEDED,
    )
    compressed_size_bytes = models.PositiveBigIntegerField(null=True, blank=True)
    extrahierter_text = models.TextField(
        blank=True,
        help_text="Plain-Text fuer LLM-Quiz-Generierung (Slice 3).",
    )
    hochgeladen_am = models.DateTimeField(auto_now_add=True)
    hochgeladen_von = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="hochgeladene_assets",
    )

    class Meta:
        ordering = ("-hochgeladen_am",)
        verbose_name = "Kurs-Asset"
        verbose_name_plural = "Kurs-Assets"

    def __str__(self) -> str:
        kb = self.original_size_bytes // 1024
        return f"Asset #{self.pk} ({self.original_mime}, {kb} KB)"


class Frage(models.Model):
    """Single-Choice-Quiz-Frage zu einem Kurs."""

    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE, related_name="fragen")
    text = models.TextField()
    erklaerung = models.TextField(blank=True, help_text="Erklärung nach Beantwortung")
    reihenfolge = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("reihenfolge", "id")
        verbose_name = "Frage"
        verbose_name_plural = "Fragen"

    def __str__(self) -> str:
        return self.text[:60]


class AntwortOption(models.Model):
    """Eine von 2-6 Antwort-Optionen einer Frage. Genau eine ist korrekt."""

    frage = models.ForeignKey(Frage, on_delete=models.CASCADE, related_name="optionen")
    text = models.CharField(max_length=300)
    ist_korrekt = models.BooleanField(default=False)
    reihenfolge = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("reihenfolge", "id")
        verbose_name = "Antwort-Option"
        verbose_name_plural = "Antwort-Optionen"

    def __str__(self) -> str:
        marker = "[x]" if self.ist_korrekt else "[ ]"
        return f"{marker} {self.text}"


class FrageVorschlag(models.Model):
    """LLM-generierter Quiz-Vorschlag, wartet auf HITL-Bestaetigung (RDG-Layer-3).

    Slice 3: Akzeptierte Vorschlaege werden zu echten Frage-Eintraegen
    konvertiert. Verworfene bleiben als Audit-Trail bestehen.
    """

    class Status(models.TextChoices):
        OFFEN = "offen", "Offen"
        AKZEPTIERT = "akzeptiert", "Akzeptiert"
        VERWORFEN = "verworfen", "Verworfen"

    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE, related_name="vorschlaege")
    text = models.TextField()
    erklaerung = models.TextField(blank=True)
    optionen = models.JSONField(
        help_text="Liste {text, ist_korrekt} — analog zu AntwortOption.",
    )
    quell_module = models.ManyToManyField(
        KursModul, blank=True, related_name="basierte_vorschlaege",
        help_text="Aus welchen Modulen wurde dieser Vorschlag generiert?",
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="erstellte_vorschlaege",
    )
    llm_modell = models.CharField(max_length=100)
    llm_prompt_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 des Prompts fuer Reproduzierbarkeit / Audit.",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OFFEN,
    )
    entschieden_am = models.DateTimeField(null=True, blank=True)
    entschieden_von = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name="entschiedene_vorschlaege",
    )
    akzeptiert_als = models.ForeignKey(
        "Frage", null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Bei status=AKZEPTIERT: Verweis auf die erzeugte Frage.",
    )

    class Meta:
        ordering = ("-erstellt_am",)
        verbose_name = "Fragen-Vorschlag"
        verbose_name_plural = "Fragen-Vorschlaege"


class SchulungsWelleStatus(models.TextChoices):
    DRAFT = "draft", "Entwurf"
    SENT = "sent", "Versendet"
    IN_PROGRESS = "in_progress", "In Bearbeitung"
    COMPLETED = "completed", "Abgeschlossen"


class SchulungsWelle(models.Model):
    """Konkreter Roll-Out eines Kurses an n Mitarbeiter."""

    kurs = models.ForeignKey(Kurs, on_delete=models.PROTECT, related_name="wellen")
    titel = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=SchulungsWelleStatus.choices,
        default=SchulungsWelleStatus.DRAFT,
    )
    deadline = models.DateField()
    einleitungs_text = models.TextField(
        blank=True,
        help_text="Optionaler personalisierter Einleitungstext (LLM-Vorschlag, HITL-bestätigt)",
    )
    erstellt_von = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="erstellte_wellen",
    )
    erstellt_am = models.DateTimeField(auto_now_add=True)
    versendet_am = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-erstellt_am",)
        verbose_name = "Schulungs-Welle"
        verbose_name_plural = "Schulungs-Wellen"

    def __str__(self) -> str:
        return f"{self.titel} ({self.kurs.titel}, {self.get_status_display()})"

    def mark_sent(self) -> None:
        """State-Transition DRAFT -> SENT."""
        if self.status != SchulungsWelleStatus.DRAFT:
            raise ValueError(f"Welle {self.pk} ist nicht im Status DRAFT (aktuell: {self.status})")
        self.status = SchulungsWelleStatus.SENT
        self.versendet_am = timezone.now()
        self.save(update_fields=("status", "versendet_am"))


class SchulungsTask(ComplianceTask):
    """Polymorph aus ComplianceTask: ein Mitarbeiter x eine Welle = ein Task.

    Erbt `betroffene` (M2M), `created_at`, `due_date` etc. aus ComplianceTask.
    """

    welle = models.ForeignKey(SchulungsWelle, on_delete=models.CASCADE, related_name="tasks")
    mitarbeiter = models.ForeignKey(
        Mitarbeiter, on_delete=models.CASCADE, related_name="schulungs_tasks"
    )
    abgeschlossen_am = models.DateTimeField(null=True, blank=True)
    richtig_prozent = models.PositiveSmallIntegerField(null=True, blank=True)
    bestanden = models.BooleanField(null=True)
    zertifikat_id = models.CharField(max_length=64, blank=True, db_index=True)
    ablauf_datum = models.DateField(null=True, blank=True)
    gezogene_fragen = models.ManyToManyField(
        "Frage",
        through="SchulungsTaskFrage",
        related_name="task_ziehungen",
        help_text=(
            "Beim ersten resolve gesampelt: kurs.fragen_pro_quiz Stück aus "
            "kurs.fragen.all(), persistiert pro Task, damit Mitarbeiter:innen "
            "bei Tab-Wechsel dieselben Fragen wiedersehen."
        ),
    )

    class Meta:
        unique_together = (("welle", "mitarbeiter"),)
        verbose_name = "Schulungs-Task"
        verbose_name_plural = "Schulungs-Tasks"

    def __str__(self) -> str:
        return f"{self.mitarbeiter} -> {self.welle.titel}"


class SchulungsTaskFrage(models.Model):
    """Through-Model für SchulungsTask.gezogene_fragen.

    Hält die konkrete Fragen-Auswahl (= Sample aus Pool) für einen Task fest,
    inklusive Reihenfolge, in der sie dem Mitarbeiter präsentiert werden.
    """

    task = models.ForeignKey(
        SchulungsTask, on_delete=models.CASCADE, related_name="frage_ziehungen"
    )
    frage = models.ForeignKey("Frage", on_delete=models.PROTECT)
    reihenfolge = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = (("task", "frage"),)
        ordering = ("reihenfolge", "id")
        verbose_name = "Gezogene Frage"
        verbose_name_plural = "Gezogene Fragen"

    def __str__(self) -> str:
        return f"{self.task_id}#{self.reihenfolge}: {self.frage_id}"


class QuizAntwort(models.Model):
    """Eine konkrete Antwort eines Mitarbeiters auf eine Frage in einem Task."""

    task = models.ForeignKey(SchulungsTask, on_delete=models.CASCADE, related_name="antworten")
    frage = models.ForeignKey(Frage, on_delete=models.PROTECT)
    gewaehlte_option = models.ForeignKey(AntwortOption, on_delete=models.PROTECT)
    war_korrekt = models.BooleanField()
    beantwortet_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("task", "frage"),)
        verbose_name = "Quiz-Antwort"
        verbose_name_plural = "Quiz-Antworten"

    def __str__(self) -> str:
        marker = "[OK]" if self.war_korrekt else "[X]"
        return f"{marker} {self.task.mitarbeiter} - {self.frage.text[:30]}"
