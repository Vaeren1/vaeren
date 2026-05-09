"""Public-Schema-URLs (`/api/demo/`)."""

from django.urls import path

from .views import DemoRequestCreateView

urlpatterns = [
    path("demo/", DemoRequestCreateView.as_view(), name="demo-request-create"),
]
