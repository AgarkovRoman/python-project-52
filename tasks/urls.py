from django.urls import path

from tasks import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='tasks_list'),
    path('create/', views.TaskCreateView.as_view(), name='tasks_create'),
    path('<int:pk>/update/', views.TaskUpdateView.as_view(), name='tasks_update'),
    path('<int:pk>/delete/', views.TaskDeleteView.as_view(), name='tasks_delete'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='tasks_detail'),
]
