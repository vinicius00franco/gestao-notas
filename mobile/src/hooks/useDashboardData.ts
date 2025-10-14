import { useQuery } from '@tanstack/react-query';
import { api } from '@/api/client'; // Assuming an api client setup

export type Period = 'last_7_days' | 'last_month' | 'last_3_months' | 'last_year';

// Add types for the API response based on the backend implementation
interface KpiData {
  total_revenue: number;
  pending_payments: number;
  processed_invoices: number;
  active_suppliers: number;
}

interface ChartData {
  revenue_evolution: { month: string; total: number }[];
  top_suppliers: { nome: string; total: number }[];
  financial_entry_distribution: { tipo: string; total: number }[];
  financial_status_distribution: { status: string; count: number }[];
}

interface DashboardData {
  kpis: KpiData;
  charts: ChartData;
}

const fetchDashboardData = async (period: Period): Promise<DashboardData> => {
  const { data } = await api.get(`/dashboard/?period=${period}`);
  return data;
};

export const useDashboardData = (period: Period) => {
  return useQuery<DashboardData, Error>({
    queryKey: ['dashboardData', period],
    queryFn: () => fetchDashboardData(period),
  });
};