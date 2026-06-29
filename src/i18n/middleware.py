from django.utils.deprecation import MiddlewareMixin


class PolylangCompatMiddleware(MiddlewareMixin):
    """Expose Polylang-style language codes (ua/ru) on the request."""

    def process_request(self, request):
        path = request.path
        if path == "/ru/" or path.startswith("/ru/"):
            request.language_code = "ru"
        else:
            request.language_code = "ua"
