from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, Leave, Rector


# ------------- HOME ------------
def home(request):
    return render(request, 'login.html')


# ------------ STUDENT SIGNUP -------------
def student(request):
    return render(request, "student.html")

def student_signup(request):
    if request.method == "POST":
        Student.objects.create(
            full_name=request.POST.get('full_name'),
            enrollment_no=request.POST.get('enrollment_no'),
            email=request.POST.get('email'),
            hostel_block=request.POST.get('hostel_block'),
            room_number=request.POST.get('room_number'),
            password=request.POST.get('password')
        )
        return redirect('student_login')

    return render(request, "student_signup.html")


# ------------- STUDENT LOGIN ------------
def student_login(request):
    if request.method == "POST":
        enrollment_no = request.POST.get('enrollment_no')
        password = request.POST.get('password')

        try:
            student = Student.objects.get(enrollment_no=enrollment_no)

            if student.password != password:
                messages.error(request, "Incorrect password")
                return redirect("student_login")

            elif not student.verified:
                messages.error(request, "Wait for rector verification")
                return redirect("student_login")

            # ✅ FIXED SESSION
            request.session['student_id'] = student.id

            return redirect("student_dashboard")

        except Student.DoesNotExist:
            messages.error(request, "Student not registered")

    return render(request, "student_login.html")


# ----------------- STUDENT DASHBOARD -------------
def student_dashboard(request):
    if not request.session.get('student_id'):
        return redirect('student_login')

    return render(request, "student.html")


# ---------------- APPLY LEAVE --------------
def apply_leave(request):
    if request.method == "POST":

        student_id = request.session.get('student_id')
        student = Student.objects.get(id=student_id)

        Leave.objects.create(
            student=student,
            hostel=student.hostel_block,
            room=student.room_number,
            student_email=student.email,

            student_contact=request.POST.get('student_contact'),
            parent_name=request.POST.get('parent_name'),
            parent_phone=request.POST.get('parent_phone'),

            from_date=request.POST.get('from_date'),
            to_date=request.POST.get('to_date'),
            travel_mode=request.POST.get('travel_mode'),
            leave_address=request.POST.get('leave_address'),
            city_state_pin=request.POST.get('city_state_pin'),
            reason=request.POST.get('reason')
        )

        return redirect("student_dashboard")

    return render(request, "apply_leave.html")

def leave_history(request):
    enrollment = request.session.get('student_enrollment')

    if not enrollment:
        return redirect('student_login')

    try:
        student = Student.objects.get(enrollment_no=enrollment)
    except Student.DoesNotExist:
        return redirect('student_login')

    history = Leave.objects.filter(student=student).exclude(status="Pending")

    return render(request, "leave_history.html", {"history": history})


# ------------- TRACK LEAVE -------------------
def track_leave(request):
    enrollment = request.session.get('student_enrollment')

    if not enrollment:
        return redirect('student_login')

    try:
        student = Student.objects.get(enrollment_no=enrollment)
    except Student.DoesNotExist:
        return redirect('student_login')

    leaves = Leave.objects.filter(student=student)

    return render(request, "track_leave.html", {"leaves": leaves})


# ------------ RECTOR DASHBOARD --------------
def rector_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            rector = Rector.objects.get(username=username, password=password)

            request.session['role'] = 'rector'
            request.session['rector_id'] = rector.id
            request.session['hostel'] = rector.hostel_block

            return redirect("rector_dashboard")

        except Rector.DoesNotExist:
            messages.error(request, "Invalid credentials")

    return render(request, "rector_login.html")

def rector_dashboard(request):

    if request.session.get('role') != 'rector':
        return redirect("rector_login")

    hostel = request.session.get('hostel')

    leaves = Leave.objects.filter(
        rector_status="Pending",
        student__hostel_block=hostel
    )

    total = Leave.objects.filter(student__hostel_block=hostel).count()
    approved = Leave.objects.filter(student__hostel_block=hostel, rector_status="Approved").count()
    rejected = Leave.objects.filter(student__hostel_block=hostel, rector_status="Rejected").count()
    pending = leaves.count()
    history = Leave.objects.filter(student__hostel_block=hostel).exclude(rector_status="Pending")

    return render(request, "rector.html", {
        "pending_final": leaves,
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "history": history
    })

# --------------- APPROVE / REJECT ------------
def rector_approve(request, id):
    leave = Leave.objects.get(id=id)
    leave.rector_status = 'Approved'
    leave.save()
    return redirect('rector_dashboard')


def rector_reject(request, id):
    leave = Leave.objects.get(id=id)
    leave.status = 'Rejected'
    leave.save()
    return redirect('rector_dashboard')


# ------------ VERIFY STUDENT ------------
def verify_student(request, id):
    student = Student.objects.get(id=id)
    student.verified = True
    student.save()
    return redirect("rector_dashboard")


# ------------- LOGOUT --------------
def logout_view(request):
    request.session.flush()
    return redirect('login')

#------------- proctor -----------
def proctor_login(request):
    return render(request, "proctor_login.html")

def proctor_dashboard(request):

    if request.session.get('role') != 'proctor':
        return redirect("proctor_login")

    leaves = Leave.objects.filter(
        rector_status="Approved",
        proctor_status="Pending"
    )

    history_leaves = Leave.objects.filter(
        rector_status="Approved"
    ).exclude(proctor_status="Pending")

    return render(request, "proctor.html", {
        "pending_leaves": leaves,
        "history_leaves": history_leaves
    })

def proctor_approve(request, id):
    leave = Leave.objects.get(id=id)
    leave.proctor_status = "Approved"
    leave.save()
    return redirect("proctor_dashboard")


def proctor_reject(request, id):
    leave = Leave.objects.get(id=id)
    leave.proctor_status = "Rejected"
    leave.final_status = "Rejected"
    leave.save()
    return redirect("proctor_dashboard")

# ------------ Hod --------------
def hod_login(request):
    return render(request, "hod_login.html")

def hod_dashboard(request):

    if request.session.get('role') != 'hod':
        return redirect("hod_login")

    leaves = Leave.objects.filter(
        proctor_status="Approved",
        hod_status="Pending"
    )

    history_leaves = Leave.objects.filter(
        proctor_status="Approved"
    ).exclude(hod_status="Pending")

    return render(request, "hod.html", {
        "escalated_leaves": leaves,
        "history_leaves": history_leaves
    })

def hod_approve(request, id):
    leave = Leave.objects.get(id=id)
    leave.hod_status = "Approved"

    leave.status = "Approved"

    leave.save()
    return redirect("hod_dashboard")


def hod_reject(request, id):
    leave = Leave.objects.get(id=id)
    leave.hod_status = "Rejected"
    leave.status = "Rejected"
    leave.save()
    return redirect("hod_dashboard")