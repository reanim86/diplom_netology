# Generated by Django 4.2.3 on 2023-08-02 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0005_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.TextField(choices=[('new', 'New'), ('confirmed', 'Confirmed'), ('assembled', 'Assambled'), ('sent', 'Sent'), ('delivered', 'Delivered'), ('canceled', 'Canceled')], default='new'),
        ),
    ]