"""Core views for the workflow management system."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.http import JsonResponse
from django.db.models import Q
from .forms import SignUpForm, TaskForm, CommentForm, TaskSearchForm
from .models import Task, TaskCategory, Comment, TaskHistory, TaskNotification
import json


def home(request):
    """Render the home page."""
    return render(request, "core/home.html")


def signup(request):
    """Handle user registration."""
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})


@login_required
def dashboard(request):
    my_assigned_tasks = Task.objects.filter(assigned_to=request.user)
    tasks_i_assigned = Task.objects.filter(assigned_by=request.user)
    all_tasks = Task.objects.all()

    def status_count(qs, status):
        return qs.filter(status=status).count()

    my_counts = {
        "pending": status_count(my_assigned_tasks, "pending"),
        "in_progress": status_count(my_assigned_tasks, "in_progress"),
        "rejected": status_count(my_assigned_tasks, "rejected"),
        "completed": status_count(my_assigned_tasks, "completed"),
    }
    global_counts = {
        "pending": status_count(all_tasks, "pending"),
        "in_progress": status_count(all_tasks, "in_progress"),
        "rejected": status_count(all_tasks, "rejected"),
        "completed": status_count(all_tasks, "completed"),
    }

    my_data_list = [
        int(my_counts["pending"]),
        int(my_counts["in_progress"]),
        int(my_counts["rejected"]),
        int(my_counts["completed"]),
    ]
    global_data_list = [
        int(global_counts["pending"]),
        int(global_counts["in_progress"]),
        int(global_counts["rejected"]),
        int(global_counts["completed"]),
    ]
    my_data_json = json.dumps(my_data_list)
    global_data_json = json.dumps(global_data_list)

    return render(
        request,
        "core/dashboard.html",
        {
            "my_assigned_tasks": my_assigned_tasks,
            "tasks_i_assigned": tasks_i_assigned,
            "all_tasks": all_tasks,
            "my_counts": my_counts,
            "global_counts": global_counts,
            "my_data_json": my_data_json,
            "global_data_json": global_data_json,
        },
    )


@login_required
def assign_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            TaskHistory.objects.create(
                task=task,
                user=request.user,
                action="create",
                details={"type": "assign"},
            )
            return redirect("dashboard")
    else:
        form = TaskForm()
    return render(request, "core/assign_task.html", {"form": form})


@login_required
def accept_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.accept()
    TaskHistory.objects.create(
        task=task,
        user=request.user,
        action="status_change",
        details={"old": task.status, "new": "in_progress"},
    )
    return redirect("dashboard")


@login_required
def reject_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.reject()
    TaskHistory.objects.create(
        task=task,
        user=request.user,
        action="status_change",
        details={"old": task.status, "new": "rejected"},
    )
    return redirect("dashboard")


@login_required
def end_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.complete()
    TaskHistory.objects.create(
        task=task,
        user=request.user,
        action="status_change",
        details={"old": task.status, "new": "completed"},
    )
    return redirect("dashboard")


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.complete()
    return redirect("dashboard")


class TaskListView(LoginRequiredMixin, ListView):
    """View for listing tasks with advanced filtering and search."""

    model = Task
    template_name = "core/task_list.html"
    context_object_name = "tasks"

    def get_queryset(self):
        queryset = Task.objects.filter(is_template=False)
        form = TaskSearchForm(self.request.GET)

        if form.is_valid():
            query = form.cleaned_data.get("query")
            category = form.cleaned_data.get("category")
            priority = form.cleaned_data.get("priority")
            status = form.cleaned_data.get("status")

            if query:
                queryset = queryset.filter(
                    Q(title__icontains=query)
                    | Q(description__icontains=query)
                    | Q(assigned_to__username__icontains=query)
                    | Q(assigned_by__username__icontains=query)
                )
            if category:
                queryset = queryset.filter(category=category)
            if priority:
                queryset = queryset.filter(priority=priority)
            if status:
                queryset = queryset.filter(status=status)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = TaskSearchForm(self.request.GET or None)
        context["categories"] = TaskCategory.objects.all()
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """Detailed view of a task with comments and history."""

    model = Task
    template_name = "core/task_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.all().order_by("-created_at")
        context["history"] = self.object.history.all()[:10]
        context["comment_form"] = CommentForm()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Add comments to tasks."""

    model = Comment
    form_class = CommentForm
    http_method_names = ["post"]

    def form_valid(self, form):
        task = get_object_or_404(Task, pk=self.kwargs["task_id"])
        form.instance.task = task
        form.instance.author = self.request.user
        response = super().form_valid(form)

        # Create history entry for the comment
        TaskHistory.objects.create(
            task=task,
            user=self.request.user,
            action="comment",
            details={"comment_id": form.instance.id},
        )

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {
                    "status": "success",
                    "comment": {
                        "author": self.request.user.username,
                        "content": form.instance.content,
                        "created_at": form.instance.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    },
                }
            )
        return response


class TaskTemplateListView(LoginRequiredMixin, ListView):
    """View for listing task templates."""

    model = Task
    template_name = "core/template_list.html"
    context_object_name = "templates"

    def get_queryset(self):
        return Task.objects.filter(is_template=True)


class TaskFromTemplateView(LoginRequiredMixin, CreateView):
    """Create a new task from a template."""

    model = Task
    form_class = TaskForm
    template_name = "core/task_from_template.html"

    def form_valid(self, form):
        """Create a new task from the template."""
        template = get_object_or_404(
            Task, pk=self.kwargs["template_id"], is_template=True
        )
        task = template.create_from_template(
            assigned_to=form.cleaned_data["assigned_to"],
            due_date=form.cleaned_data["due_date"],
        )
        return redirect("task_detail", pk=task.pk)


@login_required
def task_priority_update(request, pk):
    """Update task priority with AJAX."""
    if request.headers.get("x-requested-with") != "XMLHttpRequest":
        return JsonResponse(
            {"status": "error", "message": "Invalid request"}, status=400
        )

    task = get_object_or_404(Task, pk=pk)
    priority = request.POST.get("priority")

    if priority not in dict(Task.PRIORITY_CHOICES):
        return JsonResponse(
            {"status": "error", "message": "Invalid priority"}, status=400
        )

    old_priority = task.priority
    task.priority = priority
    task.save()

    TaskHistory.objects.create(
        task=task,
        user=request.user,
        action="priority_change",
        details={"old": old_priority, "new": priority},
    )

    return JsonResponse(
        {
            "status": "success",
            "priority": priority,
            "score": task.calculate_priority_score(),
        }
    )


@login_required
def task_notifications(request):
    """View for user's task notifications."""
    notifications = TaskNotification.objects.filter(
        user=request.user, is_read=False
    ).order_by("-created_at")

    return render(request, "core/notifications.html", {"notifications": notifications})
