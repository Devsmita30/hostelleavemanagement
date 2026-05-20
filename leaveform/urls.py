from django.contrib import admin
from django.urls import path
from students import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='login'),

    # Student
    path('student_signup/', views.student_signup, name='student_signup'),
    path('student_login/', views.student_login, name='student_login'),
    path('student/', views.student, name='student'),
    path('apply_leave/', views.apply_leave, name='apply_leave'),
    path('track_leave/', views.track_leave, name='track_leave'),
    path('leave_history/', views.leave_history, name='leave_history'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),

    # Rector
    path('rector_login/', views.rector_login, name='rector_login'),
    path('rector/', views.rector_dashboard, name='rector'),
    path('rector_dashboard/', views.rector_dashboard, name='rector_dashboard'),
    path('rector_approve/<int:id>/', views.rector_approve, name='rector_approve'),
    path('rector_reject/<int:id>/', views.rector_reject, name='rector_reject'),
    path('verify_student/<int:id>/', views.verify_student, name='verify_student'),

    # Proctor
    path('proctor_login/', views.proctor_login, name='proctor_login'),
    path('proctor/', views.proctor_dashboard, name='proctor'),
    path('proctor_dashboard/', views.proctor_dashboard, name='proctor_dashboard'),
    path('proctor_approve/<int:id>/', views.proctor_approve, name='proctor_approve'),
    path('proctor_reject/<int:id>/', views.proctor_reject, name='proctor_reject'),

    # HOD
    path('hod_login/', views.hod_login, name='hod_login'),
    path('hod/', views.hod_dashboard, name='hod'),
    path('hod_dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('hod_approve/<int:id>/', views.hod_approve, name='hod_approve'),
    path('hod_reject/<int:id>/', views.hod_reject, name='hod_reject'),

    # Logout
    path('logout/', views.logout_view, name='logout'),

    # Gate Pass
    path('gate_pass/<int:leave_id>/', views.view_gate_pass, name='view_gate_pass'),
]
