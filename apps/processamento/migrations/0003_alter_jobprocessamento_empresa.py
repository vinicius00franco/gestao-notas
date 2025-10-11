# Generated manually for making empresa nullable

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processamento', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobprocessamento',
            name='empresa',
            field=models.ForeignKey(blank=True, db_column='emp_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='jobs', to='empresa.minhaempresa'),
        ),
    ]