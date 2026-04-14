from django.contrib import admin
from .models import Room, RoomAllocation

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'capacity', 'current_occupancy', 'status', 'block', 'floor')
    list_filter = ('room_type', 'status', 'block', 'floor')
    search_fields = ('room_number', 'block')
    ordering = ('block', 'floor', 'room_number')

@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'allocated_from', 'allocated_till', 'is_active')
    list_filter = ('is_active', 'allocated_from', 'allocated_till')
    search_fields = ('student__username', 'room__room_number')
    ordering = ('-allocated_from',)
