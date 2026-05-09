# Sprint 5 — HinSchG-Hinweisgeberportal

> **Spec §12:** „HinSchG-Modul: Verschlüsselte Meldungen + Bearbeiter-Dashboard + Frist-Tracking"
> **Aufwand:** ~10–12 h (Hard-Cap pro Spec-Risiko §14). Sprint-Scope vor Stunden-Erweiterung reduzieren.
> **Vorbedingung:** Sprint 1–4 abgeschlossen. Backend liefert ComplianceTask-Engine + Mitarbeiter + Auth + MFA. Mailjet-Console-Backend in Dev verfügbar.
> **Sprint-Ende-Kriterium:** Hinweisgeber:in (anonym, kein Login) ruft öffentliches Formular auf, reicht Meldung ein, erhält **Eingangs-Token** + Status-URL. System legt automatisch zwei MeldungsTasks an: Eingangsbestätigung 7 Tage (HinSchG §17 Abs. 2), Rückmeldung 3 Monate (§17 Abs. 4). Compliance-Beauftragte:r liest Meldung (entschlüsselt), legt Bearbeitungsschritte an, schließt ab. Multi-Tenant-Isolation: Tenant A kann Meldung von Tenant B niemals entschlüsseln. CI 3-Job grün.

---

## 1. Architektur-Entscheidungen (autonom, ohne Konrad-Eingabe machbar)

