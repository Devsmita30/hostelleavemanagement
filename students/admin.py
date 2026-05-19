from django.contrib import admin
from .models import Student, Leave, Rector, Proctor, HOD, ParentNotification

# Register your models here.
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'enrollment_no', 'email', 'hostel_block', 'room_number', 'verified']
    search_fields = ['full_name', 'enrollment_no', 'email']
    list_filter = ['verified', 'hostel_block']

@admin.register(Leave)
class LeaveAdmin(admin.ModelAdmin):
    list_display = ['student', 'from_date', 'to_date', 'rector_status', 'proctor_status', 'hod_status', 'status']
    search_fields = ['student__full_name', 'student__enrollment_no']
    list_filter = ['status', 'rector_status', 'proctor_status', 'hod_status']

@admin.register(Rector)
class RectorAdmin(admin.ModelAdmin):
    list_display = ['username', 'hostel_block']
    search_fields = ['username']

@admin.register(Proctor)
class ProctorAdmin(admin.ModelAdmin):
    list_display = ['username', 'department', 'semester']
    search_fields = ['username', 'department']

@admin.register(HOD)
class HODAdmin(admin.ModelAdmin):
    list_display = ['username', 'department']
    search_fields = ['username', 'department']

@admin.register(ParentNotification)
class ParentNotificationAdmin(admin.ModelAdmin):
    list_display = ['leave', 'parent_name', 'parent_phone', 'gate_pass_status', 'status', 'sent_at']
    search_fields = ['leave__student__full_name', 'leave__student__enrollment_no', 'parent_name', 'parent_phone']
    list_filter = ['gate_pass_status', 'status', 'sent_at']
