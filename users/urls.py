from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pending-approval/', views.pending_approval, name='pending'),
    path('account/', views.account_profile, name='account'),
    path('noticeboard/', views.notice_board, name='noticeboard'),
    path('settings/', views.settings, name='settings'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
