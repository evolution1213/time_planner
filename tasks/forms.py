from django import forms
from django.utils import timezone

from .models import Category, Task


class TaskForm(forms.ModelForm):
    deadline = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.localdate,
    )

    class Meta:
        model = Task
        fields = [
            'title',
            'category',
            'description',
            'priority',
            'status',
            'deadline',
            'duration',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Назва завдання'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Опис задачі'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Наприклад, 2:00'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')
        self.fields['category'].required = False
        self.fields['category'].empty_label = 'Без категорії'
