# Generated by Django 5.1.2 on 2024-11-17 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0014_order_payer_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='google_category',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
