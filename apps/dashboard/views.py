from rest_framework import views, status
from rest_framework.response import Response
from . import selectors

class DashboardStatsView(views.APIView):
    def get(self, request, *args, **kwargs):
        period = request.query_params.get('period', 'last_month')
        start_date, end_date = selectors.get_period_dates(period)

        kpis = {
            "total_revenue": selectors.get_total_revenue(start_date, end_date),
            "pending_payments": selectors.get_pending_payments(start_date, end_date),
            "processed_invoices": selectors.get_processed_invoices_count(start_date, end_date),
            "active_suppliers": selectors.get_active_suppliers_count(start_date, end_date),
        }

        charts = {
            "revenue_evolution": selectors.get_revenue_evolution(),
            "top_suppliers": selectors.get_top_suppliers(start_date, end_date),
            "financial_entry_distribution": selectors.get_financial_entry_distribution(start_date, end_date),
            "financial_status_distribution": selectors.get_financial_status_distribution(start_date, end_date),
        }

        return Response({
            "kpis": kpis,
            "charts": charts,
        }, status=status.HTTP_200_OK)
