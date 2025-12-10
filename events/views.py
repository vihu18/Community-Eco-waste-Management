from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Event, EventAttendee
from django.utils import timezone

@login_required(login_url='users:login')
def event_list(request):
    if not request.user.is_approved:
        messages.warning(request, 'Your account is pending approval.')
        return redirect('users:pending')
    
    events = Event.objects.all().order_by('-created_at')
    filter_type = request.GET.get('filter', 'upcoming')
    
    if filter_type == 'upcoming':
        events = events.filter(event_date__gte=timezone.now().date())
    elif filter_type == 'past':
        events = events.filter(event_date__lt=timezone.now().date())
    
    context = {
        'events': events,
        'filter_type': filter_type,
    }
    return render(request, 'events/event_list.html', context)


@login_required(login_url='users:login')
@require_http_methods(["GET", "POST"])
def create_event(request):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        event_date = request.POST.get('event_date')
        event_time = request.POST.get('event_time')
        duration = request.POST.get('duration')
        
        if not title or not description:
            messages.error(request, 'Title and description are required!')
            return redirect('events:create_event')
        
        event = Event.objects.create(
            title=title,
            description=description,
            location=location,
            event_date=event_date if event_date else None,
            event_time=event_time if event_time else None,
            duration=duration,
            created_by=request.user,
        )
        
        if 'photo' in request.FILES:
            event.photo = request.FILES['photo']
        
        event.save()
        messages.success(request, 'Event created successfully!')
        return redirect('events:event_detail', pk=event.id)
    
    return render(request, 'events/create_event.html')


@login_required(login_url='users:login')
def event_detail(request, pk):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    event = get_object_or_404(Event, pk=pk)
    attendees = event.attendees.all()
    is_attending = EventAttendee.objects.filter(event=event, user=request.user).exists()
    
    if request.method == 'POST':
        if 'join' in request.POST:
            if not is_attending:
                EventAttendee.objects.create(event=event, user=request.user)
                messages.success(request, 'You have joined the event!')
            else:
                messages.info(request, 'You are already attending this event.')
            return redirect('events:event_detail', pk=event.id)
        
        elif 'leave' in request.POST:
            EventAttendee.objects.filter(event=event, user=request.user).delete()
            messages.success(request, 'You have left the event!')
            return redirect('events:event_detail', pk=event.id)
    
    context = {
        'event': event,
        'attendees': attendees,
        'is_attending': is_attending,
        'attendee_count': attendees.count(),
    }
    return render(request, 'events/event_detail.html', context)


@login_required(login_url='users:login')
def delete_event(request, pk):
    if not request.user.is_approved:
        return redirect('users:pending')
    
    event = get_object_or_404(Event, pk=pk)
    
    if event.created_by != request.user and not request.user.is_community_admin():
        messages.error(request, 'You do not have permission to delete this event.')
        return redirect('events:event_list')
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('events:event_list')
    
    context = {'event': event}
    return render(request, 'events/confirm_delete.html', context)
