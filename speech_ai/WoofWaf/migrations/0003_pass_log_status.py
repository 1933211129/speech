# Generated by Django 3.2.15 on 2022-11-06 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WoofWaf', '0002_pass_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='pass_log',
            name='status',
            field=models.CharField(default=200, max_length=16),
            preserve_default=False,
        ),
    ]
