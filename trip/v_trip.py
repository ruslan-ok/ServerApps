from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context_ext, process_common_commands, extract_get_params
from hier.params import set_article_visible, set_article_kind
from .models import app_name, Trip, Saldo, Person, enrich_context, trip_summary
from .forms import TripForm

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def trip_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('trip:trip_list') + extract_get_params(request))

    form = None
    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            return HttpResponseRedirect(reverse('trip:trip_add'))
        if ('trip-count' in request.POST):
            do_count(request)
            return HttpResponseRedirect(reverse('trip:trip_list'))

    app_param, context = get_base_context_ext(request, app_name, 'trip', _('trips').capitalize())

    redirect = False

    if app_param.article:
        if (app_param.kind != 'trip'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Trip.objects.filter(id = app_param.art_id, user = request.user.id).exists():
            redirect = get_trip_article(request, context, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('trip:trip_list') + extract_get_params(request))

    enrich_context(context, app_param, request.user.id)
    context['trip_summary'] = trip_summary(request.user.id, False)

    data = Trip.objects.filter(user = request.user.id).order_by('-year', '-week', '-modif')
    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)

    template_file = 'trip/trip_form.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def trip_form(request, pk):
    set_article_kind(request.user, app_name, 'trip', pk)
    return HttpResponseRedirect(reverse('trip:trip_list') + extract_get_params(request))

#----------------------------------
def get_trip_article(request, context, pk):
    ed_trip = get_object_or_404(Trip, id = pk)
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            trip_delete(request, ed_trip)
            return True
        if ('trip-save' in request.POST):
            s = ed_trip.summa()
            form = TripForm(request.user,
                            request.POST,
                            instance = ed_trip,
                            initial = { 'summa': s,
                                        'day_11': request.POST.get('day_11') != None,
                                        'day_12': request.POST.get('day_12') != None,
                                        'day_13': request.POST.get('day_13') != None,
                                        'day_14': request.POST.get('day_14') != None,
                                        'day_15': request.POST.get('day_15') != None,
                                        'day_16': request.POST.get('day_16') != None,
                                        'day_17': request.POST.get('day_17') != None,
                                        'day_21': request.POST.get('day_21') != None,
                                        'day_22': request.POST.get('day_22') != None,
                                        'day_23': request.POST.get('day_23') != None,
                                        'day_24': request.POST.get('day_24') != None,
                                        'day_25': request.POST.get('day_25') != None,
                                        'day_26': request.POST.get('day_26') != None,
                                        'day_27': request.POST.get('day_27') != None,
                                        })
            if form.is_valid():
                saldo_update(request.user, ed_trip.driver, ed_trip.passenger, ed_trip.oper, -1*ed_trip.summa())
                trip = form.save(commit = False)
                trip.user = request.user
                trip.modif = datetime.now()
                trip.save()
                saldo_update(request.user, trip.driver, trip.passenger, trip.oper, trip.summa())
                return True
    else:
        ed_trip = get_object_or_404(Trip, id = pk)
        form = TripForm(request.user,
                        instance = ed_trip,
                        initial = { 'summa': ed_trip.summa(),
                                    'day_11': get_day(ed_trip.days, 1, 1),
                                    'day_12': get_day(ed_trip.days, 1, 2),
                                    'day_13': get_day(ed_trip.days, 1, 3),
                                    'day_14': get_day(ed_trip.days, 1, 4),
                                    'day_15': get_day(ed_trip.days, 1, 5),
                                    'day_16': get_day(ed_trip.days, 1, 6),
                                    'day_17': get_day(ed_trip.days, 1, 7),
                                    'day_21': get_day(ed_trip.days, 2, 1),
                                    'day_22': get_day(ed_trip.days, 2, 2),
                                    'day_23': get_day(ed_trip.days, 2, 3),
                                    'day_24': get_day(ed_trip.days, 2, 4),
                                    'day_25': get_day(ed_trip.days, 2, 5),
                                    'day_26': get_day(ed_trip.days, 2, 6),
                                    'day_27': get_day(ed_trip.days, 2, 7),
                                    })

    if not form:
        form = TripForm(instance = ed_trip)

    context['form'] = form
    context['item_id'] = ed_trip.id
    return False

