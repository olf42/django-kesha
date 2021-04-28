# Generated by Django 3.2 on 2021-04-28 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("kesha", "0005_parent_parent"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="parent",
            options={"ordering": ["name", "active"]},
        ),
        migrations.AlterField(
            model_name="account",
            name="parent",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="child_accounts",
                to="kesha.parent",
            ),
        ),
    ]