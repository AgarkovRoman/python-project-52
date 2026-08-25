from django import forms
from django.contrib.auth.models import User

from tasks.models import Task


class UserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.username


class TaskForm(forms.ModelForm):
    executor = UserChoiceField(queryset=User.objects.all(), required=False, label='Исполнитель')

    class Meta:
        model = Task
        fields = ('name', 'description', 'status', 'executor', 'labels')
        labels = {
            'name': 'Имя',
            'description': 'Описание',
            'status': 'Статус',
            'labels': 'Метки',
        }
