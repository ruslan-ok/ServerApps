from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, date
from django.utils.translation import gettext, gettext_lazy as _

app_name = 'fuel'

class Car(models.Model):
    user   = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    name   = models.CharField(_('model'), max_length = 200, blank = False)
    plate  = models.CharField(_('car number'), max_length = 100)
    active = models.BooleanField(_('active'), default = False)

    class Meta:
        verbose_name = _('car')
        verbose_name_plural = _('cars')

    def __str__(self):
        return self.name + ' [' + self.plate + ']'

    def marked_item(self):
        return self.active

    def get_info(self):
        ret = []
        ret.append({'text': self.plate})
        return ret


def deactivate_all(user_id, cars_id):
    for car in Car.objects.filter(user = user_id, active = True).exclude(id = cars_id):
        car.active = False
        car.save()

def set_active(user_id, cars_id):
    if Car.objects.filter(user = user_id, id = cars_id).exists():
        car = Car.objects.filter(user = user_id, id = cars_id).get()
        deactivate_all(user_id, car.id)
        car.active = True
        car.save()


class Fuel(models.Model):
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'))
    pub_date = models.DateTimeField(_('date'), default = datetime.now)
    odometr  = models.IntegerField(_('odometer'), blank=False)
    volume   = models.DecimalField(_('volume'), blank=False, max_digits=5, decimal_places=3)
    price    = models.DecimalField(_('price'), blank=False, max_digits=15, decimal_places=2)
    comment  = models.CharField(_('information'), max_length=1000, blank=True)
    created  = models.DateTimeField(_('creation time'), auto_now_add = True, null = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True, null = True)

    class Meta:
        verbose_name = _('fueling')
        verbose_name_plural = _('fuelings')

    def __str__(self):
        return str(self.pub_date) + ' / ' + str(self.odometr) + ' ' + gettext('km.') +' / ' + str(self.volume) + ' ' + gettext('l.')
    
    def summa(self):
        return self.price * self.volume

    def name(self):
        return self.pub_date.strftime('%d.%m.%Y %H:%M')

    def get_info(self):
        ret = []
        ret.append({'text': _('odometr: ') + str(self.odometr)})
        ret.append({'icon': 'separator'})
        ret.append({'text': _('volume: ') + '{:.0f}'.format(self.volume)})
        ret.append({'icon': 'separator'})
        ret.append({'text': _('price: ') + '{:.2f}'.format(self.price)})
        ret.append({'icon': 'separator'})
        ret.append({'text': _('summa: ') + '{:.2f}'.format(self.summa())})
        if self.comment:
            ret.append({'icon': 'separator'})
            ret.append({'icon': 'notes'})
            ret.append({'text': self.comment})
        return ret


# средний расход
def consumption(_user, car = None):
  try:
    if not car:
        car = Car.objects.get(user = _user, active = True)
    car_name = car.name + ': '
    fuels = Fuel.objects.filter(car = car.id).order_by('-pub_date', '-odometr')
    counter_max = 0
    counter_min = 0
    total_volume = 0
    
    for f in fuels:
      counter_min = f.odometr
    
      if (counter_max == 0):
        counter_max = f.odometr
      else:
        total_volume += f.volume
    
    km = counter_max - counter_min
    
    if (total_volume == 0) or (km == 0):
      return 0
    
    return round((total_volume / km) * 100, 2)
  except Car.DoesNotExist:
    return 0
    

def fuel_summary(_user):
  try:
    car = Car.objects.get(user = _user, active = True)
    car_name = car.name + ': '
    cons = consumption(_user)
    if (cons == 0):
      return car_name + gettext('failed to calculate average consumption')
    else:
      return car_name + '<span class="warning">' + str(cons) + '</span> ' + gettext(' l. per 100 km')
  except Car.DoesNotExist:
    return gettext('no active car')
    

