from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from account.models import UserExt

# Define an inline admin descriptor for UserExt model
# which acts a bit like a singleton
class UserExtInline(admin.StackedInline):
    model = UserExt
    can_delete = False
    verbose_name_plural = 'userext'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserExtInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)