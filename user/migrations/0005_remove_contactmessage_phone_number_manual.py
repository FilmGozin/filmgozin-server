# Generated manually to fix ContactMessage phone_number field issue

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_remove_contactmessage_phone_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactmessage',
            name='phone_number',
        ),
    ] 