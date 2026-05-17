from .base import *

DEBUG = False
SECRET_KEY = "test-only-key-not-for-production"
# Tests laufen gegen dieselbe lokale Postgres-Instanz; pytest-django legt
# automatisch eine separate Test-DB an (vorangestellt mit "test_").

ALLOWED_HOSTS = ["*"]
