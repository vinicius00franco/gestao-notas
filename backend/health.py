from django.http import JsonResponse


def healthz(request):
    """Lightweight health endpoint.
    - Returns 200 when Django is up and DB responds to SELECT 1.
    - Returns 503 if DB check fails (so orchestrators can detect issues).
    """
    db_ok = True
    error_msg = None
    try:
        # Import inside function to avoid issues at import-time
        from django.db import connections
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception as exc:  # pragma: no cover
        db_ok = False
        error_msg = str(exc)[:300]

    status = 200 if db_ok else 503
    payload = {
        "status": "ok" if db_ok else "degraded",
        "db": "ok" if db_ok else "error",
    }
    if error_msg:
        payload["error"] = error_msg

    return JsonResponse(payload, status=status)
