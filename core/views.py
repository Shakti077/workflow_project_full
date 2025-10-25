
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import SignUpForm, TaskForm
from .models import Task, TaskActionLog
import json

def home(request):
    return render(request, 'core/home.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def dashboard(request):
    my_assigned_tasks = Task.objects.filter(assigned_to=request.user)
    tasks_i_assigned = Task.objects.filter(assigned_by=request.user)
    all_tasks = Task.objects.all()

    def status_count(qs, status):
        return qs.filter(status=status).count()

    my_counts = {
        'pending': status_count(my_assigned_tasks, 'pending'),
        'in_progress': status_count(my_assigned_tasks, 'in_progress'),
        'rejected': status_count(my_assigned_tasks, 'rejected'),
        'completed': status_count(my_assigned_tasks, 'completed'),
    }
    global_counts = {
        'pending': status_count(all_tasks, 'pending'),
        'in_progress': status_count(all_tasks, 'in_progress'),
        'rejected': status_count(all_tasks, 'rejected'),
        'completed': status_count(all_tasks, 'completed'),
    }

    my_data_list = [int(my_counts['pending']), int(my_counts['in_progress']), int(my_counts['rejected']), int(my_counts['completed'])]
    global_data_list = [int(global_counts['pending']), int(global_counts['in_progress']), int(global_counts['rejected']), int(global_counts['completed'])]
    my_data_json = json.dumps(my_data_list)
    global_data_json = json.dumps(global_data_list)

    return render(request, 'core/dashboard.html', {
        'my_assigned_tasks': my_assigned_tasks,
        'tasks_i_assigned': tasks_i_assigned,
        'all_tasks': all_tasks,
        'my_counts': my_counts,
        'global_counts': global_counts,
        'my_data_json': my_data_json,
        'global_data_json': global_data_json,
    })

@login_required
def assign_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            TaskActionLog.objects.create(task=task, user=request.user, action='assign')
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'core/assign_task.html', {'form': form})


@login_required
def accept_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.accept()
    TaskActionLog.objects.create(task=task, user=request.user, action='accept')
    return redirect('dashboard')

@login_required
def reject_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.reject()
    TaskActionLog.objects.create(task=task, user=request.user, action='reject')
    return redirect('dashboard')

@login_required
def end_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.complete()
    TaskActionLog.objects.create(task=task, user=request.user, action='end')
    return redirect('dashboard')

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    task.complete()
    return redirect('dashboard')
