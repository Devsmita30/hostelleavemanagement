from django.test import TestCase
from django.urls import reverse

from .models import Rector, Student
from .views import normalize_hostel


class StudentRegistrationApprovalTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            full_name="Pending Student",
            enrollment_no="12345678901",
            email="student@example.com",
            hostel_block="Hostel Block A",
            room_number=101,
            department="Computer",
            semester="1",
            password="secret1",
            verified=False,
            rejected=False,
        )
        self.rector = Rector.objects.create(
            username="rector",
            password="secret",
            hostel_block="A",
        )

    def test_pending_student_cannot_login(self):
        response = self.client.post(reverse("student_login"), {
            "enrollment_no": self.student.enrollment_no,
            "password": "secret1",
        })

        self.assertRedirects(response, reverse("student_login"))
        self.assertNotIn("student_id", self.client.session)

    def test_rector_can_verify_student_then_student_can_login(self):
        session = self.client.session
        session["role"] = "rector"
        session["rector_id"] = self.rector.id
        session["hostel_block"] = self.rector.hostel_block
        session.save()

        response = self.client.post(reverse("verify_student", args=[self.student.id]))
        self.assertRedirects(response, reverse("rector_dashboard"))

        self.student.refresh_from_db()
        self.assertTrue(self.student.verified)

        self.client.post(reverse("logout"))
        response = self.client.post(reverse("student_login"), {
            "enrollment_no": self.student.enrollment_no,
            "password": "secret1",
        })

        self.assertRedirects(response, reverse("student_dashboard"))
        self.assertEqual(self.client.session["student_id"], self.student.id)

    def test_rector_dashboard_shows_pending_students_from_all_hostels(self):
        Student.objects.create(
            full_name="Other Hostel Student",
            enrollment_no="12345678902",
            email="other@example.com",
            hostel_block="Hostel Block B",
            room_number=202,
            department="Computer",
            semester="1",
            password="secret1",
            verified=False,
            rejected=False,
        )

        session = self.client.session
        session["role"] = "rector"
        session["rector_id"] = self.rector.id
        session["hostel_block"] = self.rector.hostel_block
        session.save()

        response = self.client.get(reverse("rector_dashboard"))

        self.assertContains(response, "Pending Student")
        self.assertContains(response, "Other Hostel Student")

    def test_rector_can_view_full_student_registration_info(self):
        self.student.student_mobile = "9876543210"
        self.student.father_name = "Father Name"
        self.student.mother_name = "Mother Name"
        self.student.parent_mobile = "9876543211"
        self.student.parent_email = "parent@example.com"
        self.student.save()

        session = self.client.session
        session["role"] = "rector"
        session["rector_id"] = self.rector.id
        session["hostel_block"] = self.rector.hostel_block
        session.save()

        response = self.client.get(reverse("view_student_registration", args=[self.student.id]))

        self.assertContains(response, "Pending Student")
        self.assertContains(response, "9876543210")
        self.assertContains(response, "Father Name")
        self.assertContains(response, "parent@example.com")

    def test_rector_can_reject_student_registration(self):
        session = self.client.session
        session["role"] = "rector"
        session["rector_id"] = self.rector.id
        session["hostel_block"] = self.rector.hostel_block
        session.save()

        response = self.client.post(reverse("reject_student", args=[self.student.id]))

        self.assertRedirects(response, reverse("rector_dashboard"))
        self.student.refresh_from_db()
        self.assertFalse(self.student.verified)
        self.assertTrue(self.student.rejected)

        response = self.client.get(reverse("rector_dashboard"))
        self.assertNotContains(response, "Pending Student")

    def test_hostel_block_normalization_accepts_common_rector_values(self):
        self.assertEqual(normalize_hostel("A"), "Hostel Block A")
        self.assertEqual(normalize_hostel("Block A"), "Hostel Block A")
        self.assertEqual(normalize_hostel("Hostel Block A"), "Hostel Block A")
