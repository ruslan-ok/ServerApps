from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from core.forms import BaseCreateForm, BaseEditForm
from task.models import Task, Group
from task.const import ROLE_NOTE
from core.widgets import UrlsInput, CategoriesInput

role = ROLE_NOTE

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    grp = forms.ChoiceField(
        label=_('Group'),
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=[(0, '------'),]
    )
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))
    categories = forms.CharField(
        label=_('Categories'),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add category')}))

    class Meta:
        model = Task
        fields = ['name', 'event', 'info', 'grp', 'url', 'categories', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'event': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime mb-3', 'type': 'datetime-local'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(role, *args, **kwargs)
        if ('grp' in self.fields):
            self.fields['grp'].choices = self.get_groups_hier(self.instance.user.id, role)

    def get_groups_hier(self, user_id, role):
        groups = [(0, '----------'),]
        self.get_sorted_groups(groups, user_id, role)
        return groups

    def get_sorted_groups(self, groups, user_id, role, node=None, level=0):
        node_id = None
        if node:
            node_id = node.id
        items = Group.objects.filter(user=user_id, role=role, node=node_id).order_by('sort')
        for item in items:
            if (item.determinator != 'role') and (item.determinator != 'view'):
                groups.append((item.id, level * '—' + '  ' + item.name),)
                self.get_sorted_groups(groups, user_id, role, item, level+1)

    def clean_grp(self):
        ret = None
        grp_ok = int(self.cleaned_data['grp'])
        if grp_ok:
            parent = Group.objects.filter(node=grp_ok)
            if (len(parent) > 0):
                raise  ValidationError(_('A group must not have subgroups'))
            ret = Group.objects.filter(id=grp_ok).get()
        return ret
