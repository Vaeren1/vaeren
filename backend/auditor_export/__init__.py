"""Phase-3 Auditor-Export-Modul.

Generischer, modul-übergreifender Audit-Export:
- OSCAL-JSON (NIST 1.1.2 Subset)
- PDF-Sammelmappe (WeasyPrint, PDF/A-3-Ziel)
- ZIP-Beweismappe mit HMAC-signiertem Manifest
- Public Verify-Endpoint
"""

default_app_config = "auditor_export.apps.AuditorExportConfig"
