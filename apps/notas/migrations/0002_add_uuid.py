from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('notas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notafiscal',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='ntf_uuid'),
        ),
        migrations.AddField(
            model_name='notafiscalitem',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='nfi_uuid'),
        ),
    ]
