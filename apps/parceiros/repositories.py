from apps.parceiros.models import Parceiro

class ParceiroRepository:
    def get_or_create(self, cnpj: str, nome: str, clf_tipo) -> Parceiro:
        parceiro, created = Parceiro.objects.get_or_create(
            cnpj=cnpj,
            defaults={'nome': nome, 'clf_tipo': clf_tipo}
        )
        if not created:
            update_fields = []
            if parceiro.nome != nome:
                parceiro.nome = nome
                update_fields.append('nome')
            if parceiro.clf_tipo_id != clf_tipo.id:
                parceiro.clf_tipo = clf_tipo
                update_fields.append('clf_tipo')
            if update_fields:
                parceiro.save(update_fields=update_fields)
        return parceiro