"""Smoke- und Verhaltens-Tests für `hinschg.models`. Sprint 5."""

from __future__ import annotations

import datetime

import pytest
from django_tenants.utils import schema_context

from core.fields import EncryptedFieldError
from hinschg.models import (
    DEFAULT_BESTAETIGUNG_TAGE,
    Bearbeitungsschritt,
    Meldung,
    MeldungsTask,
    MeldungsTaskTyp,
    MeldungStatus,
)


@pytest.fixture
def tenant(db):
    from tests.factories import TenantFactory

    yield TenantFactory(schema_name="hin_smoke", firma_name="HinSchG-Smoke GmbH")


def test_meldung_eingangs_token_unique_and_random(tenant):
    with schema_context(tenant.schema_name):
        m1 = Meldung.objects.create(
            titel_verschluesselt="A",
            beschreibung_verschluesselt="A-Body",
        )
        m2 = Meldung.objects.create(
            titel_verschluesselt="B",
            beschreibung_verschluesselt="B-Body",
        )
        assert m1.eingangs_token != m2.eingangs_token
        assert len(m1.eingangs_token) >= 40  # url-safe 32 bytes ≈ 43 chars
        assert m1.status == MeldungStatus.EINGEGANGEN


def test_meldung_content_is_encrypted_in_db(tenant):
    """Klartext darf NICHT direkt in der DB stehen — nur Fernet-Bytes."""
    from django.db import connection

    secret = "Verdacht: Bestechung im Einkauf am 2026-05-09."
    with schema_context(tenant.schema_name):
        meldung = Meldung.objects.create(
            titel_verschluesselt="Bestechungsverdacht",
            beschreibung_verschluesselt=secret,
        )
        # Raw-Read aus DB: darf weder titel noch beschreibung als Klartext finden
        with connection.cursor() as cur:
            cur.execute(
                "SELECT titel_verschluesselt, beschreibung_verschluesselt "
                "FROM hinschg_meldung WHERE id = %s",
                [meldung.id],
            )
            row = cur.fetchone()
        raw_titel = bytes(row[0])
        raw_beschreibung = bytes(row[1])
        assert b"Bestechungsverdacht" not in raw_titel
        assert b"Bestechung" not in raw_beschreibung
        # Wiederlesen über ORM gibt Klartext
        meldung.refresh_from_db()
        assert meldung.beschreibung_verschluesselt == secret


def test_meldung_creation_auto_creates_two_compliance_tasks(tenant):
    """HinSchG §17 Abs. 2 + 4: 7d-Bestätigung + 3m-Rückmeldung."""
    with schema_context(tenant.schema_name):
        meldung = Meldung.objects.create(
            titel_verschluesselt="t",
            beschreibung_verschluesselt="b",
        )
        tasks = list(meldung.tasks.order_by("frist"))
        assert len(tasks) == 2
        typen = {t.pflicht_typ for t in tasks}
        assert typen == {MeldungsTaskTyp.BESTAETIGUNG_7D, MeldungsTaskTyp.RUECKMELDUNG_3M}
        bestaetigung = next(t for t in tasks if t.pflicht_typ == MeldungsTaskTyp.BESTAETIGUNG_7D)
        rueckmeldung = next(t for t in tasks if t.pflicht_typ == MeldungsTaskTyp.RUECKMELDUNG_3M)
        today = datetime.date.today()
        assert bestaetigung.frist == today + datetime.timedelta(days=DEFAULT_BESTAETIGUNG_TAGE)
        assert rueckmeldung.frist == meldung.rueckmeldung_faellig_bis


def test_meldungstask_unique_per_meldung_pflichttyp(tenant):
    from django.db import IntegrityError, transaction

    with schema_context(tenant.schema_name):
        meldung = Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                MeldungsTask.objects.create(
                    meldung=meldung,
                    pflicht_typ=MeldungsTaskTyp.BESTAETIGUNG_7D,
                    titel="dup",
                    modul="hinschg",
                    kategorie="bestaetigung_7d",
                    frist=datetime.date.today(),
                )


def test_bearbeitungsschritt_encrypted_notiz(tenant):
    from tests.factories import UserFactory

    with schema_context(tenant.schema_name):
        meldung = Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")
        bearbeiter = UserFactory()
        schritt = Bearbeitungsschritt.objects.create(
            meldung=meldung,
            bearbeiter=bearbeiter,
            aktion="klassifizierung",
            notiz_verschluesselt="Geheime Bewertung: Schweregrad MITTEL.",
        )
        schritt.refresh_from_db()
        assert schritt.notiz_verschluesselt == "Geheime Bewertung: Schweregrad MITTEL."


def test_bearbeitungsschritt_allows_anonymous_hinweisgeber_message(tenant):
    """bearbeiter=None markiert Hinweisgeber-Nachricht (über Status-API)."""
    with schema_context(tenant.schema_name):
        meldung = Meldung.objects.create(titel_verschluesselt="t", beschreibung_verschluesselt="b")
        Bearbeitungsschritt.objects.create(
            meldung=meldung,
            bearbeiter=None,
            aktion="hinweisgeber_nachricht",
            notiz_verschluesselt="Nachgereichte Beweise im Anhang.",
        )
        assert meldung.bearbeitungsschritte.count() == 1


@pytest.mark.tenant_isolation
def test_meldung_content_not_decryptable_in_other_tenant(db):
    """Cross-Tenant-Decrypt muss `EncryptedFieldError` raisen — kritischer CI-Gate."""
    from django.db import connection

    from tests.factories import TenantFactory

    a = TenantFactory(schema_name="hin_iso_a", firma_name="A GmbH")
    b = TenantFactory(schema_name="hin_iso_b", firma_name="B GmbH")

    with schema_context(a.schema_name):
        meldung = Meldung.objects.create(
            titel_verschluesselt="A-Geheim",
            beschreibung_verschluesselt="A-Inhalt",
        )
        a_id = meldung.id
        a_token = meldung.eingangs_token

    # Lese Tenant-A-Bytes direkt aus DB und versuche im Tenant-B-Schema zu decrypten.
    # Da Tenant-A-Daten in Tenant-A-Schema liegen, erst dort lesen, dann manuell
    # in Tenant-B-Kontext entschlüsseln.

    with schema_context(a.schema_name):
        with connection.cursor() as cur:
            cur.execute(
                "SELECT beschreibung_verschluesselt FROM hinschg_meldung WHERE id = %s",
                [a_id],
            )
            ciphertext = bytes(cur.fetchone()[0])

    with schema_context(b.schema_name):
        # Im Tenant-B-Schema gibt es diesen Eingangs-Token nicht
        assert not Meldung.objects.filter(eingangs_token=a_token).exists()

        # Direkter Decrypt-Versuch in Tenant-B muss fehlschlagen
        from core.fields import EncryptedTextField

        field = EncryptedTextField()
        with pytest.raises(EncryptedFieldError):
            field.from_db_value(ciphertext, None, None)
    connection.set_schema_to_public()
