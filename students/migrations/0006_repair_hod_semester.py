from django.db import migrations, models


def add_missing_hod_semester(apps, schema_editor):
    HOD = apps.get_model("students", "HOD")
    table_name = HOD._meta.db_table

    existing_columns = {
        column.name
        for column in schema_editor.connection.introspection.get_table_description(
            schema_editor.connection.cursor(),
            table_name,
        )
    }

    if "semester" not in existing_columns:
        field = models.CharField(max_length=20, blank=True, null=True, name="semester")
        field.set_attributes_from_name("semester")
        schema_editor.add_field(HOD, field)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("students", "0005_remove_rector_name_leave_parent_email_and_more"),
    ]

    operations = [
        migrations.RunPython(add_missing_hod_semester, migrations.RunPython.noop),
    ]
