# Generated by Django 3.2 on 2023-01-03 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0003_notice_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notice',
            name='company_id',
        ),
        migrations.AddField(
            model_name='notice',
            name='locate',
            field=models.CharField(default=1, max_length=200),
            preserve_default=False,
        ),
    ]
