from django.shortcuts import get_object_or_404, render
from django.views import View

from src.blog.models import BlogPost
from src.i18n.models import Language
from src.seo.services import get_seo_for_object


class BlogDetailView(View):
    language = Language.UA

    def get(self, request, slug):
        post = get_object_or_404(
            BlogPost,
            slug=slug,
            language=self.language,
            is_published=True,
        )
        related_posts = (
            BlogPost.objects.filter(language=self.language, is_published=True)
            .exclude(pk=post.pk)
            .order_by("-published_at")[:3]
        )
        return render(
            request,
            "blog/detail.html",
            {
                "post": post,
                "related_posts": related_posts,
                "seo": get_seo_for_object(post),
            },
        )


class BlogDetailViewRu(BlogDetailView):
    language = Language.RU
