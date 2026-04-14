from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.attendance_list, name='list'),
    path('mark/', views.mark_attendance, name='mark'),
    path('<int:pk>/', views.attendance_detail, name='detail'),
    path('<int:pk>/update/', views.attendance_update, name='update'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_attendance_sheet, name='student_attendance_sheet'),
    path('students/<int:student_id>/mark/', views.mark_attendance_for_student, name='mark_attendance_for_student'),
] 