import logging

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django_swappable_tasks.utils import run_task

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class TasksHandlerView(View):
    def post(self, request, *args, **kwargs):
        task = request.GET.get('task', None)
        args_json = request.GET.get('args', None)
        kwargs_json = request.GET.get('kwargs', None)

        success, result = run_task(task_path=task, args_json=args_json, kwargs_json=kwargs_json)
        return HttpResponse("Status {} Result : {}".format(success, result))

    def get(self, request, *args, **kwargs):
        task = request.GET.get('task', None)
        args_json = request.GET.get('args', None)
        kwargs_json = request.GET.get('kwargs', None)

        success, result = run_task(task_path=task, args_json=args_json, kwargs_json=kwargs_json)
        return HttpResponse("Status {} Result : {}".format(success, result))
