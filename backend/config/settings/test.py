from .base import *  # noqa: F401,F403

DEBUG = False
SECRET_KEY = "test-only-key-not-for-production"  # noqa: S105
# Tests laufen gegen dieselbe lokale Postgres-Instanz; pytest-django legt
# automatisch eine separate Test-DB an (vorangestellt mit "test_").
