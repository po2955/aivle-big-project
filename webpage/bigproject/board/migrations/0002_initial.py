# Generated by Django 3.2 on 2022-12-27 01:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('board', '0001_initial'),
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notice',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.company'),
        ),
        migrations.AddField(
            model_name='notice',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
