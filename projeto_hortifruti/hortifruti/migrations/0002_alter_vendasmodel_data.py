# Generated by Django 5.1.6 on 2025-04-02 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hortifruti', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendasmodel',
            name='data',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
