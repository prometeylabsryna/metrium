from django.http import HttpResponse, JsonResponse
from django.views import View


class HealthView(View):
    def get(self, request):
        return JsonResponse({"status": "ok"})


class RobotsView(View):
    def get(self, request):
        from django.conf import settings

        lines = [
            "User-agent: *",
            "Disallow: /*?replytocom",
            "Disallow: /*?fbclid",
            "Disallow: /*?utm_",
            "Disallow: /wp-includes/",
            "Disallow: /trackback/",
            "Disallow: /xmlrpc.php",
            f"Sitemap: {settings.SITE_URL}/sitemap.xml",
        ]
        return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
