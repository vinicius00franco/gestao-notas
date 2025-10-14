import { api } from '../api/client';
import { NotaFiscal, Classificacao } from '../types';
import { endpoints } from '../api/endpoints';

export async function getNotasFiscais(): Promise<NotaFiscal[]> {
    const response = await api.get(endpoints.notasFiscais);
    return response.data.results ? response.data.results : response.data;
}

export async function getClassificacoes(): Promise<Classificacao[]> {
    const response = await api.get('/classificacoes/');
    return response.data;
}

export async function updateNotaFiscalClassificacao(notaId: string, classificacaoId: string): Promise<NotaFiscal> {
    const response = await api.patch(`${endpoints.notasFiscais}${notaId}/`, { classificacao_id: classificacaoId });
    return response.data;
}

export async function deleteNotaFiscal(notaId: string): Promise<void> {
    await api.delete(`${endpoints.notasFiscais}${notaId}/`);
}