# Generated by Django 5.1.2 on 2024-10-31 00:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_paymentdetails_email_paymentdetails_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_status',
            field=models.CharField(default='Pending', max_length=100),
            preserve_default=False,
        ),
    ]
