from django.urls import path

from . import views

app_name = "press"

urlpatterns = [
    path("preview/static/<path:path>", views.preview_static, name="preview_static"),
    path("preview/media/<path:path>", views.preview_media, name="preview_media"),
    path("preview/<int:pk>.html", views.preview, name="preview"),
]
