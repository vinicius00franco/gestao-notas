# Test comment to force rebuild
import os
from django.db import migrations


def read_sql_file(file_name: str) -> str:
    path = os.path.join(os.path.dirname(__file__), file_name)
    with open(path, 'r') as f:
        return f.read()


class Migration(migrations.Migration):

    dependencies = [
        ('classificadores', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=read_sql_file('0002_initial.sql'),
            reverse_sql="""
            -- Reverse is intentionally conservative: drop only if exists
            DROP TABLE IF EXISTS geral_classificadores;
            """,
        ),
    ]
