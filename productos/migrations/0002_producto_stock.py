# Generated by Django 4.1.7 on 2023-07-03 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='stock',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]