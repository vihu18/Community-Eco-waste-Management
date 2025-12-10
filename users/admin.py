from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserApprovalNotification, NoticeBoard

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'role', 'is_approved', 'joined_date']
    list_filter = ['role', 'is_approved', 'joined_date']
    search_fields = ['username', 'email', 'first_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_approved', 'phone', 'address', 'bio', 'profile_picture')}),
    )
    actions = ['approve_users', 'reject_users']  # ⭐ ADD THIS
    
    # ⭐ ADD THESE TWO METHODS
    def approve_users(self, request, queryset):
        """Bulk approve users"""
        approved_count = 0
        for user in queryset:
            if not user.is_approved:
                user.is_approved = True
                user.save()
                # Create notification
                UserApprovalNotification.objects.create(
                    user=user,
                    message=f'Your account has been approved by {request.user.get_full_name() or "Admin"}!',
                    approved_by=request.user
                )
                approved_count += 1
        
        self.message_user(request, f'{approved_count} user(s) approved successfully!')
    
    approve_users.short_description = '✅ Approve selected users'
    
    def reject_users(self, request, queryset):
        """Bulk reject users"""
        rejected_count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{rejected_count} user(s) rejected and deleted!')
    
    reject_users.short_description = '❌ Reject selected users'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserApprovalNotification)
admin.site.register(NoticeBoard)
