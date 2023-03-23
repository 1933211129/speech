# Generated by Django 3.2.15 on 2022-11-06 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WoofWaf', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='pass_log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=16)),
                ('time', models.DateTimeField(max_length=32)),
                ('path', models.CharField(max_length=64)),
                ('post', models.CharField(max_length=128)),
                ('headers', models.CharField(max_length=256)),
            ],
        ),
    ]
