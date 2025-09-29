import re
import logging

from apps.core.observers import Observer

logger = logging.getLogger(__name__)


class ValidacaoCNPJObserver(Observer):
    """Observer that validates CNPJ on parceiro create/update events."""

    def update(self, subject, event_type: str, **kwargs):
        if event_type == "parceiro_created_or_updated":
            parceiro = kwargs.get("parceiro")
            if parceiro is not None:
                self._validar_cnpj(parceiro)

    def _validar_cnpj(self, parceiro):
        cnpj = getattr(parceiro, "cnpj", "")
        cnpj_digits = re.sub(r"\D", "", cnpj or "")

        if len(cnpj_digits) != 14:
            logger.error("CNPJ inválido para %s: %s", getattr(parceiro, "nome", "<sem nome>"), cnpj)
            return

        try:
            valido = self._calcular_digito_verificador(cnpj_digits)
        except Exception:
            logger.exception("Erro ao validar CNPJ para %s", getattr(parceiro, "nome", "<sem nome>"))
            return

        if valido:
            logger.info("CNPJ válido para %s", getattr(parceiro, "nome", "<sem nome>"))
        else:
            logger.error("CNPJ inválido para %s: %s", getattr(parceiro, "nome", "<sem nome>"), cnpj)

    def _calcular_digito_verificador(self, cnpj: str) -> bool:
        def calcular_digito(cnpj_base, pesos):
            soma = sum(int(cnpj_base[i]) * pesos[i] for i in range(len(pesos)))
            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

        digito1 = calcular_digito(cnpj[:12], pesos1)
        digito2 = calcular_digito(cnpj[:13], pesos2)

        return cnpj[12:14] == f"{digito1}{digito2}"
