# Generated by Django 3.2 on 2023-01-02 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0002_company_workers'),
        ('emotion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emotion',
            name='company_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.company'),
        ),
    ]
