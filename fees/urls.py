from django.urls import path
from . import views

app_name = 'fees'

urlpatterns = [
    path('all/', views.fee_list, name='fee_list'),
    path('update/<int:pk>/', views.fee_update, name='fee_update'),
    path('my/', views.student_fee_status, name='student_fee_status'),
    path('pay/', views.make_payment, name='make_payment'),
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('notifications/', views.notification_list, name='notification_list'),
]
