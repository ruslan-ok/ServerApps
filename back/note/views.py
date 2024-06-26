from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from core.views import BaseListView, BaseDetailView, BaseGroupView
from note.forms import CreateForm, EditForm
from note.get_info import get_info
from task.const import ROLE_NOTE, ROLE_APP
from task.models import Task

role = ROLE_NOTE
app = ROLE_APP[role]

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_note'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)


class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_note'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        get_info(form.instance)
        return response


class GroupView(LoginRequiredMixin, BaseGroupView):

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
