from django.urls import path
from . import views

urlpatterns = [
    path("action/init_scraper", views.initialize_scraper),
    path("action/start_scraper", views.start_scraper),
    path("action/stop_scraper", views.stop_scraper),
    path("info/scraper_stats", views.scraper_stats),
    path("info/database_stats", views.database_stats),
    path("info/latest_logs", views.latest_logs),
    path("verify_token", views.validate_token),
]