from .base import *

DEBUG = False
SECRET_KEY = "test-only-key-not-for-production"
# Tests laufen gegen dieselbe lokale Postgres-Instanz; pytest-django legt
# automatisch eine separate Test-DB an (vorangestellt mit "test_").

ALLOWED_HOSTS = ["*"]

# Celery synchron im Test (kein Broker/Worker nötig). `.delay()` führt den Task
# sofort in-process aus → deterministisch + schnell. EAGER_PROPAGATES lässt
# Task-Exceptions den Test laut fehlschlagen statt sie zu schlucken.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
