# Generated by Django 4.2.3 on 2023-08-02 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0004_alter_order_dt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.TextField(choices=[('new', 'Новый'), ('confirmed', 'Подтвержден'), ('assembled', 'Собран'), ('sent', 'Отправлен'), ('delivered', 'Доставлен'), ('canceled', 'Отменен')], default='new'),
        ),
    ]
