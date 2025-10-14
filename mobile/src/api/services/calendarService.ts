import { api } from '../client';
import { endpoints } from '../endpoints';

export type CalendarResumoDia = {
  data: string; // YYYY-MM-DD
  valor_pagar?: number;
  valor_receber?: number;
  saldo?: number; // when both exist
};

export type CalendarResumoResponse = {
  ano: number;
  mes: number;
  dias: CalendarResumoDia[];
};

export async function getCalendarResumo(params: { ano: number; mes: number }) {
  const res = await api.get(endpoints.calendarResumo, { params });
  return res.data as CalendarResumoResponse;
}

export type CalendarDiaItem = {
  nome_fantasia: string;
  cnpj: string;
  valor: number;
  data: string; // ISO
  tipo: 'PAGAR' | 'RECEBER' | null;
};

export type CalendarDiaResponse = {
  data: string;
  detalhes: CalendarDiaItem[];
};

export async function getCalendarDia(data: string) {
  const res = await api.get(endpoints.calendarDia, { params: { data } });
  return res.data as CalendarDiaResponse;
}
