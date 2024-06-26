from django import forms
from django.utils.translation import gettext_lazy as _, gettext

from core.forms import BaseCreateForm, BaseEditForm
from core.widgets import DateInput, NumberInput, UrlsInput
from apart.models import PeriodServices
from task.const import APP_APART

app = APP_APART

#----------------------------------
class CreateForm(BaseCreateForm):

    class Meta:
        model = PeriodServices
        fields = ['start']

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        
#----------------------------------
class EditForm(BaseEditForm):
    start = forms.DateField(
        label=False,
        required=True,
        widget=DateInput(format='%Y-%m-%d', attrs={'label': _('Period'), 'type': 'date'}))
    bill_residents = forms.IntegerField(
        label=False,
        required=True,
        widget=NumberInput(attrs={'label': _('Number of residents'), 'step': '1'}))
    info = forms.CharField(
        label=_('Comment'),
        required=False,
        widget=forms.Textarea(attrs={'label': _('Comment'), 'class': 'form-control mb-1', 'data-autoresize':''}))
    url = forms.CharField(
        label=_('URLs'),
        required=False,
        widget=UrlsInput(attrs={'class': 'form-control mb-3', 'placeholder': _('Add link')}))

    class Meta:
        model = PeriodServices
        fields = ['start', 'bill_residents', 'info', 'url',]

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
