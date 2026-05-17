"""Public-Schema-Migration für ISO 42001 Norm-Katalog."""

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Iso42001Control",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(db_index=True, max_length=10, unique=True)),
                ("title_de", models.CharField(max_length=200)),
                ("description_de", models.TextField(blank=True, default="")),
                (
                    "kategorie",
                    models.CharField(
                        choices=[
                            ("a2_policies", "A.2 Policies related to AI"),
                            ("a3_organization", "A.3 Internal Organization"),
                            ("a4_resources", "A.4 Resources for AI Systems"),
                            ("a5_impact", "A.5 Assessing Impacts of AI Systems"),
                            ("a6_lifecycle", "A.6 AI System Life Cycle"),
                            ("a7_data", "A.7 Data for AI Systems"),
                            ("a8_information", "A.8 Information for Interested Parties"),
                            ("a9_use", "A.9 Use of AI Systems"),
                            ("a10_third_party", "A.10 Third-party & Customer Relationships"),
                        ],
                        db_index=True,
                        max_length=30,
                    ),
                ),
                ("annex_b_guidance_url", models.URLField(blank=True, default="")),
                (
                    "applicability_default",
                    models.BooleanField(
                        default=True,
                        help_text="Voreinstellung im SoA. False = typischerweise nur für KI-Entwickler relevant.",
                    ),
                ),
                ("reihenfolge", models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                "verbose_name": "ISO 42001 Control",
                "verbose_name_plural": "ISO 42001 Controls",
                "ordering": ["kategorie", "reihenfolge", "code"],
            },
        ),
    ]
