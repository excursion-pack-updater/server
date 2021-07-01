# Generated by Django 3.2.4 on 2021-06-29 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('epu', '0011_alter_user_apikey'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpdaterBins',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('description', models.CharField(max_length=160)),
                ('winZip', models.FileField(upload_to='epu/zips/')),
                ('macZip', models.FileField(upload_to='epu/zips/')),
                ('linuxZip', models.FileField(upload_to='epu/zips/')),
            ],
            options={
                'verbose_name': 'Updater Binary',
                'verbose_name_plural': 'Updater Binaries',
            },
        ),
        migrations.AlterField(
            model_name='pack',
            name='updaterBinaries',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='epu.updaterbins'),
        ),
    ]
