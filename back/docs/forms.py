from django import forms
from django.utils.translation import gettext_lazy as _

from core.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from task.const import ROLE_DOC
from docs.config import app_config
from core.forms import GroupForm

role = ROLE_DOC

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    class Meta:
        model = Task
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

#----------------------------------
class FolderForm(GroupForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
