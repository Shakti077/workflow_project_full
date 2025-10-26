from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task, Comment, TaskCategory


class TaskSearchForm(forms.Form):
    """Form for searching tasks."""

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
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class TaskForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter task title'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter task description'
        })
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=TaskCategory.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    priority = forms.ChoiceField(
        choices=Task.PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )

    class Meta:
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
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = TaskCategory.objects.all()
        self.fields["category"].empty_label = "Select a category"
        self.fields["assigned_to"].empty_label = "Select assignee"


class TaskTemplateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "category", "priority"]

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_template = True
        if commit:
            instance.save()
        return instance


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Add a comment..."}
            )
        }


class TaskCategoryForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter category name'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter category description'
        })
    )
    color = forms.CharField(
        widget=forms.TextInput(attrs={
            'type': 'color',
            'class': 'form-control form-control-color',
            'title': 'Choose category color'
        })
    )

    class Meta:
        model = TaskCategory
        fields = ["name", "description", "color"]
