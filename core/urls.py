from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path("", views.home, name="home"),
    path("signup/", views.signup, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    # Dashboard and Task Management
    path("dashboard/", views.dashboard, name="dashboard"),
    path("tasks/", views.TaskListView.as_view(), name="task_list"),
    path("task/<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("assign/", views.assign_task, name="assign_task"),
    # Task Actions
    path("accept/<int:task_id>/", views.accept_task, name="accept_task"),
    path("reject/<int:task_id>/", views.reject_task, name="reject_task"),
    path("end/<int:task_id>/", views.end_task, name="end_task"),
    path(
        "task/<int:pk>/update-priority/",
        views.task_priority_update,
        name="task_priority_update",
    ),
    # Comments
    path(
        "task/<int:task_id>/comment/",
        views.CommentCreateView.as_view(),
        name="add_comment",
    ),
    # Templates
    path("templates/", views.TaskTemplateListView.as_view(), name="template_list"),
    path(
        "template/<int:template_id>/create-task/",
        views.TaskFromTemplateView.as_view(),
        name="task_from_template",
    ),
    # Categories
    path("categories/", views.task_categories, name="category_list"),
    # Notifications
    path("notifications/", views.task_notifications, name="notifications"),
]