class Part(models.Model): # Список расходников
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'))
    name     = models.CharField(_('name'), max_length = 1000, blank = False)
    chg_km   = models.IntegerField(_('replacement interval, km'), blank = True, null = True)
    chg_mo   = models.IntegerField(_('replacement interval, months'), blank = True, null = True)
    comment  = models.TextField(_('information'), blank = True)

    class Meta:
        verbose_name = _('part')
        verbose_name_plural = _('parts')
  
    def __str__(self):
        return self.name
  
    def last_date(self):
        last = Repl.objects.filter(part = self.id).order_by('-dt_chg')[:1]
        if (len(last) == 0):
            return date.min
        else:
            return last[0].dt_chg.date()

    def s_last_date(self):
        return self.last_date().isoformat()

    def last_odo(self):
        last = Repl.objects.filter(part = self.id).order_by('-dt_chg')[:1]
        if (len(last) == 0):
            return 0
        else:
            return last[0].odometr
  
    def repls(self):
        r = Repl.objects.filter(part = self.id)
        return len(r)

    def chg_km_th(self):
        return self.chg_km // 1000

    def get_rest(self):
        if ((not self.chg_km) and (not self.chg_mo)) or (not self.last_odo()):
            return '', ''

        fuels = Fuel.objects.filter(car = self.car).order_by('-pub_date')[:1]
        if (len(fuels) == 0):
            return '', ''

        output = ''
        p1 = ''
        p2 = ''
        m1 = False
        m2 = False
        color = ''

        if (self.chg_km != 0):
            trip_km_unround = fuels[0].odometr - self.last_odo() # Проехали км от последней замены
          
            trip_km = trip_km_unround
            if (trip_km > 1000):
                trip_km = round(trip_km_unround / 1000) * 1000
          
            if (trip_km_unround > self.chg_km):
                if ((trip_km_unround - self.chg_km) > 1000):
                    p1 = 'просрочено на ' + str(round(((trip_km_unround - self.chg_km) / 1000))) + ' тыс. км'
                    color = 'error'
                else:
                    p1 = 'просрочено на ' + str(trip_km_unround - self.chg_km) + ' км'
                    color = 'error'
                m1 = True
            else:
                if ((self.chg_km - trip_km) < 1000):
                    p1 = str(self.chg_km - trip_km_unround) + ' км'
                    color = 'warning'
                else:
                    p1 = str(round(((self.chg_km - trip_km) / 1000))) + ' тыс. км'
              
        if (self.chg_mo != 0):
            trip_days = (fuels[0].pub_date.date() - self.last_date()).days - self.chg_mo * 30.42
            per = ''
            days = trip_days
            if (days < 0):
                days = -1 * days
          
            if (days < 2):
                per = 'день'
            elif (days < 5):
                per = str(round(days)) + ' дня'
            elif (days < 30):
                per = str(round(days)) + ' дней'
            elif (days < 45):
                per = 'месяц'
            elif (days < 135):
                per = str(round(days/30)) + ' месяца'
            elif (days < 270):
                per = 'пол года'
            elif (days < 540):
                per = 'год'
            elif (days < 1642):
                per = str(round(days/365)) + ' года'
            else:
                per = str(round(days/365)) + ' лет'
            
            if (trip_days > 0):
                p2 = 'просрочено на ' + per
                m2 = True
                color = 'error'
            else:
                if (days < 32):
                    p2 = per
                    color = 'warning'
                else:
                    p2 = per
      
        if m1:
            output = p1
        elif m2:
            output = p2
        elif (p1 == ''):
            output = p2
        elif (p2 == ''):
            output = p1
        else:
            output = p1 + ' или ' + p2

        return output, color

    def get_info(self):
        ret = []
        if self.chg_km:
            ret.append({'text': _('km: ') + str(self.chg_km)})
    
        if self.chg_mo:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'text': _('months: ') + str(self.chg_mo)})
    
        rest, color = self.get_rest()
        if rest:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'text': rest, 'color': 'rest-color-' + color})
        
        if self.comment:
            if (len(ret) > 0):
                ret.append({'icon': 'separator'})
            ret.append({'icon': 'notes'})

        return ret


class Repl(models.Model): # Замена расходников
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name=_('car'), null = True)
    part     = models.ForeignKey(Part, on_delete=models.CASCADE, verbose_name=_('part'), null = True)
    dt_chg   = models.DateTimeField(_('date'), blank = False)
    odometr  = models.IntegerField(_('odometer, km'), blank = False)
    manuf    = models.CharField(_('manufacturer'), max_length = 1000, blank = True)
    part_num = models.CharField(_('catalog number'), max_length = 100, blank = True)
    descr    = models.CharField(_('name'), max_length = 1000, blank = True)
    comment  = models.TextField(_('information'), blank = True, default = None, null = True)
    created  = models.DateTimeField(_('creation time'), auto_now_add = True, null = True)
    last_mod = models.DateTimeField(_('last modification time'), blank = True, auto_now = True, null = True)

    class Meta:
        verbose_name = _('replacement')
        verbose_name_plural = _('replacements')

    def __str__(self):
        return str(self.dt_chg) + ' / ' + str(self.odometr) + ' ' + gettext('km.') + ' / ' + self.descr

    def s_dt_chg(self):
        d = str(self.dt_chg.day)
        m = str(self.dt_chg.month)
        y = str(self.dt_chg.year)
        if (len(d) < 2):
            d = '0' + d
        if (len(m) < 2):
            m = '0' + m
        return d + '.' + m + '.' + y

    def name(self):
        part = ''
        if self.part:
            part = ' - ' + self.part.name
        return self.dt_chg.strftime('%d.%m.%Y %H:%M') + part

    def get_info(self):
        ret = []
        ret.append({'text': _('odometr: ') + str(self.odometr)})
        if self.manuf:
            ret.append({'icon': 'separator'})
            ret.append({'text': self.manuf})
        if self.part_num:
            ret.append({'icon': 'separator'})
            ret.append({'text': self.part_num})
        if self.descr:
            ret.append({'icon': 'separator'})
            ret.append({'text': self.descr})
        if self.comment:
            ret.append({'icon': 'separator'})
            ret.append({'icon': 'notes'})
            ret.append({'text': self.comment})
        return ret

def init_repl_car():
    for repl in Repl.objects.filter(car__isnull = True):
        repl.car = repl.part.car
        repl.save()

def enrich_context(context, app_param, user_id):
    context['article_mode'] = app_param.kind
    context['article_pk'] = app_param.art_id

    context['cars_qty']      = len(Car.objects.filter(user = user_id))
    if Car.objects.filter(user = user_id, active = True).exists():
        car = Car.objects.filter(user = user_id, active = True).get()
        context['intervals_qty'] = len(Part.objects.filter(car = car))
        context['fueling_qty']   = len(Fuel.objects.filter(car = car))
        context['service_qty']   = len(Repl.objects.filter(car = car))
    return context
        