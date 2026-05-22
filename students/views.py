from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.views.decorators.http import require_POST

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


def normalize_filter_value(value):
    if value is None:
        return ''

    return str(value).strip()


def blank_student_department_filter(department):
    query = Q(student__department__isnull=True) | Q(student__department='')

    if department:
        query |= Q(student__department__iexact=department)

    return query


def blank_student_semester_filter(semester):
    query = Q(student__semester__isnull=True) | Q(student__semester='')

    if semester:
        query |= Q(student__semester__iexact=semester)

    return query


def get_role_dashboard_url(role):
    if role == 'rector':
        return 'rector_dashboard'
    if role == 'proctor':
        return 'proctor_dashboard'
    if role == 'hod':
        return 'hod_dashboard'

    return 'login'

def normalize_hostel(hostel):
    hostel = str(hostel).strip()

    if hostel.startswith("Hostel Block"):
        return hostel

    return f"Hostel Block {hostel}"

def role_leave_queryset(request):
    role = request.session.get('role')

    if role == 'rector':
        hostel = normalize_hostel(
        request.session.get('hostel_block')
    )
        return Leave.objects.filter(
        student__hostel_block__icontains=f"Block {hostel}"
    )
    if role == 'proctor':
        try:
            proctor = Proctor.objects.get(id=request.session.get('proctor_id'))
        except Proctor.DoesNotExist:
            return Leave.objects.none()

        department = normalize_filter_value(proctor.department)
        semester = normalize_filter_value(proctor.semester)

        return Leave.objects.filter(
            blank_student_department_filter(department),
            blank_student_semester_filter(semester)
        )

    if role == 'hod':
        try:
            hod = HOD.objects.get(id=request.session.get('hod_id'))
        except HOD.DoesNotExist:
            return Leave.objects.none()

        department = normalize_filter_value(hod.department)
        semester = normalize_filter_value(hod.semester)

        return Leave.objects.filter(
            blank_student_department_filter(department),
            blank_student_semester_filter(semester)
        )

    return Leave.objects.none()


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
            name=request.POST.get('name', student.full_name),
            enrollment=request.POST.get('enrollment', student.enrollment_no),
            hostel=request.POST.get('hostel', student.hostel_block),
            room=request.POST.get('room', student.room_number),
            student_email=request.POST.get('student_email', student.email),

            student_contact=request.POST.get('student_contact'),
            parent_name=request.POST.get('parent_name'),
            parent_phone=request.POST.get('parent_phone'),
            parent_email=request.POST.get('parent_email', ''),

            from_date=request.POST.get('from_date'),
            to_date=request.POST.get('to_date'),
            travel_mode=request.POST.get('travel_mode'),
            leave_address=request.POST.get('leave_address'),
            city_state_pin=request.POST.get('city_state_pin'),
            reason=request.POST.get('reason'),

            proctor_status="Pending",
            rector_status="Pending",
            hod_status="Pending",
            status="Pending"
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
            request.session['hostel_block'] = rector.hostel_block.strip()

            return redirect("rector_dashboard")

        except Rector.DoesNotExist:
            messages.error(request, "Invalid credentials")

    return render(request, "rector_login.html")


