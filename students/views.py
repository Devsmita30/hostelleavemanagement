from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q

from .models import Student, Leave, Rector, ParentNotification, Proctor, HOD


# ------------- HOME ------------
def home(request):
    return render(request, 'login.html')


def get_logged_in_student(request):
    student_id = request.session.get('student_id')

    if not student_id:
        return None

    try:
        return Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return None


# ------------ STUDENT SIGNUP -------------
def student(request):
    return redirect("student_dashboard")


def student_signup(request):
    if request.method == "POST":
        Student.objects.create(
            full_name=request.POST.get('full_name'),
            enrollment_no=request.POST.get('enrollment_no'),
            email=request.POST.get('email'),
            hostel_block=request.POST.get('hostel_block'),
            room_number=request.POST.get('room_number'),
            department=request.POST.get('department', ''),
            semester=request.POST.get('semester', ''),
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
            student = Student.objects.get(
                enrollment_no=enrollment_no
            )

            if student.password != password:
                messages.error(request, "Incorrect password")
                return redirect("student_login")

            elif not student.verified:
                messages.error(request, "Wait for rector verification")
                return redirect("student_login")

            request.session['student_id'] = student.id
            request.session['student_enrollment'] = student.enrollment_no
            request.session['student_name'] = student.full_name

            return redirect("student_dashboard")

        except Student.DoesNotExist:
            messages.error(request, "Student not registered")

    return render(request, "student_login.html")


# ----------------- STUDENT DASHBOARD -------------
def student_dashboard(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect('student_login')

    leaves = Leave.objects.filter(
        student=student
    ).order_by('-id')

    return render(request, "student.html", {
        "student": student,
        "pending_count": leaves.filter(status="Pending").count(),
        "approved_count": leaves.filter(status="Approved").count(),
        "rejected_count": leaves.filter(status="Rejected").count(),
        "recent_leaves": leaves[:5],
    })


# ---------------- APPLY LEAVE --------------
def apply_leave(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect('student_login')

    if request.method == "POST":

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

        messages.success(request, "Leave request submitted successfully.")
        return redirect("track_leave")

    return render(request, "apply_leave.html", {
        "student": student
    })


# ---------------- LEAVE HISTORY ----------------
def leave_history(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect('student_login')

    history = Leave.objects.filter(
        student=student
    ).exclude(status="Pending").order_by('-id')

    return render(request, "leave_history.html", {
        "history": history
    })


# ---------------- TRACK LEAVE ----------------
def track_leave(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect('student_login')

    leaves = Leave.objects.filter(
        student=student
    ).order_by('-id')

    return render(request, "track_leave.html", {
        "leaves": leaves
    })


# ------------ RECTOR LOGIN --------------
def rector_login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            rector = Rector.objects.get(
                username=username,
                password=password
            )

            request.session['role'] = 'rector'
            request.session['rector_id'] = rector.id
            request.session['rector_name'] = rector.username
            request.session['hostel_block'] = rector.hostel_block

            return redirect("rector_dashboard")

        except Rector.DoesNotExist:
            messages.error(request, "Invalid credentials")

    return render(request, "rector_login.html")


# ------------ RECTOR DASHBOARD --------------
def rector_dashboard(request):

    if request.session.get('role') != 'rector':
        return redirect("rector_login")

    hostel = request.session.get('hostel_block')

    # Students awaiting verification
    unverified_students = Student.objects.filter(
        verified=False,
        hostel_block=hostel
    )

    # All leaves for this hostel
    all_leaves = Leave.objects.filter(
        student__hostel_block=hostel
    )

    # Pending approvals
    pending_final = all_leaves.filter(
        rector_status="Pending"
    )

    # History
    history = all_leaves.exclude(
        rector_status="Pending"
    )

    # Stats
    total = all_leaves.count()
    approved = all_leaves.filter(
        rector_status="Approved"
    ).count()

    rejected = all_leaves.filter(
        rector_status="Rejected"
    ).count()

    pending = pending_final.count()

    return render(request, "rector.html", {

        "unverified_students": unverified_students,

        "pending_final": pending_final,

        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,

        "history": history,

        "rector_name": request.session.get(
            'rector_name',
            'Rector'
        ),
    })


# --------------- APPROVE / REJECT ------------
def send_parent_gate_pass_notification(leave):

    gate_pass_status = "Generated"

    message = (
        f"Dear {leave.parent_name},\n\n"
        f"Your ward's leave request has been approved and the gate pass is {gate_pass_status}.\n\n"
        f"Student Details:\n"
        f"Name: {leave.student.full_name}\n"
        f"Enrollment No: {leave.student.enrollment_no}\n"
        f"Hostel: {leave.hostel}\n"
        f"Room: {leave.room}\n"
        f"Student Contact: {leave.student_contact}\n"
        f"Student Email: {leave.student_email}\n\n"
        f"Leave Information:\n"
        f"From: {leave.from_date}\n"
        f"To: {leave.to_date}\n"
        f"Travel Mode: {leave.travel_mode}\n"
        f"Leave Address: {leave.leave_address}, {leave.city_state_pin}\n"
        f"Reason: {leave.reason}\n\n"
        f"Gate Pass Status: {gate_pass_status}"
    )

    ParentNotification.objects.update_or_create(
        leave=leave,
        defaults={
            "parent_name": leave.parent_name,
            "parent_phone": leave.parent_phone,
            "message": message,
            "gate_pass_status": gate_pass_status,
            "status": "Sent",
        },
    )


def rector_approve(request, id):

    leave = Leave.objects.get(id=id)

    leave.rector_status = 'Approved'
    leave.status = 'Approved'

    leave.save()

    send_parent_gate_pass_notification(leave)

    return redirect('rector_dashboard')


def rector_reject(request, id):

    leave = Leave.objects.get(id=id)

    leave.rector_status = 'Rejected'
    leave.status = 'Rejected'

    leave.save()

    return redirect('rector_dashboard')


# ------------- LOGOUT --------------
def logout_view(request):

    request.session.flush()

    return redirect('login')


# ------------- PROCTOR LOGIN -------------
def proctor_login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            proctor = Proctor.objects.get(
                username=username,
                password=password
            )

            request.session['role'] = 'proctor'
            request.session['proctor_id'] = proctor.id
            request.session['proctor_username'] = proctor.username
            request.session['department'] = proctor.department
            request.session['semester'] = proctor.semester

            return redirect("proctor_dashboard")

        except Proctor.DoesNotExist:
            messages.error(request, "Invalid credentials")

    return render(request, "proctor_login.html")


# ------------- PROCTOR DASHBOARD -------------
def proctor_dashboard(request):

    if request.session.get('role') != 'proctor':
        return redirect("proctor_login")

    department = request.session.get('department')
    semester = request.session.get('semester')

    leaves = Leave.objects.filter(
        proctor_status="Pending",
        status="Pending",
        student__department=department,
        student__semester=semester
    )

    history_leaves = Leave.objects.exclude(
        proctor_status="Pending"
    )

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

    leave.save()

    return redirect("proctor_dashboard")


# ------------ HOD LOGIN --------------
def hod_login(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            hod = HOD.objects.get(
                username=username,
                password=password
            )

            request.session['role'] = 'hod'
            request.session['hod_id'] = hod.id
            request.session['hod_username'] = hod.username
            request.session['department'] = hod.department
            request.session['semester'] = hod.semester

            return redirect("hod_dashboard")

        except HOD.DoesNotExist:
            messages.error(request, "Invalid credentials")

    return render(request, "hod_login.html")


# ------------ HOD DASHBOARD --------------
def hod_dashboard(request):

    if request.session.get('role') != 'hod':
        return redirect("hod_login")

    leaves = Leave.objects.filter(
        proctor_status="Rejected",
        hod_status="Pending"
    )

    history_leaves = Leave.objects.filter(
        proctor_status="Rejected"
    ).exclude(hod_status="Pending")

    return render(request, "hod.html", {
        "escalated_leaves": leaves,
        "history_leaves": history_leaves
    })


def hod_approve(request, id):

    leave = Leave.objects.get(id=id)

    leave.hod_status = "Approved"

    leave.save()

    send_parent_gate_pass_notification(leave)

    return redirect("hod_dashboard")


def hod_reject(request, id):

    leave = Leave.objects.get(id=id)

    leave.hod_status = "Rejected"

    leave.save()

    return redirect("hod_dashboard")


# ----------- STUDENT VERIFICATION ------------
def verify_student(request, id):

    student = Student.objects.get(id=id)

    student.verified = True

    student.save()

    return redirect('rector_dashboard')
