from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.static import serve

from sitegen.pages import body_news_article
from sitegen.render import render_layout

from .export import article_to_newsitem
from .models import Article

SITE_NAME = "Lead Japan 合同会社"


@staff_member_required
def preview(request, pk):
    article = get_object_or_404(Article, pk=pk)
    item = article_to_newsitem(article, image=None)
    image_src = f"media/{article.image.name}" if article.image else None
    html = render_layout(
        title=f"{item.title} | {SITE_NAME}",
        description=item.summary,
        body=body_news_article(item, image_src=image_src),
        current="news.html",
    )
    return HttpResponse(html)


@staff_member_required
def preview_static(request, path):
    return serve(request, path, document_root=settings.REPO_ROOT / "static")


@staff_member_required
def preview_media(request, path):
    return serve(request, path, document_root=settings.MEDIA_ROOT)
