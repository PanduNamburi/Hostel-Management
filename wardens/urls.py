from django.urls import path
from . import views

app_name = 'wardens'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
] 