# Generated by Django 3.2.7 on 2021-11-07 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bss', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='total',
            field=models.IntegerField(default=20, verbose_name='全ステップ数'),
        ),
    ]