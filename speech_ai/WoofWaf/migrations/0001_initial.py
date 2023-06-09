# Generated by Django 3.0 on 2023-04-02 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Black_List',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=16)),
                ('prohibit_time', models.DateTimeField(max_length=32)),
                ('access_time', models.DateTimeField(max_length=32)),
                ('prohibit_span', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='defend_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=16)),
                ('time', models.DateTimeField(max_length=32)),
                ('type', models.CharField(max_length=32)),
                ('rule', models.CharField(max_length=32)),
                ('path', models.CharField(max_length=1256)),
                ('address', models.CharField(default='', max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='ip_list',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=16, unique=True)),
                ('frequency', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('status', models.SmallIntegerField(choices=[(1, 'Black'), (0, 'White'), (2, 'Temporary'), (3, 'None')])),
                ('description', models.CharField(default='暂无', max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='pass_log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=16)),
                ('status', models.CharField(max_length=16)),
                ('time', models.DateTimeField(max_length=32)),
                ('path', models.CharField(max_length=1023)),
                ('post', models.CharField(max_length=128)),
                ('headers', models.CharField(max_length=1023)),
            ],
        ),
        migrations.CreateModel(
            name='waf_admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(default='admin', max_length=30, unique=True)),
                ('password', models.CharField(default='admin', max_length=128)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
