# Generated by Django 4.1.7 on 2023-07-05 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_producto_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='estado',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]