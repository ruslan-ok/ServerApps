from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Q

from core.views import BaseListView
from task.const import NUM_ROLE_TODO, ROLE_TODO, APP_HOME
from task.models import TaskInfo, Task, Step

class ListView(BaseListView):
    model = TaskInfo
    fields = {'name'}

    def __init__(self, *args, **kwargs):
        super().__init__(APP_HOME, *args, **kwargs)

    def get_queryset(self):
        data = super().get_queryset()
        if data:
            lookups = Q(stop__lte=(datetime.now() + timedelta(1))) | Q(in_my_day=True) | Q(important=True)
            svc_grp_id = int(settings.DJANGO_SERVICE_GROUP)
            return data.filter(num_role=NUM_ROLE_TODO).filter(lookups).exclude(completed=True).exclude(group_id=svc_grp_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def get_todo(request):
    svc_grp_id = int(settings.DJANGO_SERVICE_GROUP)
    days = 1
    while days < 10:
        lookups = Q(stop__lte=(datetime.now() + timedelta(days))) | Q(in_my_day=True) | Q(important=True)
        tasks = Task.objects.filter(user=request.user.id, app_task=NUM_ROLE_TODO).filter(lookups).exclude(completed=True).exclude(groups=svc_grp_id)
        if len(tasks) > 2:
            break
        days += 1
    data = [{ 
        'id': x.id, 
        'stop': x.stop, 
        'name': x.name, 
        'url': x.get_absolute_url(), 
        'group': x.get_group_name(ROLE_TODO),
        'completed': x.completed,
        'in_my_day': x.in_my_day,
        'important': x.important,
        'remind': x.remind,
        'repeat': x.repeat,
        'repeat_num': x.repeat_num,
        'repeat_days': x.repeat_days,
        'categories': x.categories,
        'info': x.info,
        'steps': get_steps(x.id),
    } for x in tasks]
    return {'result': 'ok', 'data': data, 'title': 'Actual tasks'}

def get_steps(todo_id) -> list:
    ret = []
    for step in Step.objects.filter(task=todo_id):
        ret.append({
            'id': step.id,
            'created': step.created,
            'name': step.name,
            'sort': step.sort,
            'completed': step.completed,
        })
    return ret
