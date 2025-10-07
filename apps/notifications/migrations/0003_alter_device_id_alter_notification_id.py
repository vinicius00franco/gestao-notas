from django.db import migrations
sql = open('apps/notifications/migrations/0003_alter_device_id_alter_notification_id.sql', 'r').read()

class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_add_uuid'),
    ]

    operations = [
        migrations.RunSQL(sql)
    ]
