from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def dashboard(request):
    if not request.user.is_warden:
        return redirect('core:home')
    return render(request, 'wardens/dashboard.html')
