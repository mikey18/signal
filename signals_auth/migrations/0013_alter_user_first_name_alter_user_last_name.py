# Generated by Django 5.0.6 on 2024-07-05 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signals_auth', '0012_alter_user_first_name_alter_user_is_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=120),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=120),
        ),
    ]
