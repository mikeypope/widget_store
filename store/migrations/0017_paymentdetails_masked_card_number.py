# Generated by Django 5.1.2 on 2025-02-09 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_remove_product_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentdetails',
            name='masked_card_number',
            field=models.CharField(blank=True, max_length=19, null=True),
        ),
    ]
