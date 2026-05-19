"""
URL configuration for leaveform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from students import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='login'),

    # Student
    path('student_signup/', views.student_signup, name='student_signup'),
    path('student_login/', views.student_login, name='student_login'),
    path('student/', views.student, name='student_dashboard'),
    path('apply_leave/', views.apply_leave, name='apply_leave'),
    path('track_leave/', views.track_leave, name='track_leave'),
    path('leave_history/', views.leave_history, name='leave_history'),

    # Rector
    path('rector_login/', views.rector_login, name='rector_login'),
    path('rector/', views.rector_dashboard, name='rector'),
    path('rector_dashboard/', views.rector_dashboard, name='rector_dashboard'),
    path('rector_approve/<int:id>/', views.rector_approve, name='rector_approve'),
    path('rector_reject/<int:id>/', views.rector_reject, name='rector_reject'),

    #proctor
    path('proctor/', views.proctor_dashboard, name='proctor'),
    path('proctor_dashboard/', views.proctor_dashboard, name='proctor_dashboard'),
    path('proctor_login/', views.proctor_login, name='proctor_login'),
    path('proctor_approve/<int:id>',views.proctor_approve,name='proctor_approve'),
    path('proctor_reject/<int:id>',views.proctor_reject,name='proctor_reject'),

    #hod
    path('hod_login/', views.hod_login, name='hod_login'),
    path('hod/', views.hod_dashboard, name='hod'),
    path('hod_dashboard/',views.hod_dashboard,name='hod_dashboard'),

    # Logout
    path('logout/', views.logout_view, name='logout'),

    #verification
    path('verify_student/<int:id>/', views.verify_student, name='verify_student'),
]