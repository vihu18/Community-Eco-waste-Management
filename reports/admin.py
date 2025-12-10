from django.contrib import admin
from .models import Report, ReportComment

class ReportCommentInline(admin.TabularInline):
    model = ReportComment
    extra = 0

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'status', 'created_by', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['title', 'description']
    inlines = [ReportCommentInline]

@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'report', 'created_at']
    search_fields = ['user__username', 'report__title']
