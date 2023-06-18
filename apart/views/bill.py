from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_APART, ROLE_BILL, NUM_ROLE_BILL, NUM_ROLE_METER, NUM_ROLE_SERV_VALUE
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.bill import CreateForm, EditForm
from apart.config import app_config
from apart.views.meter import next_period
from apart.calc_tarif import HSC, INTERNET, PHONE, get_bill_info, get_bill_meters

app = APP_APART
role = ROLE_BILL

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_queryset(self):
        data = super().get_queryset()
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        if not data or query:
            return data
        return data[:12]

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_BILL
        response = super().form_valid(form)
        return response
    
class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        bill = self.get_object()
        context['delete_question'] = _('delete bill').capitalize()
        if Task.objects.filter(app_apart=NUM_ROLE_BILL, task_1=bill.task_1.id, start__gt=bill.start).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because it is not the last bill').capitalize()
        context['apart_period_meters'] = get_bill_meters(bill)
        context['apart_period_services'] = Task.objects.filter(app_apart=NUM_ROLE_SERV_VALUE, task_1=self.object.task_1.id, start=self.object.start)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.name = get_bill_name(form.instance.start)
        form.instance.save()
        get_info(form.instance)
        return response

def get_info(item):
    ret = []
    bill_info = get_bill_info(item)
    ret.append({'text': '{}: {}'.format(_('accrued'), bill_info['total']['accrued']) })
    ret.append({'text': '{}: {}'.format(_('paid'), bill_info['total']['paid']) })
    item.actualize_role_info(app, role, ret)

def get_bill_name(period):
    return period.strftime('%Y.%m')

def avg_accrual(user, apart, period, service_id):
    last = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id, start__lt=period).order_by('-start')[:3]
    ret = 0
    for bill in last:
        if (service_id == INTERNET) and bill.bill_tv_bill:
            ret += bill.bill_tv_bill
        if (service_id == PHONE) and bill.bill_phone_bill:
            ret += bill.bill_phone_bill
        if (service_id == HSC) and bill.bill_zhirovka:
            ret += bill.bill_zhirovka
    if (len(last) > 0):
        ret = round(ret / len(last), 2)
    return ret

def add_bill(user, apart):
    if (len(Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id)) < 2):
        return None, _('there are no meter readings').capitalize()
    if not Task.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id).exists():
        # First bill
        prev = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id).order_by('start')[0]
        curr = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id).order_by('start')[1]
        period = curr.start
    else:
        last = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id).order_by('-start')[0]
        period = next_period(last.start)
        if not Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id, start=period).exists(): 
            return None, _('there are no meter readings for the next period').capitalize()
        prev = last.task_3
        curr = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id, start=period).get()

    internet = phone = zkx = 0
    if apart.apart_has_tv:
        internet = avg_accrual(user, apart, period, INTERNET)
    if apart.apart_has_phone:
        phone = avg_accrual(user, apart, period, PHONE)
    if apart.apart_has_zkx:
        zkx = avg_accrual(user, apart, period, HSC)
    task = Task.objects.create(user=user, app_apart=NUM_ROLE_BILL, task_1=apart, task_2=prev, task_3=curr, start=period, name=get_bill_name(period), event=datetime.now(), bill_tv_bill=internet, bill_phone_bill=phone, bill_zhirovka=zkx)
    return task, ''
