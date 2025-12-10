from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import CustomUser, NoticeBoard, UserApprovalNotification
from reports.models import Report
from events.models import Event


def index(request):
    if request.user.is_authenticated:
        if not request.user.is_approved:
            return redirect('users:pending')
        return redirect('users:dashboard')
    
    total_users = CustomUser.objects.filter(is_approved=True, role='user').count()
    total_reports = Report.objects.filter(report_type='community').count()
    total_events = Event.objects.all().count()
    recent_reports = Report.objects.filter(report_type='community').order_by('-created_at')[:3]
    
    context = {
        'total_users': total_users,
        'total_reports': total_reports,
        'total_events': total_events,
        'recent_reports': recent_reports,
    }
    return render(request, 'users/index.html', context)


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        role = request.POST.get('role', 'user')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('users:register')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('users:register')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('users:register')
        
        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role=role,
                is_approved=False,
            )
            messages.success(request, 'Registration successful! Waiting for admin approval.')
            return redirect('users:login')
        except Exception as e:
            messages.error(request, f'Error during registration: {str(e)}')
            return redirect('users:register')
    
    return render(request, 'users/register.html')


@require_http_methods(["GET", "POST"])
def user_login(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_approved:
                messages.warning(request, 'Your account is pending admin approval. Please wait.')
                return redirect('users:pending')
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
    
    return render(request, 'users/login.html')


@login_required(login_url='users:login')
def pending_approval(request):
    if request.user.is_approved:
        return redirect('users:dashboard')
    
    return render(request, 'users/pending_approval.html')


@login_required(login_url='users:login')
def dashboard(request):
    if not request.user.is_approved:
        messages.warning(request, 'Your account is pending approval.')
        return redirect('users:pending')
    
    user_reports = Report.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    user_events = Event.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    notifications = UserApprovalNotification.objects.filter(user=request.user, is_read=False)[:5]
    
    context = {
        'user_reports': user_reports,
        'user_events': user_events,
        'notifications': notifications,
        'all_reports_count': Report.objects.filter(created_by=request.user).count(),
        'all_events_count': Event.objects.filter(created_by=request.user).count(),
    }
    return render(request, 'users/dashboard.html', context)


@login_required(login_url='users:login')
def account_profile(request):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.phone = request.POST.get('phone', request.user.phone)
        request.user.bio = request.POST.get('bio', request.user.bio)
        
        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']
        
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:account')
    
    user_reports = Report.objects.filter(created_by=request.user)
    user_events = Event.objects.filter(created_by=request.user)
    
    context = {
        'user_reports': user_reports,
        'user_events': user_events,
        'admin_info': CustomUser.objects.filter(role='admin', is_approved=True).first(),
    }
    return render(request, 'users/account.html', context)


@login_required(login_url='users:login')
def notice_board(request):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    notices = NoticeBoard.objects.all().order_by('-created_at')
    
    if request.user.is_community_admin():
        if request.method == 'POST':
            title = request.POST.get('title')
            content = request.POST.get('content')
            is_important = request.POST.get('is_important') == 'on'
            
            NoticeBoard.objects.create(
                admin=request.user,
                title=title,
                content=content,
                is_important=is_important
            )
            messages.success(request, 'Notice posted successfully!')
            return redirect('users:noticeboard')
    
    context = {'notices': notices}
    return render(request, 'users/noticeboard.html', context)


@login_required(login_url='users:login')
def settings(request):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'change_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            new_password_confirm = request.POST.get('new_password_confirm')
            
            if not request.user.check_password(old_password):
                messages.error(request, 'Old password is incorrect!')
            elif new_password != new_password_confirm:
                messages.error(request, 'New passwords do not match!')
            else:
                request.user.set_password(new_password)
                request.user.save()
                login(request, request.user)
                messages.success(request, 'Password changed successfully!')
        
        elif action == 'delete_account':
            user_id = request.user.id
            logout(request)
            CustomUser.objects.filter(id=user_id).delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('users:index')
    
    admin_info = CustomUser.objects.filter(role='admin', is_approved=True).first()
    context = {'admin_info': admin_info}
    return render(request, 'users/settings.html', context)


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('users:index')


@login_required(login_url='users:login')
@require_http_methods(["GET", "POST"])
def admin_dashboard(request):
    if not request.user.is_community_admin():
        messages.error(request, 'Access Denied! Admin only.')
        return redirect('users:dashboard')
    
    pending_users = CustomUser.objects.filter(is_approved=False).order_by('-joined_date')
    approved_users = CustomUser.objects.filter(is_approved=True, role='user').order_by('-joined_date')
    all_reports = Report.objects.all().order_by('-created_at')
    all_events = Event.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        try:
            user_to_update = CustomUser.objects.get(id=user_id)
            
            if action == 'approve':
                user_to_update.is_approved = True
                user_to_update.save()
                UserApprovalNotification.objects.create(
                    user=user_to_update,
                    message=f'Your account has been approved by {request.user.get_full_name()}!',
                    approved_by=request.user
                )
                messages.success(request, f'{user_to_update.username} has been approved!')
            
            elif action == 'reject':
                user_to_update.delete()
                messages.success(request, f'{user_to_update.username} has been rejected and deleted.')
        
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found!')
        
        return redirect('users:admin_dashboard')
    
    context = {
        'pending_users': pending_users,
        'approved_users': approved_users,
        'all_reports': all_reports,
        'all_events': all_events,
        'total_users': approved_users.count(),
        'total_pending': pending_users.count(),
    }
    return render(request, 'users/admin_dashboard.html', context)