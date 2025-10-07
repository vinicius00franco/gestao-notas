from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID', db_column='dvc_id')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='dvc_uuid')),
                ('token', models.CharField(max_length=512, unique=True)),
                ('platform', models.CharField(blank=True, choices=[('ios', 'iOS'), ('android', 'Android')], max_length=16, null=True)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, to='auth.user')),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, to='empresa.minhaempresa')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID', db_column='ntf_id')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_column='ntf_uuid')),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('data', models.JSONField(blank=True, null=True)),
                ('delivered', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='notifications', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]