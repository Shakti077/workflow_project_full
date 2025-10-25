from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('assign/', views.assign_task, name='assign_task'),
    path('accept/<int:task_id>/', views.accept_task, name='accept_task'),
    path('reject/<int:task_id>/', views.reject_task, name='reject_task'),
    path('end/<int:task_id>/', views.end_task, name='end_task'),
]
