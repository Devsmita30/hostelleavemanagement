# Create your models here.
from django.db import models


class Student(models.Model):
    full_name = models.CharField(max_length=100)
    enrollment_no = models.CharField(max_length=12)
    email = models.EmailField()
    password = models.CharField(max_length=20)

    hostel_block = models.CharField(max_length=50)
    room_number = models.IntegerField()
    department = models.CharField(max_length=50)
    semester = models.CharField(max_length=20)

    student_mobile = models.CharField(max_length=10, blank=True, null=True)

    father_name = models.CharField(max_length=100, blank=True, null=True)
    mother_name = models.CharField(max_length=100, blank=True, null=True)

    parent_mobile = models.CharField(max_length=10, blank=True, null=True)
    parent_email = models.EmailField(blank=True, null=True)

    verified = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    
class Rector(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    hostel_block = models.CharField(max_length=50)

    def __str__(self):
        return self.username

class Proctor(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    semester = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username
    
class HOD(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    semester = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username
    
class Leave(models.Model):

    name = models.CharField(max_length=100, null=True, blank=True)
    enrollment = models.CharField(max_length=20, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    hostel = models.CharField(max_length=50)
    room = models.CharField(max_length=10)

    student_contact = models.CharField(max_length=15)
    student_email = models.EmailField()

    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(default="", blank=True, null=True)

    from_date = models.DateField()
    to_date = models.DateField()

    travel_mode = models.CharField(max_length=20)

    leave_address = models.TextField()
    city_state_pin = models.CharField(max_length=200)

    reason = models.TextField()

    rector_status = models.CharField(max_length=20, default="Pending")
    proctor_status = models.CharField(max_length=20, default="Pending")
    hod_status = models.CharField(max_length=20, default="Pending")

    status = models.CharField(max_length=20, default="Pending")

    @property
    def display_name(self):
        return self.name if self.name else self.student.full_name

    @property
    def display_enrollment(self):
        return self.enrollment if self.enrollment else self.student.enrollment_no

    def __str__(self):
        return f"{self.display_name} - {self.status}"


class ParentNotification(models.Model):
    leave = models.OneToOneField(Leave, on_delete=models.CASCADE, related_name="parent_notification")
    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)
    parent_email = models.EmailField(blank=True, null=True)
    message = models.TextField()
    gate_pass_status = models.CharField(max_length=30, default="Generated")
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Sent")

    def __str__(self):
        return f"{self.parent_name} - {self.gate_pass_status}"
