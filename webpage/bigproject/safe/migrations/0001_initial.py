# Generated by Django 3.2 on 2022-12-27 01:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AI_Model',
            fields=[
                ('model_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('version', models.CharField(max_length=200)),
                ('explain', models.TextField()),
                ('config', models.FileField(blank=True, null=True, upload_to='')),
                ('class_txt', models.FileField(blank=True, null=True, upload_to='')),
                ('Image', models.ImageField(blank=True, null=True, upload_to='')),
                ('weights', models.FileField(blank=True, null=True, upload_to='')),
            ],
        ),
        migrations.CreateModel(
            name='Alarm',
            fields=[
                ('date', models.DateTimeField(blank=True, null=True)),
                ('alarm_level', models.IntegerField()),
                ('alarm_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('group_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.group')),
                ('model_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='safe.ai_model')),
            ],
        ),
        migrations.CreateModel(
            name='Accident',
            fields=[
                ('accident_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('injury', models.IntegerField()),
                ('cause', models.TextField()),
                ('locate', models.CharField(max_length=200)),
                ('group_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='common.group')),
            ],
        ),
    ]
