from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'created_by', 'priority', 'status', 
        'created_at', 'updated_at', 'assigned_to'
    )
    list_filter = ('status', 'priority', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'created_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    # Optional: Add bulk actions for admin
    actions = ['mark_as_resolved', 'mark_as_in_progress']

    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} complaint(s) marked as resolved.")
    mark_as_resolved.short_description = "Mark selected complaints as resolved"

    def mark_as_in_progress(self, request, queryset):
        updated = queryset.update(status='in_progress')
        self.message_user(request, f"{updated} complaint(s) marked as in progress.")
    mark_as_in_progress.short_description = "Mark selected complaints as in progress" 