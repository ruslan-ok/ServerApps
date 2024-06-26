from django import forms
from django.utils.translation import gettext_lazy as _
from core.forms import BaseCreateForm, BaseEditForm
from task.const import ROLE_TODO
from task.models import Task
#from todo.models import Item
from core.widgets import UrlsInput, CategoriesInput, CompletedInput

role = ROLE_TODO

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = Task
        #model = Item
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(role, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    completed = forms.BooleanField(label=False, required=False, 
        widget=CompletedInput(
            attrs={'class': '', 
                'label': _('Completed')}))
    add_step = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control-sm form-control small-input', 
            'placeholder': _('Next step')}), 
        required=False)
    stop = forms.DateTimeField(
        label=_('Termin'),
        required=False,
        widget=forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime d-inline-block mb-3 me-3', 'type': 'datetime-local'}))
    grp = forms.ChoiceField(
        label=_('Group'),
        widget=forms.Select(attrs={'class': 'form-control mb-3'}),
        choices=[(0, '------'),])
    categories = forms.CharField(
        label=_('Categories'),
        required=False,
        widget=CategoriesInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add category')}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))

    
    class Meta:
        model = Task
        #model = Item
        fields = ['completed', 'name', 'add_step', 'stop', 'repeat', 'repeat_num', 'repeat_days', 'remind', 
                    'info', 'grp', 'categories', 'url', 'upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'repeat': forms.Select(attrs={'class': 'form-control-sm'}),
            'repeat_num': forms.NumberInput(attrs={'class': 'form-control-sm d-inline-block'}),
            'repeat_days': forms.NumberInput(attrs={'class': 'form-control d-inline-block'}),
            'remind': forms.DateTimeInput(format='%Y-%m-%dT%H:%M', attrs={'class': 'form-control datetime d-inline-block mb-3 me-3', 'type': 'datetime-local'}),
            'info': forms.Textarea(attrs={'class': 'form-control mb-3', 'data-autoresize':''}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(role, *args, **kwargs)
