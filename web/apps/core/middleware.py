from django.conf import settings
from django.contrib.auth.views import redirect_to_login

EXEMPT_PATH_PREFIXES = ("/admin/", "/accounts/")


class LoginRequiredMiddleware:
    """Gates every view behind login except Django admin and the auth URLs.

    MakerStock is a self-hosted personal/small-team tool where every page is
    private inventory data, so this is applied globally instead of decorating
    each view individually.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not self._is_exempt(request.path):
            return redirect_to_login(request.get_full_path())
        return self.get_response(request)

    def _is_exempt(self, path: str) -> bool:
        if path.startswith(EXEMPT_PATH_PREFIXES):
            return True
        if path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
            return True
        return False
