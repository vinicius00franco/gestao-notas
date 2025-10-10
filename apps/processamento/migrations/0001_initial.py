import os
from django.db import migrations

def read_sql_file(file_name):
    """Reads the specified SQL file from the migrations directory."""
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, 'r') as f:
        return f.read()

class Migration(migrations.Migration):

    initial = True
    dependencies = [
        ('empresa', '0001_initial'),
        ('classificadores', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=read_sql_file('0001_initial.sql'),
            reverse_sql="DROP TABLE IF EXISTS movimento_jobs_processamento;",
        ),
    ]