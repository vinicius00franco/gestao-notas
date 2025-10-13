import hashlib
from .models import JobProcessamento
from .publishers import CeleryTaskPublisher
from apps.empresa.models import MinhaEmpresa
from apps.classificadores.models import get_classifier

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
        empresa = None
        if cnpj:
            cnpj_numero = cnpj_para_numero(cnpj)
            if cnpj_numero:
                try:
                    empresa = MinhaEmpresa.get_by_cnpj(cnpj_numero)
                except MinhaEmpresa.DoesNotExist:
                    # CNPJ fornecido mas empresa não existe - erro
                    raise ValueError("Empresa com CNPJ informado não encontrada")

        hash_arquivo = calcular_hash_arquivo(arquivo)
        job_existente = JobProcessamento.objects.filter(hash_arquivo=hash_arquivo).first()

        if job_existente:
            arquivo_a_salvar = job_existente.arquivo_original
        else:
            arquivo_a_salvar = arquivo

        status_pendente = get_classifier('STATUS_JOB', 'PENDENTE')
        job = JobProcessamento.objects.create(
            arquivo_original=arquivo_a_salvar,
            hash_arquivo=hash_arquivo,
            empresa=empresa,
            status=status_pendente,
        )
        CeleryTaskPublisher().publish_processamento_nota(job_id=job.id)
        return job