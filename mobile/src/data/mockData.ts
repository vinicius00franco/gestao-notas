import { JobStatus, NotaFiscal, TopFornecedor } from '../types';
import 'react-native-get-random-values';
import { v4 as uuidv4 } from 'uuid';

// --- Estado Simulado ---
// Uma "tabela" em memória para armazenar os jobs criados durante a sessão.
export const mockJobsDB: JobStatus[] = [];

// --- Tipos e Status ---
export const STATUS_OPTIONS = {
  PENDENTE: { codigo: 'PENDENTE', descricao: 'Aguardando processamento' },
  PROCESSANDO: { codigo: 'PROCESSANDO', descricao: 'Em processamento' },
  CONCLUIDO: { codigo: 'CONCLUIDO', descricao: 'Processamento concluído com sucesso' },
  ERRO: { codigo: 'ERRO', descricao: 'Falha ao processar a nota' },
};

// --- Fábricas de Dados Mockados ---

/**
 * Cria um novo job com status PENDENTE.
 */
export const createMockJob = (): JobStatus => {
  return {
    uuid: uuidv4(),
    status: STATUS_OPTIONS.PENDENTE,
  };
};

/**
 * Simula a extração de dados de uma nota fiscal, retornando os dados extraídos.
 * Randomicamente decide se a extração é um sucesso, parcial ou uma falha.
 */
export const extractMockNotaData = (): Partial<NotaFiscal> & { success: boolean, partial: boolean, error?: string } => {
  const random = Math.random();

  // 20% de chance de erro
  if (random < 0.2) {
    return {
      success: false,
      partial: false,
      error: 'QR code ilegível ou formato de nota inválido.',
    };
  }

  // 30% de chance de sucesso parcial
  if (random < 0.5) {
    return {
      success: true,
      partial: true,
      numero: '12345',
      // cnpj_emitente: null, // Campo faltando. Removido para conformidade de tipo.
      nome_emitente: 'Fornecedor Exemplo',
      valor_total: 150.75,
    };
  }

  // 50% de chance de sucesso total
  return {
    success: true,
    partial: false,
    numero: '98765',
    cnpj_emitente: '12.345.678/0001-99',
    nome_emitente: 'Empresa de Tecnologia XYZ',
    valor_total: 1234.56,
  };
};

/**
 * Gera dados mockados para o dashboard.
 * @param jobs A lista atual de jobs para calcular as métricas.
 */
export const createMockDashboardData = (jobs: JobStatus[]) => {
  const stats = {
    concluidos: jobs.filter(j => j.status.codigo === 'CONCLUIDO').length,
    erros: jobs.filter(j => j.status.codigo === 'ERRO').length,
    pendentes: jobs.filter(j => j.status.codigo === 'PENDENTE').length,
    processando: jobs.filter(j => j.status.codigo === 'PROCESSANDO').length,
  };

  const topFornecedores: TopFornecedor[] = [
    { nome: 'Fornecedor A', cnpj: '11.111.111/0001-11', total_a_pagar: 1500.50 },
    { nome: 'Fornecedor B', cnpj: '22.222.222/0001-22', total_a_pagar: 1250.00 },
    { nome: 'Fornecedor C', cnpj: '33.333.333/0001-33', total_a_pagar: 980.75 },
  ];

  return {
    stats,
    top_5_fornecedores_pendentes: topFornecedores,
    economia_gerada: 450.23, // Valor estático por enquanto
    total_processado: jobs.length,
  };
};
