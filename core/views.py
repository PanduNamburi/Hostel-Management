from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on user role
        if request.user.is_student:
            return redirect('students:dashboard')
        elif request.user.is_warden:
            return redirect('wardens:dashboard')
        elif request.user.is_admin:
            return redirect('admin_panel:dashboard')
        elif request.user.is_security:
            return redirect('security:dashboard')
    return render(request, 'core/home.html')
