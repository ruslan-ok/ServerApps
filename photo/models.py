from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

app_name = 'photo'

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('user'))
    creation = models.DateTimeField(_('creation time'), null = True, auto_now_add = True)
    last_mod = models.DateTimeField(_('last modification time'), null = True, auto_now = True)
    name = models.CharField(_('name'), max_length=1000)
    path = models.CharField(_('path'), max_length=1000, blank = True)
    categories = models.CharField(_('categories'), max_length=1000, blank = True)
    info = models.TextField(_('information'), blank = True)

    def __str__(self):
        return self.name

    def full_name(self):
        if self.path:
            return self.path + '/' + self.name
        return self.name


