from django.db import migrations

sql = open('apps/empresa/migrations/0003_add_senha_hash.sql', 'r').read()


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0002_add_uuid'),
    ]

    operations = [
        migrations.RunSQL(sql)
    ]
