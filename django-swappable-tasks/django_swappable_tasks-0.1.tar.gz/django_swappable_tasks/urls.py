from django.urls import path

from django_swappable_tasks.views import TasksHandlerView

app_name = "django_swappable_tasks"

urlpatterns = [
    path('tasks/', TasksHandlerView.as_view(), name='tasks')
]
