from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Community Member'),
        ('admin', 'Community Head (Admin)'),
    )
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_approved = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    community_name = models.CharField(max_length=255, blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-joined_date']
        verbose_name_plural = "Users"
    
    def __str__(self):
        return f"{self.get_full_name() or self.username}"
    
    def is_community_admin(self):
        return self.role == 'admin' and self.is_approved
    
    def is_active_user(self):
        return self.is_approved and self.is_active


class UserApprovalNotification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='approval_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='approvals_given')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}"


class NoticeBoard(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notices_posted')
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_important = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
