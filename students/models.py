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

    '''student_mobile = models.CharField(max_length=10)

    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)

    parent_mobile = models.CharField(max_length=10)
    parent_email = models.EmailField()'''

    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    
class Rector(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=50)

    hostel_block = models.CharField(max_length=50)

    def __str__(self):
        return self.name

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

    #name = models.CharField(max_length=100)
    #enrollment = models.CharField(max_length=20)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    hostel = models.CharField(max_length=50)
    room = models.CharField(max_length=10)

    student_contact = models.CharField(max_length=15)
    student_email = models.EmailField()

    parent_name = models.CharField(max_length=100)
    parent_phone = models.CharField(max_length=15)

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

    def __str__(self):
        return f"{self.student.full_name} - {self.status}"