from django.db import models
from django.utils import timezone
from apps.profiles.models import Profile

class Service(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='services')
    title = models.CharField(max_length=120, help_text="e.g. 1-on-1 Consultation")
    description = models.TextField(blank=True, help_text="What the client can expect")
    duration_minutes = models.PositiveIntegerField(default=30, help_text="Duration in minutes (e.g. 15, 30, 60)")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Price in USD (0 for free)")
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    instructions = models.TextField(blank=True, help_text="Preparation notes or Zoom link instructions sent upon booking")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'price']

    def __str__(self):
        return f"{self.title} ({self.duration_minutes}m) - ${self.price}"


class AvailabilityRule(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='availability_rules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField(default='09:00')
    end_time = models.TimeField(default='17:00')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ('profile', 'day_of_week')

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid / Pay on Meeting'),
        ('paid', 'Paid'),
        ('waived', 'Waived / Free'),
        ('refunded', 'Refunded'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    visitor_name = models.CharField(max_length=100)
    visitor_email = models.EmailField()
    visitor_phone = models.CharField(max_length=30, blank=True)
    notes = models.TextField(blank=True, help_text="Special requests or discussion topics")
    
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_reference = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['profile', 'start_time', 'end_time']),
            models.Index(fields=['profile', 'status']),
        ]

    def __str__(self):
        return f"Booking for {self.visitor_name} - {self.service.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

    @property
    def is_upcoming(self):
        return self.start_time >= timezone.now()

    # FIX: Explicit booking status state machine transitions
    VALID_TRANSITIONS = {
        'pending': {'confirmed', 'rejected', 'cancelled'},
        'confirmed': {'completed', 'cancelled'},
        'rejected': set(),
        'cancelled': set(),
        'completed': set(),
    }

    def can_transition_to(self, new_status):
        """
        Returns True if transition from current status to new_status is permitted.
        Disallows transitions out of terminal states (completed, cancelled, rejected).
        """
        allowed = self.VALID_TRANSITIONS.get(self.status, set())
        return new_status in allowed

