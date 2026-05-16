"""Django-Admin-Konfiguration für redaktion."""

from __future__ import annotations

from django.contrib import admin

from .models import (
    Korrektur,
    NewsCandidate,
    NewsPost,
    NewsSource,
    RedaktionRun,
)


@admin.register(NewsSource)
class NewsSourceAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "active", "last_crawled_at")
    list_filter = ("active",)
    search_fields = ("name", "key")
    readonly_fields = ("created_at", "updated_at")


@admin.register(NewsCandidate)
class NewsCandidateAdmin(admin.ModelAdmin):
    list_display = ("source", "titel_raw", "fetched_at", "selected_at", "discarded_at")
    list_filter = ("source", "selected_at", "discarded_at")
    search_fields = ("titel_raw", "quell_url")
    readonly_fields = ("quell_url_hash", "fetched_at")


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = (
        "titel",
        "kategorie",
        "geo",
        "relevanz",
        "status",
        "published_at",
        "pinned",
    )
    list_filter = ("status", "kategorie", "geo", "type", "relevanz", "pinned")
    search_fields = ("titel", "slug", "lead")
    prepopulated_fields = {"slug": ("titel",)}
    readonly_fields = ("unpublish_token", "created_at", "updated_at")
    actions = ("action_publish", "action_unpublish", "action_pin", "action_unpin")

    @admin.action(description="Veröffentlichen")
    def action_publish(self, request, queryset):
        for post in queryset:
            post.publish()
        self.message_user(request, f"{queryset.count()} Beiträge veröffentlicht.")

    @admin.action(description="Zurückziehen")
    def action_unpublish(self, request, queryset):
        for post in queryset:
            post.unpublish()
        self.message_user(request, f"{queryset.count()} Beiträge zurückgezogen.")

    @admin.action(description="Anpinnen")
    def action_pin(self, request, queryset):
        queryset.update(pinned=True)

    @admin.action(description="Anpinnen aufheben")
    def action_unpin(self, request, queryset):
        queryset.update(pinned=False)


@admin.register(RedaktionRun)
class RedaktionRunAdmin(admin.ModelAdmin):
    list_display = ("started_at", "finished_at", "published", "held", "cost_eur")
    readonly_fields = ("started_at",)


@admin.register(Korrektur)
class KorrekturAdmin(admin.ModelAdmin):
    list_display = ("post", "korrigiert_am")
    search_fields = ("post__titel", "was_geaendert")
    readonly_fields = ("korrigiert_am",)
