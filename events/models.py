from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True, null=True)
    event_date = models.DateField(blank=True, null=True)
    event_time = models.TimeField(blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='events/photos/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def is_past_event(self):
        if self.event_date:
            return self.event_date < timezone.now().date()
        return False


class EventAttendee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event', 'user')
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user} - {self.event}"
