from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.widgets import AdminSplitDateTime

from hier.forms import DateInput, DateTimeInput
from .models import Apart, Meter, Bill, Price

#----------------------------------
class ApartForm(forms.ModelForm):
    class Meta:
        model = Apart
        fields = ['name', 'addr', 'active', 'has_gas', 'has_ppo']

#----------------------------------
class MeterForm(forms.ModelForm):
    reading = forms.SplitDateTimeField(widget = AdminSplitDateTime(), label = _('meters reading date').capitalize(), required = False)
    class Meta:
        model = Meter
        fields = ['period', 'reading', 'el', 'hw', 'cw', 'ga', 'info']
        widgets = { 'period': DateInput() }

#----------------------------------
class BillForm(forms.ModelForm):
    url = forms.CharField(widget = forms.TextInput(attrs = {'placeholder': _('add link').capitalize()}), required = False)
    payment = forms.SplitDateTimeField(widget = AdminSplitDateTime(), label = _('date of payment').capitalize(), required = False)
    class Meta:
        model = Bill
        fields = ['payment', 'el_pay', 'tv_bill', 'tv_pay', 'phone_bill', 'phone_pay', 'zhirovka', 'hot_pay', 'repair_pay', 'ZKX_pay', 'water_pay', 'gas_pay', 'rate', 'info', 'url', 'PoO', 'PoO_pay']
        widgets = { 'info': forms.Textarea(attrs={'rows':3, 'cols':10, 'placeholder':_('add note').capitalize(), 'data-autoresize':''}) }
        

#----------------------------------
class FileForm(forms.Form):
    upload = forms.FileField()

#----------------------------------
class PriceForm(forms.ModelForm):
    class Meta:
        model = Price
        exclude = ['apart', 'service', 'period']
        widgets = { 'start': DateInput(), 'info': forms.Textarea(attrs={'rows':3, 'cols':10, 'placeholder':_('add note').capitalize(), 'data-autoresize':''}) }

