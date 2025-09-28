from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('processamento', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobprocessamento',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='jbp_uuid'),
        ),
    ]
