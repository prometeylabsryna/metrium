from django.http import HttpResponseGone, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin

from src.redirects.models import RedirectRule


class RedirectMiddleware(MiddlewareMixin):
    _cache: dict[str, RedirectRule] | None = None

    @classmethod
    def _rules(cls) -> dict[str, RedirectRule]:
        if cls._cache is None:
            cls._cache = {
                r.source_path: r
                for r in RedirectRule.objects.filter(is_active=True)
            }
        return cls._cache

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache = None

    def process_request(self, request):
        path = request.path.rstrip("/") or "/"

        # /ru/ — Django route for RU homepage; legacy WP rule /ru -> /golovna/ must not override it
        if path == "/ru":
            return None

        rules = self._rules()
        rule = rules.get(path) or rules.get(request.path)
        if not rule:
            return None
        if rule.status_code == 410:
            return HttpResponseGone()
        if rule.status_code in (301, 308):
            return HttpResponsePermanentRedirect(rule.target_url)
        if rule.status_code in (302, 307):
            return HttpResponseRedirect(rule.target_url)
        return None
