from django.db import migrations

sql = open('apps/notifications/migrations/0002_add_uuid.sql', 'r').read()

class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(sql)
    ]
