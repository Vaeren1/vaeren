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
    aktiv = models.BooleanField(default=True)
    erstellt_am = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-erstellt_am",)
        verbose_name = "Kurs"
        verbose_name_plural = "Kurse"

    def __str__(self) -> str:
        return self.titel


class KursModul(models.Model):
    """Lerninhalt-Block in einem Kurs. Markdown."""

    kurs = models.ForeignKey(Kurs, on_delete=models.CASCADE, related_name="module")
    titel = models.CharField(max_length=200)
    inhalt_md = models.TextField(help_text="Lerninhalt als Markdown")
    reihenfolge = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("reihenfolge", "id")
        unique_together = (("kurs", "reihenfolge"),)
        verbose_name = "Kurs-Modul"
        verbose_name_plural = "Kurs-Module"

    def __str__(self) -> str:
        return f"{self.kurs.titel} / {self.titel}"


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