# ------------ RECTOR DASHBOARD --------------
def rector_dashboard(request):

    if request.session.get('role') != 'rector':
        return redirect("rector_login")

    hostel = normalize_hostel(
    request.session.get('hostel_block')
)
    # Students awaiting verification
    unverified_students = Student.objects.filter(
        verified=False,
        hostel_block__iexact=hostel.strip()
    )

    # All leaves for this hostel that are ready for Rector approval.
    # Route 1: Proctor approved directly.
    # Route 2: Proctor forwarded to HOD and HOD approved.
    all_leaves = Leave.objects.filter(
        student__hostel_block__icontains=hostel
    ).filter(
        Q(proctor_status="Approved") | Q(hod_status="Approved")
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
        "all_applications": role_leave_queryset(request).order_by('-id'),

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
        f"Name: {leave.display_name}\n"
        f"Enrollment No: {leave.display_enrollment}\n"
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

    notification_status = "Sent"

    if leave.parent_email:
        try:
            print("EMAIL:", leave.parent_email)
            print("FROM:", settings.EMAIL_HOST_USER)
            send_mail(
                subject=f"Gate Pass Generated for {leave.display_name}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[leave.parent_email],
                fail_silently=False,
            )
        except Exception as error:
            notification_status = "Email Failed"
            print(f"Parent email failed for leave #{leave.id}: {error}")
    else:
        notification_status = "No Email"

    ParentNotification.objects.update_or_create(
        leave=leave,
        defaults={
            "parent_name": leave.parent_name,
            "parent_phone": leave.parent_phone,
            "parent_email": leave.parent_email,
            "message": message,
            "gate_pass_status": gate_pass_status,
            "status": notification_status,
        },
    )

    # SMS/WhatsApp needs an external gateway such as Twilio or MSG91.
    # Until credentials are configured, keep a terminal log of the parent alert.
    print("\n" + "="*50)
    print(" [PARENT GATE PASS NOTIFICATION]")
    print(f" To: {leave.parent_name}")
    print(f" SMS/Message queued for mobile: {leave.parent_phone}")
    print(f" Email status: {notification_status} ({leave.parent_email or 'N/A'})")
    print("-"*50)
    print(message)
    print("="*50 + "\n")


@require_POST
def rector_approve(request, id):

    if request.session.get('role') != 'rector':
        return redirect("rector_login")

    leave = get_object_or_404(Leave, id=id)

    if leave.proctor_status != "Approved" and leave.hod_status != "Approved":
        messages.error(request, "This leave request is not ready for rector approval.")
        return redirect('rector_dashboard')

    leave.rector_status = 'Approved'
    leave.status = 'Approved'

    leave.save()

    send_parent_gate_pass_notification(leave)

    return redirect('rector_dashboard')


@require_POST
def rector_reject(request, id):

    if request.session.get('role') != 'rector':
        return redirect("rector_login")

    leave = get_object_or_404(role_leave_queryset(request), id=id)

    if leave.proctor_status != "Approved" and leave.hod_status != "Approved":
        messages.error(request, "This leave request is not ready for rector rejection.")
        return redirect('rector_dashboard')

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

    try:
        proctor = Proctor.objects.get(id=request.session.get('proctor_id'))
    except Proctor.DoesNotExist:
        request.session.flush()
        return redirect("proctor_login")

    department = normalize_filter_value(proctor.department)
    semester = normalize_filter_value(proctor.semester)

    leaves = Leave.objects.filter(
        proctor_status="Pending",
        status="Pending",
    ).filter(
        blank_student_department_filter(department),
        blank_student_semester_filter(semester)
    )

    history_leaves = Leave.objects.filter(
        blank_student_department_filter(department),
        blank_student_semester_filter(semester)
    ).exclude(
        proctor_status="Pending"
    )

    return render(request, "proctor.html", {
        "pending_leaves": leaves.order_by('-id'),
        "history_leaves": history_leaves.order_by('-id'),
        "all_applications": role_leave_queryset(request).order_by('-id'),
    })


@require_POST
def proctor_approve(request, id):

    if request.session.get('role') != 'proctor':
        return redirect("proctor_login")

    leave = get_object_or_404(role_leave_queryset(request), id=id, proctor_status="Pending", status="Pending")

    leave.proctor_status = "Approved"
    leave.rector_status = "Pending"
    leave.hod_status = "NA"

    leave.save()

    return redirect("proctor_dashboard")


@require_POST
def proctor_forward_hod(request, id):

    if request.session.get('role') != 'proctor':
        return redirect("proctor_login")

    leave = get_object_or_404(
        role_leave_queryset(request),
        id=id,
        proctor_status="Pending",
        status="Pending"
    )

    leave.proctor_status = "Forwarded"
    leave.hod_status = "Pending"

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

    try:
        hod = HOD.objects.get(id=request.session.get('hod_id'))
    except HOD.DoesNotExist:
        request.session.flush()
        return redirect("hod_login")

    department = normalize_filter_value(hod.department)
    semester = normalize_filter_value(hod.semester)

    leaves = Leave.objects.filter(
        proctor_status="Forwarded",
        hod_status="Pending",
    ).filter(
        blank_student_department_filter(department),
        blank_student_semester_filter(semester)
    )

    history_leaves = Leave.objects.filter(
        proctor_status="Forwarded"
    ).filter(
        blank_student_department_filter(department),
        blank_student_semester_filter(semester)
    ).exclude(hod_status="Pending")

    return render(request, "hod.html", {
        "escalated_leaves": leaves.order_by('-id'),
        "history_leaves": history_leaves.order_by('-id'),
        "all_applications": role_leave_queryset(request).order_by('-id'),
    })


@require_POST
def hod_approve(request, id):

    if request.session.get('role') != 'hod':
        return redirect("hod_login")

    leave = get_object_or_404(
        role_leave_queryset(request),
        id=id,
        proctor_status="Forwarded",
        hod_status="Pending",
        status="Pending",
    )

    leave.hod_status = "Approved"
    leave.rector_status = "Pending"
    leave.status = "Pending"

    leave.save()

    return redirect("hod_dashboard")


@require_POST
def hod_reject(request, id):

    if request.session.get('role') != 'hod':
        return redirect("hod_login")

    leave = get_object_or_404(
        role_leave_queryset(request),
        id=id,
        proctor_status="Forwarded",
        hod_status="Pending",
        status="Pending",
    )

    leave.hod_status = "Rejected"
    leave.rector_status = "NA"
    leave.status = "Rejected"

    leave.save()

    return redirect("hod_dashboard")


# ----------- STUDENT VERIFICATION ------------
@require_POST
def verify_student(request, id):

    if request.session.get('role') != 'rector':
        return redirect("rector_login")

    student = get_object_or_404(
        Student,
        id=id,
        hostel_block__icontains=request.session.get('hostel_block'),
    )

    student.verified = True

    student.save()

    return redirect('rector_dashboard')


# ----------- VIEW FULL LEAVE APPLICATION ------------
def view_leave_application(request, leave_id):
    role = request.session.get('role')

    if role not in ['rector', 'proctor', 'hod']:
        return redirect('login')

    leave = get_object_or_404(Leave, id=leave_id)

    return render(request, "leave_application_detail.html", {
        "leave": leave,
        "role": role,
        "back_url": get_role_dashboard_url(role),
    })


# ----------- VIEW GATE PASS ------------
def view_gate_pass(request, leave_id):
    try:
        leave = Leave.objects.get(id=leave_id)
    except Leave.DoesNotExist:
        messages.error(request, "Leave request not found.")
        return redirect("student_dashboard")

    if leave.status != "Approved":
        messages.error(request, "Gate pass is not available yet as the leave has not been approved.")
        return redirect("track_leave")

    return render(request, "gate_pass.html", {
        "leave": leave
    })
