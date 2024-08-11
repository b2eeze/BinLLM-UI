# Generated by Django 5.0.8 on 2024-08-11 02:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("User", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Firmwares",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("local_url", models.CharField(blank=True, max_length=255)),
                ("file_name", models.CharField(blank=True, max_length=255)),
                ("size", models.IntegerField(blank=True, null=True)),
                ("user", models.CharField(default="default", max_length=255)),
                ("hash_value", models.CharField(blank=True, max_length=255, null=True)),
                ("taint_label", models.IntegerField(blank=True, null=True)),
                ("call_chain", models.TextField(default="no call chain yet")),
                ("checksec", models.TextField(default="checksec error")),
                ("md_path", models.CharField(blank=True, max_length=255)),
                ("json_path", models.CharField(blank=True, max_length=255)),
                ("dc_path", models.CharField(blank=True, max_length=255)),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="Create time"),
                ),
                (
                    "update_time",
                    models.DateTimeField(auto_now=True, verbose_name="Update time"),
                ),
                (
                    "delete_time",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Delete time"
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_firmwares",
                        to="User.user",
                    ),
                ),
            ],
        ),
    ]
