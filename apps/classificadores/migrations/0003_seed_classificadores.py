from django.db import migrations


def create_classifiers(apps, schema_editor):
    Classificador = apps.get_model('classificadores', 'Classificador')
    entries = [
        # STATUS_JOB
        {'tipo': 'STATUS_JOB', 'codigo': 'PENDENTE', 'descricao': 'Pendente'},
        {'tipo': 'STATUS_JOB', 'codigo': 'PROCESSANDO', 'descricao': 'Processando'},
        {'tipo': 'STATUS_JOB', 'codigo': 'CONCLUIDO', 'descricao': 'Concluído'},
        {'tipo': 'STATUS_JOB', 'codigo': 'FALHA', 'descricao': 'Falha'},
        # TIPO_PARCEIRO
        {'tipo': 'TIPO_PARCEIRO', 'codigo': 'FORNECEDOR', 'descricao': 'Fornecedor'},
        {'tipo': 'TIPO_PARCEIRO', 'codigo': 'CLIENTE', 'descricao': 'Cliente'},
        # TIPO_LANCAMENTO
        {'tipo': 'TIPO_LANCAMENTO', 'codigo': 'PAGAR', 'descricao': 'A Pagar'},
        {'tipo': 'TIPO_LANCAMENTO', 'codigo': 'RECEBER', 'descricao': 'A Receber'},
        # STATUS_LANCAMENTO
        {'tipo': 'STATUS_LANCAMENTO', 'codigo': 'PENDENTE', 'descricao': 'Pendente'},
        {'tipo': 'STATUS_LANCAMENTO', 'codigo': 'PAGO', 'descricao': 'Pago'},
    ]

    for e in entries:
        Classificador.objects.create(tipo=e['tipo'], codigo=e['codigo'], descricao=e['descricao'])


def delete_classifiers(apps, schema_editor):
    Classificador = apps.get_model('classificadores', 'Classificador')
    Classificador.objects.filter(tipo__in=['STATUS_JOB', 'TIPO_PARCEIRO', 'TIPO_LANCAMENTO', 'STATUS_LANCAMENTO']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('classificadores', '0002_add_uuid'),
    ]

    operations = [
        migrations.RunPython(create_classifiers, reverse_code=delete_classifiers),
    ]
