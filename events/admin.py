from django.contrib import admin
from .models import Event, EventAttendee

class EventAttendeeInline(admin.TabularInline):
    model = EventAttendee
    extra = 0

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'event_time', 'created_by', 'created_at']
    list_filter = ['event_date', 'created_at']
    search_fields = ['title', 'description']
    inlines = [EventAttendeeInline]

@admin.register(EventAttendee)
class EventAttendeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'joined_at']
    search_fields = ['user__username', 'event__title']
