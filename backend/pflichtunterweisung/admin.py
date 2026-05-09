from django.contrib import admin

from .models import (
    AntwortOption,
    Frage,
    Kurs,
    KursModul,
    QuizAntwort,
    SchulungsTask,
    SchulungsWelle,
)


class KursModulInline(admin.TabularInline):
    model = KursModul
    extra = 0


class AntwortOptionInline(admin.TabularInline):
    model = AntwortOption
    extra = 0


@admin.register(Kurs)
class KursAdmin(admin.ModelAdmin):
    list_display = ("titel", "min_richtig_prozent", "gueltigkeit_monate", "aktiv", "erstellt_am")
    list_filter = ("aktiv",)
    search_fields = ("titel",)
    inlines = (KursModulInline,)


@admin.register(Frage)
class FrageAdmin(admin.ModelAdmin):
    list_display = ("text", "kurs", "reihenfolge")
    list_filter = ("kurs",)
    inlines = (AntwortOptionInline,)


@admin.register(SchulungsWelle)
class SchulungsWelleAdmin(admin.ModelAdmin):
    list_display = ("titel", "kurs", "status", "deadline", "versendet_am", "erstellt_von")
    list_filter = ("status", "kurs")
    search_fields = ("titel",)


@admin.register(SchulungsTask)
class SchulungsTaskAdmin(admin.ModelAdmin):
    list_display = (
        "mitarbeiter",
        "welle",
        "bestanden",
        "richtig_prozent",
        "abgeschlossen_am",
        "ablauf_datum",
    )
    list_filter = ("bestanden", "welle")


admin.site.register(QuizAntwort)
