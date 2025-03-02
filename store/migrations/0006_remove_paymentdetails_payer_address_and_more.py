# Generated by Django 5.1.2 on 2024-10-30 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_cart_order_is_processed_cartitem_paymentdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentdetails',
            name='payer_address',
        ),
        migrations.AddField(
            model_name='paymentdetails',
            name='city',
            field=models.CharField(default='Malibu', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentdetails',
            name='state',
            field=models.CharField(default='CA', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentdetails',
            name='street_address',
            field=models.CharField(default='123 Main Street', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paymentdetails',
            name='zip_code',
            field=models.CharField(default='90265', max_length=10),
            preserve_default=False,
        ),
    ]
