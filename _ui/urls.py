from django.urls import path
from . import views

urlpatterns = [
    path("dashboard", views.dashboard),
    path("stdout-log", views.stdout_log),
    path("main-log", views.main_log),
]