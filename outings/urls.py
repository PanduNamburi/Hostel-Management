from django.urls import path
from . import views

app_name = 'outings'

urlpatterns = [
    path('', views.outing_list, name='list'),
    path('create/', views.outing_create, name='create'),
    path('<int:pk>/', views.outing_detail, name='detail'),
    path('<int:pk>/update/', views.outing_update, name='update'),
    path('<int:pk>/approve/', views.outing_approve, name='approve'),
    path('<int:pk>/return/', views.outing_return, name='return'),
    path('submit/', views.submit_outing_request, name='submit_outing'),
    path('status/', views.outing_status, name='outing_status'),
] 