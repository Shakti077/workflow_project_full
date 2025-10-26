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
    due_date = forms.DateTimeField(
        required=False, widget=forms.DateTimeInput(attrs={"type": "datetime-local"})
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
    class Meta:
        model = TaskCategory
        fields = ["name", "description", "color"]
        widgets = {"color": forms.TextInput(attrs={"type": "color"})}
