# Generated by Django 4.0.6 on 2022-10-30 23:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('epu', '0012_auto_20210629_1848'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='updaterbins',
            options={'verbose_name': 'Client Binary', 'verbose_name_plural': 'Client Binaries'},
        ),
        migrations.AlterField(
            model_name='pack',
            name='gitURL',
            field=models.CharField(max_length=1024, verbose_name='Git repository'),
        ),
        migrations.AlterField(
            model_name='pack',
            name='instanceZip',
            field=models.FileField(upload_to='epu/zips/', verbose_name='Instance zip'),
        ),
        migrations.AlterField(
            model_name='pack',
            name='name',
            field=models.CharField(max_length=1024, verbose_name='Display name'),
        ),
        migrations.AlterField(
            model_name='pack',
            name='slug',
            field=models.CharField(max_length=256, verbose_name='URL-friendly name'),
        ),
        migrations.AlterField(
            model_name='pack',
            name='updaterBinaries',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='epu.updaterbins', verbose_name='Client binaries'),
        ),
        migrations.AlterField(
            model_name='updaterbins',
            name='description',
            field=models.CharField(help_text='Use to record e.g. the git tag+hash the zips were built from.', max_length=160),
        ),
        migrations.AlterField(
            model_name='updaterbins',
            name='linuxZip',
            field=models.FileField(upload_to='epu/zips/', verbose_name='Linux zip'),
        ),
        migrations.AlterField(
            model_name='updaterbins',
            name='macZip',
            field=models.FileField(upload_to='epu/zips/', verbose_name='macOS zip'),
        ),
        migrations.AlterField(
            model_name='updaterbins',
            name='winZip',
            field=models.FileField(upload_to='epu/zips/', verbose_name='Windows zip'),
        ),
        migrations.AlterField(
            model_name='user',
            name='apiKey',
            field=models.CharField(blank=True, help_text='Leave blank to regenerate.', max_length=64, verbose_name='API key'),
        ),
    ]
