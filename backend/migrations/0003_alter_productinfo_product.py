# Generated by Django 4.2.3 on 2023-07-28 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_productinfo_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinfo',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productinfos', to='backend.product'),
        ),
    ]