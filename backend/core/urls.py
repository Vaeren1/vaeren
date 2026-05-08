from django.urls import path

from .views import health

# Leer-Pfad, weil das Tenant-URLconf bereits "api/health/" als Mountpoint setzt.
urlpatterns = [
    path("", health, name="health"),
]
