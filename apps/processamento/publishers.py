import abc
from apps.processamento.tasks import processar_nota_fiscal_task

class PublisherInterface(abc.ABC):
    @abc.abstractmethod
    def publish_processamento_nota(self, job_id: int):
        raise NotImplementedError

class CeleryTaskPublisher(PublisherInterface):
    def publish_processamento_nota(self, job_id: int):
        processar_nota_fiscal_task.delay(job_id=job_id)
        print(f"Task para processar Job ID {job_id} enviada para a fila.")
