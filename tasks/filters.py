import django_filters
from django import forms
from django.contrib.auth.models import User

from labels.models import Label
from statuses.models import Status
from tasks.forms import UserChoiceField
from tasks.models import Task


class UserModelChoiceFilter(django_filters.ModelChoiceFilter):
    field_class = UserChoiceField


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ModelChoiceFilter(
        queryset=Status.objects.all(),
        label='Статус',
    )
    executor = UserModelChoiceFilter(
        queryset=User.objects.all(),
        label='Исполнитель',
    )
    labels = django_filters.ModelChoiceFilter(
        field_name='labels',
        queryset=Label.objects.all(),
        label='Метка',
    )
    self_tasks = django_filters.BooleanFilter(
        label='Только свои задачи',
        widget=forms.CheckboxInput,
        method='filter_self_tasks',
    )

    class Meta:
        model = Task
        fields = ('status', 'executor', 'labels', 'self_tasks')

    def filter_self_tasks(self, queryset, name, value):
        if value:
            return queryset.filter(author=self.request.user)
        return queryset
