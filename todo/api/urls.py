from django.urls import path

from .views import TodoListView, TodoDetailApiView, redis_cashe

urlpatterns = [
    path("task-list/", TodoListView.as_view(), name="task_list"),
    path(
        "task-detail/<int:pk>/",
        TodoDetailApiView.as_view(),
        name="task_detail",
    ),
    path("test-cashing-redis/", redis_cashe, name="redis_cashe"),
]