#----------------------------------
def trip_add(request):
    # Инициализация полей новой записи
    last_trip = Trip.objects.filter(user = request.user.id, oper = 0).order_by('-year', '-week', '-days')[:1]
    price_new  = 0
    drvr_new = None
    pass_new = None
    debt_sum = 0
    week_new = int(datetime.now().strftime("%W")) + 1
    
    if (len(last_trip) > 0): # последняя поездка
        price_new = last_trip[0].price
        drvr_new  = last_trip[0].driver
        pass_new  = last_trip[0].passenger
    
    saldos = Saldo.objects.filter(user = request.user.id)
    for s in saldos:
        if (s.summ < 0):
            tmp = -1*s.summ
            if (debt_sum < tmp):
                debt_sum = tmp
                drvr_new = s.p2
                pass_new = s.p1
        else:
            if (debt_sum < s.summ):
                debt_sum = s.summ
                drvr_new = s.p1
                pass_new = s.p2

            form = TripForm(request.user,
                            initial = {'year':      datetime.now().year,
                                       'week':      week_new,
                                       'days':      0,
                                       'oper':      0,
                                       'price':     price_new,
                                       'driver':    drvr_new.id,
                                       'passenger': pass_new.id,
                                       'summa':     0, 
                                       'day_11': get_day(0, 1, 1),
                                       'day_12': get_day(0, 1, 2),
                                       'day_13': get_day(0, 1, 3),
                                       'day_14': get_day(0, 1, 4),
                                       'day_15': get_day(0, 1, 5),
                                       'day_16': get_day(0, 1, 6),
                                       'day_17': get_day(0, 1, 7),
                                       'day_21': get_day(0, 2, 1),
                                       'day_22': get_day(0, 2, 2),
                                       'day_23': get_day(0, 2, 3),
                                       'day_24': get_day(0, 2, 4),
                                       'day_25': get_day(0, 2, 5),
                                       'day_26': get_day(0, 2, 6),
                                       'day_27': get_day(0, 2, 7),
                                       'text':      '' })

    new_trip = Trip.objects.create(user = request.user, year = datetime.now().year, week = week_new, price = price_new, driver = drvr_new, passenger = pass_new)
    return HttpResponseRedirect(reverse('trip:trip_form', args = [new_trip.id]))

#----------------------------------
def trip_delete(request, trip):
    if Trip.objects.filter(driver = trip.id).exists() or Trip.objects.filter(passenger = trip.id).exists():
        return False

    trip.delete()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def get_me_code(_user):
    try:
        me = Person.objects.get(user = _user, me = True)
        return me.id
    except Person.DoesNotExist:
        return 0

#----------------------------------
def saldo_update(_user, _p1, _p2, _oper, _sum):
    if (_p1.id > _p2.id):
        a1 = _p2
        a2 = _p1
        sm = -1*_sum 
    else:
        a1 = _p1
        a2 = _p2
        sm = _sum 
  
    if (_oper == 1):
        sm *= -1
  
    try:
        s = Saldo.objects.get(user = _user.id, p1 = a1.id, p2 = a2.id)
        if ((s.summ + sm) == 0):
            s.delete()
        else:
            s.summ += sm
            s.save()
    except Saldo.DoesNotExist:
        me_code = get_me_code(_user)
        is_me = 0
        if (a1.id == me_code) or (a2.id == me_code):
            is_me = 1
        s = Saldo(user = _user, p1 = a1, p2 = a2, me = is_me, summ = sm)
        s.save()

#----------------------------------
def do_count(request):
    Saldo.objects.filter(user = request.user.id).delete()
    trips = Trip.objects.filter(user = request.user.id)
    for t in trips:
        saldo_update(request.user, t.driver, t.passenger, t.oper, t.summa())

  
#----------------------------------
def get_day(days, row, col):
    return ((days & (1 << (row-1) + (col-1)*2)) != 0)
