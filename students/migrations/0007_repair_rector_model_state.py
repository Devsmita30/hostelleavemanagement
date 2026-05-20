from django.db import migrations, models


def drop_rector_name_if_exists(apps, schema_editor):
    Rector = apps.get_model("students", "Rector")
    table_name = Rector._meta.db_table

    existing_columns = {
        column.name
        for column in schema_editor.connection.introspection.get_table_description(
            schema_editor.connection.cursor(),
            table_name,
        )
    }

    if "name" in existing_columns:
        field = models.CharField(max_length=100, name="name")
        field.set_attributes_from_name("name")
        schema_editor.remove_field(Rector, field)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("students", "0006_repair_hod_semester"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(drop_rector_name_if_exists, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name="rector",
                    name="name",
                ),
                migrations.AlterField(
                    model_name="rector",
                    name="username",
                    field=models.CharField(max_length=50),
                ),
            ],
        ),
    ]
