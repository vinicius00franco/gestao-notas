import { JobStatus, NotaFiscal, TopFornecedor, Lancamento } from '../types';
import 'react-native-get-random-values';
import { v4 as uuidv4 } from 'uuid';

// --- Estado Simulado ---
export const mockJobsDB: JobStatus[] = [];
export const mockLancamentosDB: Lancamento[] = [];


// --- Tipos e Status ---
export const STATUS_OPTIONS = {
  PENDENTE: { codigo: 'PENDENTE', descricao: 'Aguardando processamento' },
  PROCESSANDO: { codigo: 'PROCESSANDO', descricao: 'Em processamento' },
  CONCLUIDO: { codigo: 'CONCLUIDO', descricao: 'Processamento concluído com sucesso' },
  ERRO: { codigo: 'ERRO', descricao: 'Falha ao processar a nota' },
};

// --- Gerador de Dados Mockados para Lançamentos ---
const generateMockLancamentos = () => {
  // Previne a duplicação de dados em hot-reloads
  if (mockLancamentosDB.length > 0) return;

  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();

  const contasAPagar = [
    { desc: "Compra de Fertilizantes NPK", valor: 350.80, dia: 5 },
    { desc: "Sementes de Alface (5000 un)", valor: 120.00, dia: 8 },
    { desc: "Manutenção do Trator", valor: 550.00, dia: 15 },
    { desc: "Combustível para Maquinário", valor: 250.50, dia: 22 },
  ];

  const contasAReceber = [
    { desc: "Venda de 50 caixas de Alface", valor: 750.00, dia: 10 },
    { desc: "Pagamento - Supermercado X", valor: 1200.00, dia: 18 },
    { desc: "Venda de 100kg de Caqui Fuyu", valor: 450.75, dia: 25 },
    { desc: "Pagamento - Atacadista Y", valor: 980.60, dia: 28 },
  ];

  contasAPagar.forEach(conta => {
    const vencimento = new Date(year, month, conta.dia).toISOString().split('T')[0];
    mockLancamentosDB.push({
      uuid: uuidv4(),
      descricao: conta.desc,
      valor: conta.valor,
      data_vencimento: vencimento,
      data_pagamento: null,
      clf_tipo: { nome: 'A Pagar' },
      clf_status: { nome: 'Pendente' },
      dt_criacao: today.toISOString(),
      dt_alteracao: today.toISOString(),
    });
  });

  contasAReceber.forEach(conta => {
    const vencimento = new Date(year, month, conta.dia).toISOString().split('T')[0];
    mockLancamentosDB.push({
      uuid: uuidv4(),
      descricao: conta.desc,
      valor: conta.valor,
      data_vencimento: vencimento,
      data_pagamento: null,
      clf_tipo: { nome: 'A Receber' },
      clf_status: { nome: 'Pendente' },
      dt_criacao: today.toISOString(),
      dt_alteracao: today.toISOString(),
    });
  });
};

// Gera os dados iniciais ao carregar o módulo
generateMockLancamentos();


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
 * Simula a extração de dados de uma nota fiscal.
 */
export const extractMockNotaData = (): Partial<NotaFiscal> & { success: boolean, partial: boolean, error?: string } => {
  const random = Math.random();

  if (random < 0.2) {
    return { success: false, partial: false, error: 'QR code ilegível.' };
  }

  if (random < 0.5) {
    return { success: true, partial: true, numero: '12345', nome_emitente: 'Fornecedor Parcial', valor_total: 150.75 };
  }

  return { success: true, partial: false, numero: '98765', cnpj_emitente: '12.345.678/0001-99', nome_emitente: 'Empresa Completa', valor_total: 1234.56 };
};

/**
 * Gera dados mockados para o dashboard.
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
    economia_gerada: 450.23,
    total_processado: jobs.length,
  };
};
