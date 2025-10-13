from prometheus_client import Counter, Histogram, Gauge
import time
import functools

# Métricas de rotas
route_requests_total = Counter(
    'django_route_requests_total',
    'Total requests per route',
    ['method', 'route', 'status']
)

route_duration_seconds = Histogram(
    'django_route_duration_seconds',
    'Request duration per route',
    ['method', 'route']
)

# Métricas de negócio
notas_processadas_total = Counter(
    'notas_processadas_total',
    'Total notas fiscais processadas',
    ['status', 'tipo']
)

jobs_ativos = Gauge(
    'jobs_processamento_ativos',
    'Jobs de processamento ativos'
)

def track_route_metrics(view_func):
    """Decorator para rastrear métricas de rotas."""
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        route = request.resolver_match.url_name
        method = request.method

        try:
            response = view_func(request, *args, **kwargs)
            status = response.status_code
            return response
        except Exception as e:
            status = 500
            raise
        finally:
            duration = time.time() - start_time
            route_requests_total.labels(
                method=method,
                route=route,
                status=status
            ).inc()
            route_duration_seconds.labels(
                method=method,
                route=route
            ).observe(duration)

    return wrapper