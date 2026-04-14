from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/create/', views.room_create, name='room_create'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('rooms/<int:room_id>/edit/', views.room_edit, name='room_edit'),
    path('rooms/allocate/', views.warden_allocation_dashboard, name='allocate_room'),
    path('rooms/allocate/visual/<int:student_id>/', views.visual_room_allocation, name='visual_room_allocation'),
    path('rooms/allocate/process/', views.process_room_allocation, name='process_room_allocation'),
    path('rooms/deallocate/<int:allocation_id>/', views.deallocate_room, name='deallocate_room'),
    path('attendance/', views.attendance_management, name='attendance_management'),
    path('outings/', views.outing_approval, name='outing_approval'),
    path('complaints/', views.complaints_management, name='complaints_management'),
    path('fees/', views.fee_approval, name='fee_approval'),
    path('log-activity/', views.log_activity, name='log_activity'),
] 