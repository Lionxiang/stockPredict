# Generated by Django 4.1.7 on 2023-04-04 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("test2023", "0002_stocklist_delete_book"),
    ]

    operations = [
        migrations.RemoveField(model_name="stocklist", name="id",),
        migrations.AlterField(
            model_name="stocklist",
            name="stockId",
            field=models.CharField(max_length=4, primary_key=True, serialize=False),
        ),
    ]