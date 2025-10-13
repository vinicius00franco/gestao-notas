import os
from django.db import migrations

def read_sql_file(file_name):
    """Reads the specified SQL file from the migrations directory."""
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r') as f:
        return f.read()

def apply_sql(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        sql = read_sql_file('0001_initial.sql')
        schema_editor.execute(sql)

def unapply_sql(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        reverse_sql = "DROP TABLE IF EXISTS movimento_nota_fiscal_itens; DROP TABLE IF EXISTS movimento_notas_fiscais;"
        schema_editor.execute(reverse_sql)

class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ('processamento', '0001_initial'),
        ('parceiros', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(apply_sql, unapply_sql),
    ]