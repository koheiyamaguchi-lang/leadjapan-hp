import datetime

from django.contrib import admin

from .models import Article, suggest_slug


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "published_on", "category", "status")
    list_filter = ("status", "category")
    search_fields = ("title",)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        today = datetime.date.today()
        initial.setdefault("published_on", today)
        initial.setdefault("slug", suggest_slug(today))
        return initial
