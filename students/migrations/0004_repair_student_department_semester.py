from django.db import migrations, models


def add_missing_student_columns(apps, schema_editor):
    Student = apps.get_model("students", "Student")
    table_name = Student._meta.db_table

    existing_columns = {
        column.name
        for column in schema_editor.connection.introspection.get_table_description(
            schema_editor.connection.cursor(),
            table_name,
        )
    }

    fields_to_add = [
        models.CharField(max_length=50, default="", name="department"),
        models.CharField(max_length=20, default="", name="semester"),
    ]

    for field in fields_to_add:
        if field.name not in existing_columns:
            field.set_attributes_from_name(field.name)
            schema_editor.add_field(Student, field)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("students", "0003_parentnotification"),
    ]

    operations = [
        migrations.RunPython(add_missing_student_columns, migrations.RunPython.noop),
    ]
