from datetime import datetime
from decimal import *
from django.utils.translation import gettext_lazy as _
from task.models import Task
from task.const import NUM_ROLE_PRICE, NUM_ROLE_METER_PROP, NUM_ROLE_METER_VALUE
from apart.models import ApartMeter, PeriodMeters, MeterValue
from apart.const import *

def used(bill, service_id):
    excl = service_excluded(bill, service_id)
    if excl:
        return False
    apart = bill.task_1
    if (service_id == ELECTRICITY):
        return apart.apart_has_el
    if (service_id == GAS):
        return apart.apart_has_gas
    if (service_id == WATER):
        return apart.apart_has_cw
    if (service_id == POO):
        return apart.apart_has_ppo
    if (service_id == INTERNET):
        return apart.apart_has_tv
    if (service_id == PHONE):
        return apart.apart_has_phone
    if (service_id == HSC):
        return apart.apart_has_zkx
    return False

def get_tarif(bill, service_id):
    ret = {'t1': 0,
           'b1': 0,
           't2': 0,
           'b2': 0,
           't3': 0}

    tarifs = Task.objects.filter(user=bill.user.id, app_apart=NUM_ROLE_PRICE, task_1=bill.task_1.id, price_service=service_id, start__lte=bill.start).order_by('-start')[:1]

    if (len(tarifs) > 0):
      
        if tarifs[0].price_tarif:
            ret['t1'] = tarifs[0].price_tarif
        else:
            ret['t1'] = 0
      
        if tarifs[0].price_border:
            ret['b1'] = tarifs[0].price_border
        else:
            ret['b1'] = 0
      
        if tarifs[0].price_tarif2:
            ret['t2'] = tarifs[0].price_tarif2
        else:
            ret['t2'] = 0
      
        if tarifs[0].price_border2:
            ret['b2'] = tarifs[0].price_border2
        else:
            ret['b2'] = 0
      
        if tarifs[0].price_tarif3:
            ret['t3'] = tarifs[0].price_tarif3
        else:
            ret['t3'] = 0
  
    return ret

def check_none(value):
    if not value:
        return 0
    return value

def get_consumption(bill, resource_id):
    prev = bill.task_2
    curr = bill.task_3
    if (not prev) or (not curr):
        return 0
    if (resource_id == ELECTRICITY):
        return check_none(curr.meter_el) - check_none(prev.meter_el)
    if (resource_id == GAS):
        return check_none(curr.meter_ga) - check_none(prev.meter_ga)
    if (resource_id == COLD_WATER):
        return check_none(curr.meter_cw) - check_none(prev.meter_cw)
    if (resource_id == HOT_WATER):
        return check_none(curr.meter_hw) - check_none(prev.meter_hw)
    return 0

def get_accrued(bill, service_id):
    if (service_id == INTERNET):
        return check_none(bill.bill_tv_bill)
    if (service_id == PHONE):
        return check_none(bill.bill_phone_bill)
    if (service_id == HSC):
        return check_none(bill.bill_zhirovka)
    if (service_id == POO):
        return check_none(bill.bill_poo)
    return 0

def get_paid(bill, service_id):
    if (service_id == ELECTRICITY):
        return check_none(bill.bill_el_pay)
    if (service_id == GAS):
        return check_none(bill.bill_gas_pay)
    if (service_id == WATER):
        return check_none(bill.bill_water_pay)
    if (service_id == INTERNET):
        return check_none(bill.bill_tv_pay)
    if (service_id == PHONE):
        return check_none(bill.bill_phone_pay)
    if (service_id == HSC):
        return check_none(bill.bill_zkx_pay)
    if (service_id == POO):
        return check_none(bill.bill_poo_pay)
    return 0

def get_service_amount(bill, service_id):
    if not used(bill, service_id):
        return False, 0, 0, 0
    if (service_id in (INTERNET, PHONE, HSC, POO)):
        return True, 0, get_accrued(bill, service_id), get_paid(bill, service_id)
    if (service_id != WATER):
        tar = get_tarif(bill, service_id)
        consump = get_consumption(bill, service_id)
        if (tar['b1'] == 0) or (consump <= tar['b1']):
            accrued = consump * tar['t1']
        else:
            i_sum = tar['b1'] * tar['t1']
            if (tar['b2'] == 0) or (consump <= tar['b2']):
                accrued = i_sum + (consump - tar['b1']) * tar['t2']
            else:
                accrued = i_sum + (tar['b2'] - tar['b1']) * tar['t2'] + (consump - tar['b2']) * tar['t3']
        tarif = 0
        if consump:
            tarif = accrued / consump
    else:
        water_tarif = get_tarif(bill, WATER_SUPPLY)
        sewer_tarif = get_tarif(bill, SEWERAGE)
        cold_water_consump = get_consumption(bill, COLD_WATER)
        hot_water_consump = get_consumption(bill, HOT_WATER)
        water_consump = cold_water_consump + hot_water_consump
        residents = 1
        if bill.bill_residents:
            residents = bill.bill_residents
        pers_consump = Decimal(water_consump / residents)
        water_accrued = water_tarif['t1'] * pers_consump
        sewer_accrued = sewer_tarif['t1'] * pers_consump
        pers_accrued = round(water_accrued, 2) + round(sewer_accrued, 2)
        accrued = 0
        if pers_accrued and bill.bill_residents:
            accrued = pers_accrued * bill.bill_residents
        tarif = 0
        if (cold_water_consump + hot_water_consump):
            tarif = accrued / (cold_water_consump + hot_water_consump)
    return True, round(tarif, 5), round(accrued, 2), get_paid(bill, service_id)

