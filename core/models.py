from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)
    assigned_by = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)

    def accept(self):
        self.status = 'in_progress'
        self.start_time = timezone.now()
        self.save()

    def reject(self):
        self.status = 'rejected'
        self.save()

    def complete(self):
        self.status = 'completed'
        self.end_time = timezone.now()
        if self.start_time:
            self.time_taken = self.end_time - self.start_time
        self.save()

    def __str__(self):
        return self.title

# Optional: Action log for extra credit
class TaskActionLog(models.Model):
    ACTION_CHOICES = [
        ('assign', 'Assigned'),
        ('accept', 'Accepted'),
        ('reject', 'Rejected'),
        ('end', 'Completed'),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='actions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
