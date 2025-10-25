from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from abc import ABC, abstractmethod


class BaseTask(models.Model):
    """Abstract base class for all task types."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def calculate_priority_score(self) -> int:
        """Calculate priority score based on task attributes."""
        raise NotImplementedError(
            "Subclasses must implement calculate_priority_score()"
        )


class TaskCategory(models.Model):
    """Category for organizing tasks."""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default="#000000")  # Hex color code

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Task Categories"


class Task(BaseTask):
    """Main task model with enhanced features."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    assigned_to = models.ForeignKey(
        User, related_name="tasks", on_delete=models.CASCADE
    )
    assigned_by = models.ForeignKey(
        User, related_name="assigned_tasks", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        TaskCategory, related_name="tasks", on_delete=models.SET_NULL, null=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    due_date = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)
    is_template = models.BooleanField(default=False)
    parent_template = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="derived_tasks",
    )

    def accept(self):
        self.status = "in_progress"
        self.start_time = timezone.now()
        self.save()

    def reject(self):
        self.status = "rejected"
        self.save()

    def complete(self):
        self.status = "completed"
        self.end_time = timezone.now()
        if self.start_time:
            self.time_taken = self.end_time - self.start_time
        self.save()

    def calculate_priority_score(self) -> int:
        """Calculate priority score based on various factors."""
        score = 0
        priority_weights = {"low": 1, "medium": 2, "high": 3, "urgent": 4}

        # Base priority score
        score += priority_weights[self.priority] * 10

        # Due date factor
        if self.due_date:
            time_until_due = self.due_date - timezone.now()
            if time_until_due.days < 1:  # Due within 24 hours
                score += 20
            elif time_until_due.days < 3:  # Due within 3 days
                score += 10

        return score

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        return bool(self.due_date and timezone.now() > self.due_date)

    def create_from_template(self, assigned_to: User, due_date=None):
        """Create a new task instance from this template."""
        if not self.is_template:
            raise ValueError("This task is not a template")

        new_task = Task.objects.create(
            title=self.title,
            description=self.description,
            category=self.category,
            priority=self.priority,
            assigned_to=assigned_to,
            assigned_by=self.assigned_by,
            due_date=due_date,
            parent_template=self,
        )
        return new_task

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comments on tasks for team communication."""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class TaskObserver(ABC):
    """Abstract base class for task observers."""

    @abstractmethod
    def update(self, task: Task, action: str, user: User):
        pass


class TaskHistory(models.Model):
    """Comprehensive task history tracking."""

    ACTION_CHOICES = [
        ("create", "Created"),
        ("assign", "Assigned"),
        ("update", "Updated"),
        ("comment", "Commented"),
        ("status_change", "Status Changed"),
        ("priority_change", "Priority Changed"),
        ("due_date_change", "Due Date Changed"),
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="history")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict)  # Store detailed change information
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} by {self.user.username} on {self.task.title}"

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "Task Histories"


class TaskNotification(models.Model):
    """Notifications for task-related events."""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="notifications"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}..."
