from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('empresa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='minhaempresa',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='emp_uuid'),
        ),
    ]
