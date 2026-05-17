"""Public-Schema-URLs (`/api/demo/`, `/api/kontakt/`)."""

from django.urls import path

from .views import DemoRequestCreateView, KontaktRequestCreateView

urlpatterns = [
    path("demo/", DemoRequestCreateView.as_view(), name="demo-request-create"),
    path("kontakt/", KontaktRequestCreateView.as_view(), name="kontakt-request-create"),
]
