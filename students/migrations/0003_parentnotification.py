# Generated manually for parent gate pass notifications.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_hod_proctor_rector_remove_student_father_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParentNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_name', models.CharField(max_length=100)),
                ('parent_phone', models.CharField(max_length=15)),
                ('message', models.TextField()),
                ('gate_pass_status', models.CharField(default='Generated', max_length=30)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(default='Sent', max_length=20)),
                ('leave', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parent_notification', to='students.leave')),
            ],
        ),
    ]
