from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard(request):
    if not request.user.is_security:
        return redirect('core:home')
    return render(request, 'security/dashboard.html')