| Entscheidung | Wahl | Begründung |
|---|---|---|
| **Modul-Struktur** | Eigene Django-App `hinschg/` (tenant-Schema-App). | Spec §1: Domain-driven boundaries. Cross-Module-Aufrufe nur über Service-Schnittstellen. |
| **Encryption-Library** | `cryptography.fernet.Fernet` direkt, **NICHT** `django-cryptography`. | Spec §4 nennt `django-cryptography`, aber das Paket ist seit 2023 abandoned und inkompatibel mit Django ≥ 4.2 ohne Patches. `cryptography` (>= 48) ist als Hard-Dependency bereits installiert. Risiko-minimal: ein eigenes ~80-Zeilen-Field statt unmaintained 3rd-Party-Code. Migrations-Pfad zu KMS in Phase 2 bleibt offen. |
| **Encryption-Key-Verwaltung** | Per-Tenant-`encryption_key` (BinaryField im Public-`Tenant`-Modell, auto-generiert via `Fernet.generate_key()` in `Tenant.save()`). | Spec §4: per-Tenant-Schlüssel. Tenant A hat keinen Zugriff auf Tenant-B-Schlüssel via DB-Isolation des Public-Schemas (nur Globalrolle liest). |
| **Encryption-Field-Pattern** | `EncryptedTextField` = TextField, das `value` Fernet-encrypted in BinaryField-Subspalte hält. Liest Key aus `connection.tenant.encryption_key`. | Native Django-Field-API. Lesbar via Manager bleibt transparent (`meldung.beschreibung_verschluesselt` gibt Plaintext zurück). |
| **Polymorphic-Pattern** | `MeldungsTask(ComplianceTask)` per `django-polymorphic` (gleich wie SchulungsTask). | Sprint 2/4 Pattern. Jeder MeldungsTask referenziert genau eine `Meldung` + einen Pflicht-Typ. |
| **Eingangs-Token** | `secrets.token_urlsafe(32)` (256 bit Entropy), `unique=True, db_index=True`. **NICHT** `TimestampSigner`, weil Token als Hinweisgeber-„Login" dient und nicht ablaufen darf (Hinweisgeber muss noch Monate später Status checken können). | HinSchG §17 Abs. 4: Hinweisgeber muss „angemessene Zeit" Status erfragen können. |
| **Frist-Pflichten** | DRAFT von HinSchG §17: 7 Tage Eingangsbestätigung + 3 Monate Rückmeldung. Bei Meldung-Eingang werden 2 `MeldungsTask` automatisch via `pre_save`/`post_save`-Signal angelegt. | HinSchG §17 Abs. 2 + 4 hard requirements. |
| **HITL-Gate** | Eingangsbestätigung-Mail wird **nicht** automatisch versandt. Stattdessen erscheint MeldungsTask im Dashboard. Compliance-Beauftragte:r klickt „Eingangsbestätigung versenden" → markiert Task `erledigt`. | Spec §1: HITL-Pflicht. Verhindert auch Bot-Submission-Mailfluten. |
| **Permission-Modell** | `compliance_beauftragter` allein kann lesen + bearbeiten (Spec §6 Tabelle). GF darf **lesen** (Audit/Aufsicht), aber **nicht bearbeiten**. Andere Rollen: 403. | Spec §6 nicht-verhandelbar. Nicht jeder QM-Leiter hat HinSchG-Befugnis (Vertrauensgrundsatz). |
| **Status-API für Hinweisgeber** | `GET /api/public/hinschg/status/<eingangs_token>/` gibt sanitized payload: `status`, `eingegangen_am`, `bestaetigt_am`, `letzte_rueckmeldung`. **Keine** Bearbeiter-Identitäten oder interne Notizen. | HinSchG §16 Vertraulichkeit beidseitig: Bearbeiter-Identität gegenüber Hinweisgeber geschützt. |
| **Hinweisgeber-Nachricht** | `POST /api/public/hinschg/status/<token>/nachricht/` — Hinweisgeber kann unter Token weiter Hinweise nachliefern. Wird als `Bearbeitungsschritt` mit `aktion="hinweisgeber_nachricht"` geloggt + verschlüsselt gespeichert. | HinSchG §17 Abs. 4: Vertraulicher Rückkanal. |
| **Eingangs-Kanal** | Free-Text `eingangs_kanal` (`web_anonym`, `web_persoenlich`, `email`, `telefon`, `persoenlich`) — in MVP nur `web_anonym` + `web_persoenlich` (Formular-Toggle „Ich möchte nicht anonym bleiben"). E-Mail/Telefon-Eingangskanal manuell durch Bearbeiter erfassbar (Phase 2). | YAGNI. |
| **Aufbewahrungs-Pflicht** | `archiv_loeschdatum = abgeschlossen_am + 3 Jahre` (§11 HinSchG). Setzen wir nur, kein Löschjob in Sprint 5 — der ist Phase 2 (Celery-Beat). | YAGNI bis Pilot-Kunde. |
| **Frontend-Routing** | `/hinschg/meldungen` (intern), `/hinschg/meldungen/:id` (Detail), `/hinweise` (extern, anonym, kein Login), `/hinweise/status/:token` (extern, Token-Status). | Public-Routing nutzt eigene Subdomain `hinweise.app.vaeren.de` (DNS bereits vorhanden, Spec §3). MVP: gleiche `app.vaeren.de`-Subdomain mit Pfad-Routing — Subdomain-Switch in Sprint 8. |
| **Out-of-Scope: Datei-Anhänge** | Keine File-Uploads in Sprint 5. Hinweisgeber:in beschreibt im Free-Text. File-Upload kommt Sprint 5b (`django-storages` + Encryption-on-Upload). | YAGNI. |

---

## 2. Datenmodell (Sprint 5 Erweiterungen)

### 2.1 Public-Schema-Erweiterung (`tenants/models.py`)

```python
class Tenant(TenantMixin):
    # ...bestehend...
    encryption_key = models.BinaryField(
        editable=False,
        help_text="Fernet-Schlüssel für HinSchG-Meldungen. Auto-generiert. NIEMALS rotieren ohne Re-Encrypt-Migration.",
    )

    def save(self, *args, **kwargs):
        if not self.encryption_key:
            from cryptography.fernet import Fernet
            self.encryption_key = Fernet.generate_key()
        super().save(*args, **kwargs)
```

### 2.2 Encryption-Field (`core/fields.py`, neu)

```python
class EncryptedTextField(models.TextField):
    """Fernet-encrypted TextField. Schlüssel kommt aus connection.tenant.encryption_key.

    DB-Repräsentation: bytes (BinaryField im Postgres). Python-Repräsentation: str.
    Kein Index/Search möglich (verschlüsselt). Für Volltextsuche eigenes Phase-2-Modul.
    """
    # _to_python(value) = decrypt
    # get_prep_value(value) = encrypt
    # get_internal_type() = "BinaryField"
```

### 2.3 Tenant-Schema-Modelle (`hinschg/models.py`)

```python
class MeldungStatus(TextChoices):
    EINGEGANGEN = "eingegangen", "Eingegangen"
    BESTAETIGT = "bestaetigt", "Eingangsbestätigung versandt"
    IN_PRUEFUNG = "in_pruefung", "In Prüfung"
    MASSNAHME = "massnahme", "Maßnahme eingeleitet"
    ABGESCHLOSSEN = "abgeschlossen", "Abgeschlossen"
    ABGEWIESEN = "abgewiesen", "Abgewiesen (kein HinSchG-Verstoß)"


class EingangsKanal(TextChoices):
    WEB_ANONYM = "web_anonym", "Web (anonym)"
    WEB_PERSOENLICH = "web_persoenlich", "Web (mit Kontakt)"
    EMAIL = "email", "E-Mail"
    TELEFON = "telefon", "Telefon"
    PERSOENLICH = "persoenlich", "Persönlich"


class Meldung(models.Model):
    eingangs_token = CharField(max_length=64, unique=True, db_index=True)
    eingangs_kanal = CharField(choices=EingangsKanal.choices)
    anonym = BooleanField(default=True)
    titel_verschluesselt = EncryptedTextField()
    beschreibung_verschluesselt = EncryptedTextField()
    melder_kontakt_verschluesselt = EncryptedTextField(blank=True, default="")  # nur wenn anonym=False
    kategorie = CharField(max_length=50, blank=True, default="")  # vom Bearbeiter klassifiziert
    schweregrad = CharField(max_length=20, choices=Schweregrad, blank=True, default="")
    status = CharField(choices=MeldungStatus, default=EINGEGANGEN)
    eingegangen_am = DateTimeField(auto_now_add=True)
    bestaetigung_versandt_am = DateTimeField(null=True)
    rueckmeldung_faellig_bis = DateField()  # eingegangen_am + 3 Monate
    abgeschlossen_am = DateTimeField(null=True)
    archiv_loeschdatum = DateField(null=True)  # = abgeschlossen + 3 Jahre


class MeldungsTaskTyp(TextChoices):
    BESTAETIGUNG_7D = "bestaetigung_7d", "Eingangsbestätigung (7 Tage HinSchG §17 Abs. 2)"
    RUECKMELDUNG_3M = "rueckmeldung_3m", "Rückmeldung (3 Monate HinSchG §17 Abs. 4)"
    ABSCHLUSS = "abschluss", "Abschluss-Mitteilung an Hinweisgeber"


class MeldungsTask(ComplianceTask):
    meldung = ForeignKey(Meldung, related_name="tasks")
    pflicht_typ = CharField(choices=MeldungsTaskTyp.choices)

    class Meta:
        unique_together = (("meldung", "pflicht_typ"),)


class Bearbeitungsschritt(models.Model):
    meldung = ForeignKey(Meldung, related_name="bearbeitungsschritte")
    bearbeiter = ForeignKey(User, on_delete=PROTECT, null=True, blank=True)  # null = Hinweisgeber-Nachricht
    aktion = CharField(max_length=50)  # z.B. "klassifizierung", "rueckmeldung", "hinweisgeber_nachricht"
    notiz_verschluesselt = EncryptedTextField()
    timestamp = DateTimeField(auto_now_add=True)
```

---

## 3. API-Endpoints

### Interne Endpoints (auth required, Permission `hinschg.bearbeiten`)

| Method | Path | Permission | Zweck |
|---|---|---|---|
| GET | `/api/hinschg/meldungen/` | bearbeiten/lesen | Liste Meldungen (sortable nach Frist) |
| GET | `/api/hinschg/meldungen/{id}/` | bearbeiten/lesen | Detail inkl. entschlüsselter Inhalte + Bearbeitungsschritte |
| PATCH | `/api/hinschg/meldungen/{id}/` | bearbeiten | Update kategorie/schweregrad/status |
| POST | `/api/hinschg/meldungen/{id}/bestaetigen/` | bearbeiten | Markiert `bestaetigung_versandt_am`, schließt `BESTAETIGUNG_7D`-Task |
| POST | `/api/hinschg/meldungen/{id}/abschliessen/` | bearbeiten | Setzt status=ABGESCHLOSSEN + abgeschlossen_am + archiv_loeschdatum |
| POST | `/api/hinschg/meldungen/{id}/bearbeitungsschritte/` | bearbeiten | Neuer Bearbeitungsschritt + entsprechender AuditLog-Eintrag |

### Public Endpoints (kein Login)

| Method | Path | Zweck |
|---|---|---|
| POST | `/api/public/hinschg/meldung/` | Neue Meldung anlegen (anonym oder pseudonym). Returns `{eingangs_token, status_url, rueckmeldung_faellig_bis}` |
| GET | `/api/public/hinschg/status/{token}/` | Status-Snapshot (sanitized): status + Datums-Trail. **Keine** Bearbeiter-Identität. |
| POST | `/api/public/hinschg/status/{token}/nachricht/` | Hinweisgeber:in liefert verschlüsselte Nachricht nach. Erscheint als `Bearbeitungsschritt(aktion="hinweisgeber_nachricht", bearbeiter=null)`. |

---

## 4. Sprint-Tasks

| # | Task | Output |
|---|---|---|
| 1 | Sprint-Plan dokumentieren (diese Datei) | Plan committed |
| 2 | `Tenant.encryption_key` + Migration + Auto-Generation in `save()` | Test: jeder Tenant hat unique Key. |
| 3 | `core/fields.py::EncryptedTextField` mit Fernet | Test: roundtrip + multi-tenant isolation (decrypt mit fremdem Key fails). |
| 4 | App `hinschg/` + Models + Migrations + Factories | App + 3 Modelle + 3 Factories + Smoke-Tests. |
| 5 | Auto-Frist-Erstellung via `post_save`-Signal: Bei `Meldung.create` werden 2 `MeldungsTask` angelegt | Test: 2 Tasks mit korrektem Frist-Datum. |
| 6 | Public-Endpoints (Submission + Status + Nachricht) | DRF-Tests für 3 Endpoints + Throttle. |
| 7 | Internal-Endpoints (List/Detail/Patch/Bestaetigen/Abschliessen/Bearbeitungsschritte) | DRF-Tests inkl. Permission-Matrix. |
| 8 | `core/rules.py` erweitern: `hinschg.bearbeiten`/`hinschg.lesen` predicates | Tests aller 5 Rollen. |
| 9 | Multi-Tenant-Isolation: Test, dass Meldung-Inhalt nicht entschlüsselbar ist im fremden Tenant. | Tenant-Isolation-Test (kritischer CI-Gate). |
| 10 | Frontend: `/meldungen` (Liste) + `/meldungen/:id` (Detail mit Bearbeitungsschritt-Form) | React-Routes + TanStack-Query-Hooks. |
| 11 | Frontend: `/hinweise` (anonyme Submission-Form) + `/hinweise/status/:token` (Status-Page + Nachricht-Form) | Public-Routes ohne Login-Wrapper. |
| 12 | OpenAPI-Schema-Sync + CI grün | drift-clean. |
| 13 | README-Update + Direkt-Merge nach `main` | Tag `sprint-5-done`. |

---

## 5. Risiko-Mitigation

| Risiko | Mitigation |
|---|---|
| **Encryption-Key-Verlust** | `encryption_key` ist im `Tenant`-Modell (Public-Schema). `restic` deckt Public-Schema ab → bei Backup-Restore bleibt der Key erhalten. **Restore-Test in Sprint 8.** Bei Key-Verlust = Daten unwiederbringlich. Dokumentieren in `infrastructure/README.md`. |
| **`connection.tenant` ist None bei migrations** | `EncryptedTextField.get_prep_value` muss prüfen `if value is None: return None`. Migrations laufen im Public-Schema, encrypted Felder sind aber nur in Tenant-Schemas → Migration-Code triggert kein encrypt. |
| **Race-Condition Eingangs-Token-Kollision** | `secrets.token_urlsafe(32)` = 256 bit. `unique=True` + `IntegrityError`-Retry-Loop (max 3 Retries). |
| **Hinweisgeber lost Token = lost access** | UI zeigt Token einmalig + Hinweis „Notiere diesen Code, kein Reset möglich" + Print-Button. |
| **Anonyme Submission = Spam-Vektor** | DRF `AnonRateThrottle` 10/h pro IP. Bei Pilot-Eskalation: hCaptcha (Phase 2). |
| **Cross-Tenant-Decrypt-Versuch in Tests** | Multi-Tenant-Isolation-Test, der bewusst Tenant-A-Encrypted-Bytes mit Tenant-B-Key zu decrypten versucht und `InvalidToken` erwartet. |
| **`django-polymorphic`-Migrations-Konflikt** | Sprint 4 hat MeldungsTask-analoges Pattern (SchulungsTask) bereits etabliert. |
| **PII in DRF-Logs** | DRF-Default loggt request bodies bei 5xx → Sentry. **Mitigation:** DRF-Renderer für Public-Endpoint überschreibt `__repr__` der payload. Nice-to-have, nicht kritisch in Sprint 5. |

---

## 6. Out-of-Scope (Sprint 5b oder später)

- Datei-Anhänge zur Meldung (verschlüsselt im S3-Bucket)
- Per-User-Encryption (Bearbeiter-Schlüssel statt Tenant-Schlüssel)
- Auto-Mailjet-Versand der Eingangsbestätigung (HITL bleibt MVP-Default)
- hCaptcha auf Public-Form
- Volltextsuche über entschlüsselte Inhalte (sucht im Klartext-Cache: Phase 2)
- Auto-Lösch-Job (Celery-Beat) bei `archiv_loeschdatum`-Ablauf
- E-Mail-Eingangskanal (parser für `hinweise@<tenant>.vaeren.de`)
- Webhook bei Status-Änderung (Phase 2)
- Mehrsprachige Public-Form (en/tr/pl für KMU mit migrant. Belegschaft) — nice-to-have
