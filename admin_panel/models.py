from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Room(models.Model):
    ROOM_TYPES = [
        ('SINGLE', 'Single Occupancy'),
        ('DOUBLE', 'Double Occupancy'),
        ('TRIPLE', 'Triple Occupancy'),
        ('QUAD', 'Quad Occupancy'),
    ]
    
    ROOM_STATUS = [
        ('AVAILABLE', 'Available'),
        ('OCCUPIED', 'Occupied'),
        ('MAINTENANCE', 'Under Maintenance'),
    ]
    
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    capacity = models.PositiveIntegerField()
    current_occupancy = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='AVAILABLE')
    floor = models.PositiveIntegerField()
    block = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.room_number} - {self.get_room_type_display()}"

    class Meta:
        ordering = ['block', 'floor', 'room_number']

class RoomAllocation(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='allocations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_allocations')
    allocated_from = models.DateField()
    allocated_till = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.room.room_number}"

    class Meta:
        ordering = ['-allocated_from']