def service_excluded(bill, service_id):
    ret = False
    if bill and bill.user:
        period = bill.start
        apart_name = bill.task_1.name
        user_name = bill.user.username
        if user_name == 'ruslan.ok' and apart_name == 'Жодино' and service_id == WATER and period >= datetime(2022, 10, 1).date():
            ret = True
    return ret

def get_bill_info(bill):
    total_accrued = total_paid = 0
    ret = {}
    ret['volume'] = { 
        'el': get_consumption(bill, ELECTRICITY), 
        'ga': get_consumption(bill, GAS), 
        'wt': get_consumption(bill, COLD_WATER) + get_consumption(bill, HOT_WATER),
        }
    used, tarif, accrued, paid = get_service_amount(bill, INTERNET)
    total_accrued += accrued
    total_paid += paid
    ret['internet'] = {
        'title': _('Internet/TV'),
        'used': used,
        }
    used, tarif, accrued, paid = get_service_amount(bill, PHONE)
    total_accrued += accrued
    total_paid += paid
    ret['phone'] = {
        'title': _('phone').capitalize(),
        'used': used,
        }
    used, tarif, accrued, paid = get_service_amount(bill, HSC)
    total_accrued += accrued
    total_paid += paid
    ret['zkx'] = {
        'title': _('HCS'), # housing and communal services
        'used': used,
        }
    used, tarif, accrued, paid = get_service_amount(bill, POO)
    total_accrued += accrued
    total_paid += paid
    ret['poo'] = {
        'title': _('PoO'), # pay to the Partnership of Owners
        'used': used,
        }
    used, tarif, accrued, paid = get_service_amount(bill, ELECTRICITY)
    total_accrued += accrued
    total_paid += paid
    ret['electro'] = {
        'title': _('electricity').capitalize(),
        'used': used,
        'tarif': tarif,
        'accrued': accrued,
        }
    used, tarif, accrued, paid = get_service_amount(bill, GAS)
    total_accrued += accrued
    total_paid += paid
    ret['gas'] = {
        'title': _('gas').capitalize(),
        'used': used,
        'tarif': tarif,
        'accrued': accrued,
        }
    used, tarif, accrued, paid = get_service_amount(bill, WATER)
    total_accrued += accrued
    total_paid += paid
    ret['water'] = {
        'title': _('water').capitalize(),
        'used': used,
        'tarif': tarif,
        'accrued': accrued,
        }
    ret['total'] = {
        'title': _('total').capitalize(),
        'accrued': round(total_accrued, 2),
        'paid': round(total_paid, 2),
        }
    return ret

def get_meter_value(code, meter):
    if meter:
        if MeterValue.objects.filter(app_apart=NUM_ROLE_METER_VALUE, task_1=meter.task_1, start=meter.start, name=code).exists():
            meter_value = MeterValue.objects.filter(app_apart=NUM_ROLE_METER_VALUE, task_1=meter.task_1, start=meter.start, name=code).get()
            return meter_value.get_value()
    return None

def get_value_str(value: Decimal|None):
    if not value:
        return '0'
    normalized = value.normalize()
    sign, digits, exponent = normalized.as_tuple()
    if exponent > 0:
        return str(Decimal((sign, digits + (0,) * exponent, 0)))
    else:
        return str(normalized)

def get_bill_meters(bill):
    prev = bill.task_2
    curr = bill.task_3
    ret = []
    apart_id = bill.task_1.id
    props = ApartMeter.objects.filter(task_1=apart_id, app_apart=NUM_ROLE_METER_PROP).order_by('sort')
    future = PeriodMeters.next_period(bill.start)
    for prop in props:
        if prop.start and prop.start >= future:
            continue
        if prop.stop and prop.stop < bill.start:
            continue
        prev_value = get_meter_value(prop.name, prev)
        curr_value = get_meter_value(prop.name, curr)
        value = None
        if prev_value and curr_value:
            value = curr_value - prev_value
        ret.append({
            'name': prop.get_name(),
            'prev_value': prev_value,
            'curr_value': curr_value,
            'value': value,
            'prev_value_str': get_value_str(prev_value),
            'curr_value_str': get_value_str(curr_value),
            'value_str': get_value_str(value),
        })
    return ret

