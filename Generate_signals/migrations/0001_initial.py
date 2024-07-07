# Generated by Django 5.0.4 on 2024-06-20 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Trade_History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('symbol', models.CharField(max_length=100)),
                ('stop_loss', models.FloatField()),
                ('take_profit', models.FloatField()),
                ('price', models.FloatField()),
                ('type', models.CharField(max_length=100)),
                ('result', models.CharField(blank=True, choices=[('profit', 'profit'), ('loss', 'loss')], max_length=15)),
            ],
        ),
    ]
