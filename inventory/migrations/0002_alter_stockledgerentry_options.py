# Generated by Django 4.2.20 on 2025-03-22 23:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stockledgerentry',
            options={'ordering': ['-created_at'], 'verbose_name': 'Stock Ledger Entry', 'verbose_name_plural': 'Stock Ledger Entries'},
        ),
    ]
