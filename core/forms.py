"""Forms for the workflow management system.

This module contains all the forms used in the workflow application for handling
tasks, categories, comments, and user authentication.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, Comment, TaskCategory


class TaskSearchForm(forms.Form):
    """Form for searching and filtering tasks.

    Provides fields for text search, category filter, status filter,
    and priority filter with styled form controls.
    """

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search tasks...",
                "class": "form-control form-control-lg",
            }
        ),
    )
    category = forms.ModelChoiceField(
        queryset=TaskCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        choices=[("", "All Status")] + list(Task.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    priority = forms.ChoiceField(
        choices=[("", "All Priorities")] + list(Task.PRIORITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class SignUpForm(UserCreationForm):
    """User registration form with email field.

    Extends Django's UserCreationForm to include an email field
    for user registration.
    """

    email = forms.EmailField()

    class Meta:
        """Form metadata."""

        model = User
        fields = ("username", "email", "password1", "password2")


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks.

    Provides fields for task creation and editing with Bootstrap styling,
    including title, description, assignee, category, priority, and due date.
    """

    title = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter task title"}
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter task description",
            }
        )
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(), widget=forms.Select(attrs={"class": "form-select"})
    )
    category = forms.ModelChoiceField(
        queryset=TaskCategory.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
        required=False,
    )
    priority = forms.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        ),
    )

    class Meta:
        """Form metadata."""

        model = Task
        fields = [
            "title",
            "description",
            "assigned_to",
            "category",
            "priority",
            "due_date",
        ]

    def __init__(self, *args, **kwargs):
        """Initialize form with customized empty labels for dropdowns."""
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = TaskCategory.objects.all()
        self.fields["category"].empty_label = "Select a category"
        self.fields["assigned_to"].empty_label = "Select assignee"


class TaskTemplateForm(forms.ModelForm):
    """Form for creating task templates.

    Allows creation of task templates with basic fields that can be
    used as a starting point for new tasks.
    """

    class Meta:
        """Form metadata."""

        model = Task
        fields = ["title", "description", "category", "priority"]

    def save(self, commit=True):
        """Save the template with is_template flag set to True."""
        instance = super().save(commit=False)
        instance.is_template = True
        if commit:
            instance.save()
        return instance


class CommentForm(forms.ModelForm):
    """Form for adding comments to tasks.

    Provides a textarea for entering comment content with
    appropriate styling and placeholder text.
    """

    class Meta:
        """Form metadata."""

        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Add a comment..."}
            )
        }


class TaskCategoryForm(forms.ModelForm):
    """Form for creating and editing task categories.

    Provides fields for category management with Bootstrap styling,
    including name, description, and color picker.
    """

    name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter category name"}
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Enter category description",
            }
        )
    )
    color = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "color",
                "class": "form-control form-control-color",
                "title": "Choose category color",
            }
        )
    )

    class Meta:
        """Form metadata."""

        model = TaskCategory
        fields = ["name", "description", "color"]
