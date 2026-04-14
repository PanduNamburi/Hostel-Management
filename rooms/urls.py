from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('details/', views.room_details, name='details'),
] 