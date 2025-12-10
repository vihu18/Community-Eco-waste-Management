from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import Report, ReportComment
from users.models import UserApprovalNotification
from django.utils import timezone

@login_required(login_url='users:login')
def report_list(request):
    if not request.user.is_approved:
        messages.warning(request, 'Your account is pending approval.')
        return redirect('users:pending')
    
    if request.user.is_community_admin():
        reports = Report.objects.all().order_by('-created_at')
    else:
        reports = Report.objects.filter(
            Q(report_type='community') | Q(created_by=request.user)
        ).order_by('-created_at')
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    context = {
        'reports': reports,
        'status_filter': status_filter,
    }
    return render(request, 'reports/report_list.html', context)


@login_required(login_url='users:login')
@require_http_methods(["GET", "POST"])
def create_report(request):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        report_type = request.POST.get('report_type', 'community')
        location = request.POST.get('location')
        
        if not title or not description or not report_type:
            messages.error(request, 'Please fill all required fields!')
            return redirect('reports:create_report')
        
        report = Report.objects.create(
            title=title,
            description=description,
            report_type=report_type,
            location=location,
            created_by=request.user,
        )
        
        if 'photo' in request.FILES:
            report.photo = request.FILES['photo']
        
        if 'video' in request.FILES:
            report.video = request.FILES['video']
        
        report.save()
        messages.success(request, 'Report created successfully!')
        return redirect('reports:report_detail', pk=report.id)
    
    return render(request, 'reports/create_report.html')


@login_required(login_url='users:login')
def report_detail(request, pk):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    report = get_object_or_404(Report, pk=pk)
    
    if report.report_type == 'home' and report.created_by != request.user and not request.user.is_community_admin():
        messages.error(request, 'You do not have permission to view this report.')
        return redirect('reports:report_list')
    
    comments = report.comments.all()
    
    if request.method == 'POST':
        if 'comment' in request.POST:
            content = request.POST.get('comment')
            ReportComment.objects.create(
                report=report,
                user=request.user,
                content=content
            )
            messages.success(request, 'Comment added successfully!')
            return redirect('reports:report_detail', pk=report.id)
        
        elif 'resolve' in request.POST and request.user.is_community_admin():
            report.mark_resolved(request.user)
            
            if report.created_by:
                UserApprovalNotification.objects.create(
                    user=report.created_by,
                    message=f'Your report "{report.title}" has been marked as Resolved by {request.user.get_full_name()}'
                )
            
            messages.success(request, 'Report marked as resolved!')
            return redirect('reports:report_detail', pk=report.id)
    
    context = {
        'report': report,
        'comments': comments,
    }
    return render(request, 'reports/report_detail.html', context)


@login_required(login_url='users:login')
def delete_report(request, pk):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    report = get_object_or_404(Report, pk=pk)
    
    if report.created_by != request.user and not request.user.is_community_admin():
        messages.error(request, 'You do not have permission to delete this report.')
        return redirect('reports:report_list')
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Report deleted successfully!')
        return redirect('reports:report_list')
    
    context = {'report': report}
    return render(request, 'reports/confirm_delete.html', context)
