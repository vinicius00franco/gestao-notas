import re
from django.conf import settings


class ApiVersionFallbackMiddleware:
    """
    Rewrites incoming paths like /api/v15/... to a target version according
    to configuration in settings.API_VERSION_FALLBACKS.

    settings.API_VERSION_FALLBACKS is expected to be a list of dicts:
      {"range": (min_inclusive, max_inclusive), "target": 10}

    Example:
      API_VERSION_FALLBACKS = [ {"range": (10,20), "target": 10} ]

    If no fallback matches, the path is left unchanged.
    """

    VERSION_RE = re.compile(r"^/api/v(?P<ver>\d+)(?P<rest>/.*|$)")

    def __init__(self, get_response):
        self.get_response = get_response
        self.fallbacks = getattr(settings, 'API_VERSION_FALLBACKS', [])

    def __call__(self, request):
        path = request.path
        m = self.VERSION_RE.match(path)
        if m:
            ver = int(m.group('ver'))
            rest = m.group('rest') or '/'
            for fb in self.fallbacks:
                rmin, rmax = fb.get('range', (fb.get('target'), fb.get('target')))
                if rmin <= ver <= rmax:
                    target = fb.get('target')
                    new_path = f"/api/v{target}{rest}"
                    # mutate path info so view resolving uses new path
                    request.path_info = new_path
                    request.path = new_path
                    break

        response = self.get_response(request)
        return response
