class NotaFiscalValidator:
    def validate_cnpj_match(self, dados_extraidos, minha_empresa):
        if minha_empresa is None:
            return  # Skip validation if no empresa provided
        is_remetente = dados_extraidos.remetente_cnpj == minha_empresa.cnpj
        is_destinatario = dados_extraidos.destinatario_cnpj == minha_empresa.cnpj
        if not is_remetente and not is_destinatario:
            raise ValueError("Nota fiscal não pertence à sua empresa (CNPJ não corresponde).")