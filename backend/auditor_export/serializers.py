"""DRF-Serializer für Audit-Export."""

from __future__ import annotations

from rest_framework import serializers

from .models import AuditExportProfile, AuditExportRun


class AuditExportProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditExportProfile
        fields = [
            "id",
            "name",
            "template",
            "norm_scope",
            "zeitraum_von",
            "zeitraum_bis",
            "filter_json",
            "evidence_mode",
            "anonymisieren_pii",
            "watermark_draft",
            "erstellt_von",
            "erstellt_am",
            "aktualisiert_am",
        ]
        read_only_fields = ["id", "erstellt_von", "erstellt_am", "aktualisiert_am"]

    def validate_norm_scope(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError(
                "norm_scope muss eine nicht-leere Liste von NormScope-Strings sein."
            )
        from .models import NormScope

        valid = {choice for choice, _ in NormScope.choices}
        for entry in value:
            if entry not in valid:
                raise serializers.ValidationError(f"Unbekannter NormScope: {entry}")
        return value

    def validate(self, attrs):
        zv = attrs.get("zeitraum_von") or getattr(self.instance, "zeitraum_von", None)
        zb = attrs.get("zeitraum_bis") or getattr(self.instance, "zeitraum_bis", None)
        if zv and zb and zv > zb:
            raise serializers.ValidationError("zeitraum_von muss <= zeitraum_bis sein.")
        return attrs


class AuditExportRunListSerializer(serializers.ModelSerializer):
    """Schmale Liste-Serializer für /runs/"""

    class Meta:
        model = AuditExportRun
        fields = [
            "id",
            "mappe_id",
            "profile",
            "status",
            "started_at",
            "finished_at",
            "evidence_count",
            "file_size_bytes",
            "file_hash_sha256",
            "error",
        ]
        read_only_fields = fields


class AuditExportRunDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditExportRun
        fields = [
            "id",
            "mappe_id",
            "profile",
            "status",
            "started_by",
            "started_at",
            "finished_at",
            "result_path",
            "zip_path",
            "pdf_path",
            "oscal_ssp_path",
            "oscal_assessment_path",
            "file_hash_sha256",
            "pdf_hash_sha256",
            "file_size_bytes",
            "evidence_count",
            "generation_log",
            "error",
        ]
        read_only_fields = fields


class VerifyRequestSerializer(serializers.Serializer):
    mappe_id = serializers.CharField(max_length=30)
    file_sha256 = serializers.CharField(max_length=64)


class VerifyResponseSerializer(serializers.Serializer):
    # Bewusst KEIN tenant-Feld: Public-Endpoint ohne Auth, Tenant-Schema
    # darf nicht ausgegeben werden (Wettbewerber-Reconnaissance).
    verified = serializers.BooleanField()
    reason = serializers.CharField(required=False, allow_blank=True)
    norm_scope = serializers.ListField(child=serializers.CharField(), required=False)
    generated_at = serializers.CharField(required=False, allow_blank=True)
