"""factory_boy Factories für Tests."""

import factory
from django.contrib.auth import get_user_model
from django_tenants.utils import get_tenant_domain_model, get_tenant_model

from core.models import TenantRole

Tenant = get_tenant_model()
TenantDomain = get_tenant_domain_model()
User = get_user_model()


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant
        django_get_or_create = ("schema_name",)

    schema_name = factory.Sequence(lambda n: f"test_tenant_{n}")
    firma_name = factory.Sequence(lambda n: f"Test-Firma {n} GmbH")
    plan = "professional"
    pilot = True
    pilot_discount_percent = 40


class TenantDomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TenantDomain
        django_get_or_create = ("domain",)

    tenant = factory.SubFactory(TenantFactory)
    # Underscore in DNS-Labels ist RFC 1034/1035-verboten; Django blockt das via SuspiciousOperation.
    domain = factory.LazyAttribute(
        lambda o: f"{o.tenant.schema_name.replace('_', '-')}.app.vaeren.local"
    )
    is_primary = True


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("email",)
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    tenant_role = TenantRole.QM_LEITER
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):  # type: ignore[override]
        if not create:
            return
        self.set_password(extracted or "test-password-12345")
        self.save()


import datetime  # noqa: E402
import hashlib  # noqa: E402

from core.models import Mitarbeiter  # noqa: E402


class MitarbeiterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mitarbeiter

    vorname = factory.Faker("first_name", locale="de_DE")
    nachname = factory.Faker("last_name", locale="de_DE")
    email = factory.LazyAttribute(lambda o: f"{o.vorname.lower()}.{o.nachname.lower()}@example.de")
    abteilung = factory.Iterator(["Produktion", "QM", "IT", "HR", "Vertrieb"])
    rolle = "Mitarbeiter:in"
    eintritt = datetime.date(2024, 1, 1)


from core.models import ComplianceTask, ComplianceTaskStatus  # noqa: E402


class ComplianceTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ComplianceTask

    titel = factory.Sequence(lambda n: f"Compliance-Task {n}")
    modul = "pflichtunterweisung"
    kategorie = "schulung"
    frist = factory.LazyAttribute(lambda o: datetime.date.today() + datetime.timedelta(days=30))
    status = ComplianceTaskStatus.OFFEN


from core.models import Evidence  # noqa: E402


class EvidenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Evidence

    titel = factory.Sequence(lambda n: f"Evidence {n}")
    sha256 = factory.Sequence(lambda n: hashlib.sha256(f"x-{n}".encode()).hexdigest())
    mime_type = "application/pdf"
    groesse_bytes = 1024


# --- Sprint 4: pflichtunterweisung -------------------------------------

from pflichtunterweisung.models import (  # noqa: E402
    AntwortOption,
    Frage,
    Kurs,
    KursModul,
    SchulungsTask,
    SchulungsWelle,
)


def _current_tenant_schema() -> str:
    from django.db import connection

    return connection.schema_name


class KursFactory(factory.django.DjangoModelFactory):
    """Standard-Katalog-Kurs (eigentuemer_tenant=""). Read-only fuer Tenants."""

    class Meta:
        model = Kurs

    titel = factory.Sequence(lambda n: f"Kurs {n}: AI-Act-Grundlagen")
    beschreibung = "Pflicht-Schulung zu Vaeren-Compliance-Grundlagen."
    gueltigkeit_monate = 12
    min_richtig_prozent = 80
    fragen_pro_quiz = 10
    quiz_modus = Kurs.QuizModus.QUIZ
    mindest_lesezeit_s = 0
    zertifikat_aktiv = True
    eigentuemer_tenant = ""  # Standardkatalog


class EigenerKursFactory(KursFactory):
    """Vom Tenant selbst angelegter Kurs. eigentuemer_tenant + erstellt_von gesetzt."""

    eigentuemer_tenant = factory.LazyFunction(_current_tenant_schema)
    erstellt_von = factory.SubFactory(UserFactory)


class KursModulFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = KursModul

    kurs = factory.SubFactory(KursFactory)
    titel = factory.Sequence(lambda n: f"Modul {n}")
    inhalt_md = "## Lernziel\n\nWichtige Inhalte stehen hier."
    reihenfolge = factory.Sequence(lambda n: n)


class FrageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Frage

    kurs = factory.SubFactory(KursFactory)
    text = factory.Sequence(lambda n: f"Frage {n}: Was ist korrekt?")
    erklaerung = "Erklärung zur richtigen Antwort."
    reihenfolge = factory.Sequence(lambda n: n)


class AntwortOptionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AntwortOption

    frage = factory.SubFactory(FrageFactory)
    text = factory.Sequence(lambda n: f"Antwort-Option {n}")
    ist_korrekt = False
    reihenfolge = factory.Sequence(lambda n: n)


class SchulungsWelleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SchulungsWelle

    kurs = factory.SubFactory(KursFactory)
    titel = factory.Sequence(lambda n: f"Welle {n}")
    deadline = factory.LazyAttribute(lambda _o: datetime.date.today() + datetime.timedelta(days=30))
    erstellt_von = factory.SubFactory(UserFactory)


class SchulungsTaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SchulungsTask

    welle = factory.SubFactory(SchulungsWelleFactory)
    mitarbeiter = factory.SubFactory(MitarbeiterFactory)
    titel = factory.LazyAttribute(lambda o: f"Schulung: {o.welle.titel}")
    modul = "pflichtunterweisung"
    kategorie = "schulung"
    frist = factory.LazyAttribute(lambda o: o.welle.deadline)
    status = ComplianceTaskStatus.OFFEN


# --- Sprint 5: hinschg -------------------------------------------------

from hinschg.models import (  # noqa: E402
    Bearbeitungsschritt,
    EingangsKanal,
    Meldung,
    MeldungsTaskTyp,
)


class MeldungFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Meldung

    eingangs_kanal = EingangsKanal.WEB_ANONYM
    anonym = True
    titel_verschluesselt = factory.Sequence(lambda n: f"Hinweis Nr. {n}")
    beschreibung_verschluesselt = (
        "Verdacht auf Compliance-Verstoss. Beobachtung am 2026-05-08 um 14:30 in Halle 3."
    )
    melder_kontakt_verschluesselt = ""


class BearbeitungsschrittFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Bearbeitungsschritt

    meldung = factory.SubFactory(MeldungFactory)
    aktion = "klassifizierung"
    notiz_verschluesselt = "Erstklassifizierung durch QM."


__all__ = [
    "AntwortOptionFactory",
    "BearbeitungsschrittFactory",
    "ComplianceTaskFactory",
    "EigenerKursFactory",
    "EvidenceFactory",
    "FrageFactory",
    "KursFactory",
    "KursModulFactory",
    "MeldungFactory",
    "MeldungsTaskTyp",
    "MitarbeiterFactory",
    "SchulungsTaskFactory",
    "SchulungsWelleFactory",
    "TenantDomainFactory",
    "TenantFactory",
    "UserFactory",
]
