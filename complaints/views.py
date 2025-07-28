from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Complaint
from .forms import ComplaintForm

@login_required
def complaint_list(request):
    # Always show only the logged-in user's complaints for students (case-insensitive)
    if hasattr(request.user, 'role') and request.user.role.lower() == 'student':
        complaints = Complaint.objects.filter(created_by=request.user)
    elif hasattr(request.user, 'role') and request.user.role.lower() == 'warden':
        complaints = Complaint.objects.filter(assigned_to=request.user) | Complaint.objects.filter(status='pending')
    else:
        complaints = Complaint.objects.all()

    paginator = Paginator(complaints, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'complaints/complaint_list.html', {
        'page_obj': page_obj,
        'is_warden': hasattr(request.user, 'role') and request.user.role.lower() == 'warden'
    })

@login_required
def complaint_create(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.created_by = request.user
            complaint.save()
            messages.success(request, 'Complaint submitted successfully.')
            return redirect('complaints:list')
    else:
        form = ComplaintForm()

    return render(request, 'complaints/complaint_form.html', {
        'form': form,
        'title': 'Submit Complaint'
    })

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.user.role == 'student' and complaint.created_by != request.user:
        messages.error(request, 'You do not have permission to view this complaint.')
        return redirect('complaints:list')

    return render(request, 'complaints/complaint_detail.html', {
        'complaint': complaint,
        'is_warden': request.user.role == 'warden'
    })

@login_required
def complaint_update(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.user.role != 'warden' and complaint.created_by != request.user:
        messages.error(request, 'You do not have permission to update this complaint.')
        return redirect('complaints:list')

    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, 'Complaint updated successfully.')
            return redirect('complaints:detail', pk=pk)
    else:
        form = ComplaintForm(instance=complaint)

    return render(request, 'complaints/complaint_form.html', {
        'form': form,
        'title': 'Update Complaint'
    })

@login_required
def complaint_resolve(request, pk):
    if request.user.role != 'warden':
        messages.error(request, 'Only wardens can resolve complaints.')
        return redirect('complaints:list')

    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        resolution_notes = request.POST.get('resolution_notes')
        
        complaint.status = status
        complaint.resolution_notes = resolution_notes
        complaint.assigned_to = request.user
        complaint.save()
        
        messages.success(request, 'Complaint status updated successfully.')
        return redirect('complaints:detail', pk=pk)

    return render(request, 'complaints/complaint_resolve.html', {
        'complaint': complaint
    }) 