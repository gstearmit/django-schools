# Generated by Django 3.0.4 on 2020-05-17 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0004_auto_20200418_1555'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='image',
            field=models.ImageField(blank=True, upload_to='answers/'),
        ),
        migrations.AddField(
            model_name='question',
            name='image',
            field=models.ImageField(blank=True, upload_to='questions/'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='text',
            field=models.CharField(blank=True, max_length=255, verbose_name='Answer'),
        ),
        migrations.AlterField(
            model_name='question',
            name='text',
            field=models.TextField(blank=True, verbose_name='Question'),
        ),
    ]