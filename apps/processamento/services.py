import hashlib
import logging
from .models import JobProcessamento
from .publishers import CeleryTaskPublisher
from .repositories import JobProcessamentoRepository
from apps.empresa.models import MinhaEmpresa
from apps.classificadores.models import get_classifier

logger = logging.getLogger(__name__)

def calcular_hash_arquivo(arquivo):
    """
    Calcula o hash SHA-256 de um arquivo.
    """
    sha256_hash = hashlib.sha256()
    # Garante que o ponteiro do arquivo esteja no início
    arquivo.seek(0)
    for chunk in iter(lambda: arquivo.read(4096), b""):
        sha256_hash.update(chunk)
    # Retorna o ponteiro do arquivo para o início para que ele possa ser lido novamente
    arquivo.seek(0)
    return sha256_hash.hexdigest()

def cnpj_para_numero(cnpj_str):
    """Converte CNPJ string para número inteiro."""
    if not cnpj_str:
        return None
    # Remove pontos, barras e traços
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj_str))
    return int(cnpj_limpo) if cnpj_limpo else None

class ProcessamentoService:
    def criar_job_processamento(self, cnpj: str = None, arquivo=None) -> JobProcessamento:
        logger.info(f"PROCESSAMENTO: Iniciando criação de job - CNPJ: {cnpj}, Arquivo: {arquivo.name if arquivo else 'None'}")

        empresa = None
        if cnpj:
            logger.debug(f"PROCESSAMENTO: Buscando empresa por CNPJ: {cnpj}")
            cnpj_numero = cnpj_para_numero(cnpj)
            logger.debug(f"PROCESSAMENTO: CNPJ convertido: {cnpj_numero}")
            if cnpj_numero:
                try:
                    empresa = MinhaEmpresa.get_by_cnpj(cnpj_numero)
                    logger.info(f"PROCESSAMENTO: Empresa encontrada: {empresa.nome} (ID: {empresa.pk})")
                except MinhaEmpresa.DoesNotExist:
                    logger.warning(f"PROCESSAMENTO: Empresa com CNPJ {cnpj} não encontrada")
                    # CNPJ fornecido mas empresa não existe - erro
                    raise ValueError("Empresa com CNPJ informado não encontrada")
            else:
                logger.warning(f"PROCESSAMENTO: CNPJ inválido: {cnpj}")
        else:
            logger.info("PROCESSAMENTO: Nenhum CNPJ fornecido - processamento sem empresa associada")

        logger.debug("PROCESSAMENTO: Calculando hash do arquivo")
        hash_arquivo = calcular_hash_arquivo(arquivo)
        logger.debug(f"PROCESSAMENTO: Hash calculado: {hash_arquivo}")

        job_existente = JobProcessamentoRepository.find_by_hash(hash_arquivo)
        if job_existente:
            logger.info(f"PROCESSAMENTO: Job existente encontrado (ID: {job_existente.id}) - reutilizando arquivo")
            arquivo_a_salvar = job_existente.arquivo_original
        else:
            logger.info("PROCESSAMENTO: Novo arquivo - será salvo")
            arquivo_a_salvar = arquivo

        status_pendente = get_classifier('STATUS_JOB', 'PENDENTE')
        logger.debug(f"PROCESSAMENTO: Status pendente: {status_pendente}")

        job = JobProcessamentoRepository.create_job(
            arquivo_original=arquivo_a_salvar,
            hash_arquivo=hash_arquivo,
            empresa=empresa,
            status=status_pendente,
        )
        logger.info(f"PROCESSAMENTO: Job criado com sucesso - UUID: {job.uuid}, ID: {job.id}")

        logger.debug(f"PROCESSAMENTO: Publicando tarefa Celery para job {job.id}")
        CeleryTaskPublisher().publish_processamento_nota(job_id=job.id)
        logger.info(f"PROCESSAMENTO: Tarefa Celery publicada para job {job.id}")

        return job