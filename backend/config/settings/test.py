from .base import *

DEBUG = False
SECRET_KEY = "test-only-key-not-for-production"
# Tests laufen gegen dieselbe lokale Postgres-Instanz; pytest-django legt
# automatisch eine separate Test-DB an (vorangestellt mit "test_").

ALLOWED_HOSTS = ["*"]

# Phase-3-Worktree: eigene Test-DB, weil Cross-Worktree-Migrations
# in test_vaeren konkurrieren (module_iso42001_aktiv aus parallel-Branch).
DATABASES["default"]["TEST"] = {"NAME": "test_vaeren_arbsch"}
