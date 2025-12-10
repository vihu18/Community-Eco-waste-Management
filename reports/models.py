from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Report(models.Model):
    REPORT_TYPE_CHOICES = (
        ('home', 'Home (Private)'),
        ('community', 'Community (Public)'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('in_progress', 'In Progress'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES, default='community')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    location = models.CharField(max_length=255, blank=True, null=True)
    photo = models.ImageField(upload_to='reports/photos/', blank=True, null=True)
    video = models.FileField(upload_to='reports/videos/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def mark_resolved(self, admin_user):
        self.status = 'resolved'
        self.resolved_by = admin_user
        self.resolved_at = timezone.now()
        self.save()


class ReportComment(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.user} on {self.report}"
