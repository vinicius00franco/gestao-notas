import { api } from '../api/client';
import { NotaFiscal, Classificacao } from '../types';

export async function getNotasFiscais(): Promise<NotaFiscal[]> {
    const response = await api.get('/notas-fiscais/');
    return response.data;
}

export async function getClassificacoes(): Promise<Classificacao[]> {
    const response = await api.get('/classificacoes/');
    return response.data;
}

export async function updateNotaFiscalClassificacao(notaId: string, classificacaoId: string): Promise<NotaFiscal> {
    const response = await api.patch(`/notas-fiscais/${notaId}/`, { classificacao_id: classificacaoId });
    return response.data;
}

export async function deleteNotaFiscal(notaId: string): Promise<void> {
    await api.delete(`/notas-fiscais/${notaId}/`);
}