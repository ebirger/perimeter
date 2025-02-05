# Generated by Django 4.2.17 on 2025-02-02 23:30

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac_address', models.CharField(max_length=17, unique=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('hostname', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('allowed', 'Allowed'), ('blocked', 'Blocked'), ('pending', 'Pending')], default='pending', max_length=10)),
                ('first_seen', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
