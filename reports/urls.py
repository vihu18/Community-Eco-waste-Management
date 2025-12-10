from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('create/', views.create_report, name='create_report'),
    path('<int:pk>/', views.report_detail, name='report_detail'),
    path('<int:pk>/delete/', views.delete_report, name='delete_report'),
]
