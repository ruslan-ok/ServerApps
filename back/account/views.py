import hashlib

from django.conf import settings
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import resolve_url
from django.shortcuts import get_object_or_404, Http404
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string

from django.utils.decorators import method_decorator
from django.utils.http import (url_has_allowed_host_and_scheme, urlsafe_base64_decode,)
from django.utils.translation import gettext, gettext_lazy as _

from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView

from django.contrib import messages
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import (REDIRECT_FIELD_NAME, get_user_model, login as auth_login, logout as auth_logout,)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from account.forms import (LoginForm, RegisterForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm, ProfileForm, AvatarForm,)
from core.send_email import send_email

from task.const import ROLE_ACCOUNT
from core.context import get_base_context
from account.models import UserExt

UserModel = get_user_model()


class SuccessURLAllowedHostsMixin:
    success_url_allowed_hosts = set()

    def get_success_url_allowed_hosts(self):
        return {self.request.get_host(), *self.success_url_allowed_hosts}


class LoginView(SuccessURLAllowedHostsMixin, FormView):
    """
    Display the login form and handle the login action.
    """
    form_class = LoginForm
    authentication_form = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'account/login.html'
    redirect_authenticated_user = False
    extra_context = None

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.extra_context = get_base_context(request, 'home', ROLE_ACCOUNT, None, False, gettext('Log in'))
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or resolve_url(settings.LOGIN_REDIRECT_URL)

    def get_redirect_url(self):
        """Return the user-originating redirect URL if it's safe."""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name, '')
        )
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.get_success_url_allowed_hosts(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else ''

    def get_form_class(self):
        return self.authentication_form or self.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            self.redirect_field_name: self.get_redirect_url(),
            'username': self.request.user.username or '',
            'user': self.request.user,
            **(self.extra_context or {})
        })
        return context

class LogoutView(SuccessURLAllowedHostsMixin, TemplateView):
    """
    Log out the user and display the 'You are logged out' message.
    """
    next_page = None
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'account/index.html'
    extra_context = None

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        self.extra_context = get_base_context(request, 'home', ROLE_ACCOUNT, None, True, gettext('Logged out'))
        auth_logout(request)
        next_page = self.get_next_page()
        if next_page:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(next_page)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Logout may be done via POST."""
        return self.get(request, *args, **kwargs)

    def get_next_page(self):
        if self.next_page is not None:
            next_page = resolve_url(self.next_page)
        elif settings.LOGOUT_REDIRECT_URL:
            next_page = resolve_url(settings.LOGOUT_REDIRECT_URL)
        else:
            next_page = self.next_page

        if (self.redirect_field_name in self.request.POST or
                self.redirect_field_name in self.request.GET):
            next_page = self.request.POST.get(
                self.redirect_field_name,
                self.request.GET.get(self.redirect_field_name)
            )
            url_is_safe = url_has_allowed_host_and_scheme(
                url=next_page,
                allowed_hosts=self.get_success_url_allowed_hosts(),
                require_https=self.request.is_secure(),
            )
            # Security check -- Ensure the user-originating redirection URL is safe.
            if not url_is_safe:
                next_page = self.request.path
        return next_page

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            **(self.extra_context or {})
        })
        return context


def generate_activation_key(username):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(20, chars)
    return hashlib.sha256((secret_key + username).encode('utf-8')).hexdigest()

@csrf_protect
def register(request):
    title = _('Register')
    extra_context = {}
    if request.method == 'POST':
        f = RegisterForm(request.POST)
        if f.is_valid():
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password1']
            # send email verification now
            activation_key = generate_activation_key(username=username)


            title = subject = gettext('Account Verification')

            message = '\n' + gettext('Please visit the following link to verify your account') + ' \n\n' + \
                    '{}://{}/account/activate/?key={}'.format(request.scheme, request.get_host(), activation_key)            

            error = False

            try:
                send_email(subject, message, email)
                admin_subject = 'Регистрация нового пользователя'
                admin_message = f'Зарегистрировался новый пользователь "{username}" с электронной почтой {email}.'
                send_email(admin_subject, admin_message, settings.EMAIL_ADMIN)
            except Exception as e:
                message = _('Unable to send email verification. Please try again.') + ' ' + str(e)
                extra_context.update({'form_messages': [message]})
                error = True
                title = _('Register')

            if not error:
                u = User.objects.create_user(
                        username,
                        email,
                        password,
                        is_active = 0
                )

                newUser = UserExt()
                newUser.activation_key = activation_key
                newUser.user = u
                newUser.save()
                Token.objects.create(user=u)
                return HttpResponseRedirect(reverse_lazy('account:register_done'))
    else:
        f = RegisterForm()

    context = get_base_context(request, 'home', ROLE_ACCOUNT, None, False, title)
    context.update(extra_context)
    context['form'] = f
    return render(request, 'account/register.html', context)

def register_done(request):
    context = get_base_context(request, 'home', ROLE_ACCOUNT, None, False, gettext('Register done'))
    return render(request, 'account/register_done.html', context)

def activate_account(request):
    key = request.GET.get('key')
    if not key:
        raise Http404()

    r = get_object_or_404(UserExt, activation_key=key, email_validated=False)
    r.user.is_active = True
    r.user.save()
    r.email_validated = True
    r.save()

    context = get_base_context(request, 'home', ROLE_ACCOUNT, None, False, gettext('Account activated'))
    return render(request, 'account/activated.html', context)

class PasswordContextMixin:
    extra_context = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': self.title,
            **(self.extra_context or {})
        })
        return context


class PasswordResetView(PasswordContextMixin, FormView):
    email_template_name = 'account/password_reset_email.html'
    extra_email_context = None
    form_class = PasswordResetForm
    from_email = None
    html_email_template_name = None
    subject_template_name = 'account/password_reset_subject.txt'
    success_url = reverse_lazy('account:password_reset_done')
    template_name = 'account/password_reset_form.html'
    title = _('Password reset')
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': self.token_generator,
            'from_email': self.from_email,
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.html_email_template_name,
            'extra_email_context': self.extra_email_context,
        }
        form.save(**opts)
        return super().form_valid(form)


INTERNAL_RESET_SESSION_TOKEN = settings.DJANGO_PWD_RESET_TOKEN


class PasswordResetDoneView(PasswordContextMixin, TemplateView):
    template_name = 'account/password_reset_done.html'
    title = _('Password reset sent')


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class = SetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'set-password'
    success_url = reverse_lazy('account:password_reset_complete')
    template_name = 'account/password_reset_confirm.html'
    title = _('Enter new password')
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        if self.post_reset_login:
            auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context


class PasswordResetCompleteView(PasswordContextMixin, TemplateView):
    template_name = 'account/password_reset_complete.html'
    title = _('Password reset complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = resolve_url('account:login')
        return context


class PasswordChangeView(PasswordContextMixin, FormView):
    form_class = PasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'account/password_change_form.html'
    title = _('Password change')

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        # Updating the password logs out all other sessions for the user
        # except the current one.
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)


class PasswordChangeDoneView(PasswordContextMixin, TemplateView):
    template_name = 'account/password_change_done.html'
    title = _('Password change successful')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

def user_data_changed(user, data, request):
    userext = None
    if UserExt.objects.filter(user=request.user).exists():
        userext = UserExt.objects.filter(user=request.user).get()
    if user.username == data['username'] and \
        user.first_name == data['first_name'] and \
        user.last_name == data['last_name'] and \
        user.email == data['email'] and \
        (userext and userext.phone or None) == data['phone'] and \
        (('avatar' not in data) or ((userext and userext.avatar or None) == data['avatar'])):
        messages.add_message(request, messages.INFO, 'User information is not changed.')
        return False
    return True


def service(request):
    context = get_base_context(request, 'home', ROLE_ACCOUNT, None, False, gettext('Profile service'))
    return render(request, 'account/service.html', context)


def profile(request):
    userext = None
    if UserExt.objects.filter(user=request.user).exists():
        userext = UserExt.objects.filter(user=request.user).get()
    if request.method == 'POST':
        usr = User.objects.get(id=request.user.id)
        form = ProfileForm(request.POST, request.FILES, instance = request.user)
        if form.is_valid():
            if user_data_changed(usr, form.cleaned_data, request):
                usr.username = form.cleaned_data['username']
                usr.first_name = form.cleaned_data['first_name']
                usr.last_name = form.cleaned_data['last_name']
                usr.email = form.cleaned_data['email']
                usr.is_active = True
                usr.save()
                if userext and ('avatar' in form.cleaned_data or 'phone' in form.cleaned_data or 'lang' in form.cleaned_data):
                    if ('avatar' in form.cleaned_data):
                        avatar = form.cleaned_data['avatar']
                        userext.avatar = avatar
                    if ('phone' in form.cleaned_data):
                        userext.phone = form.cleaned_data['phone']
                    userext.save()

                messages.add_message(request, messages.SUCCESS, 'The user `%s` was changed successfully.' % (usr.username))
            if ('form_close' in request.POST):
                return HttpResponseRedirect(reverse_lazy('index'))
    else:
        form = ProfileForm(instance = request.user)
        if userext:
            form.initial['phone'] = userext.phone

    context = get_base_context(request, 'home', ROLE_ACCOUNT, None, '', (_('Profile'),))
    context['form'] = form
    avatar = userext and userext.avatar or None
    context['avatar_url'] = avatar.url if avatar and type(avatar) == ImageFieldFile else '/static/account/img/Default-avatar.jpg'
    if userext and userext.avatar_mini and type(userext.avatar_mini) == ImageFieldFile:
        context['avatar_mini_url'] = userext.avatar_mini.url
    else:
        context['avatar_mini_url'] = '/static/account/img/Default-avatar.jpg'
    context['hide_add_item_input'] = True

    return render(request, 'account/profile.html', context)

def avatar(request):
    userext = None
    if UserExt.objects.filter(user=request.user).exists():
        userext = UserExt.objects.filter(user=request.user).get()
    else:
        userext = UserExt.objects.create(user=request.user)
    if request.method != 'POST':
        form = AvatarForm(instance=userext)
    else:
        form = AvatarForm(request.POST, request.FILES, instance=userext)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy('account:avatar'))

    context = get_base_context(request, 'home', ROLE_ACCOUNT, None, '', (_('avatar').capitalize(),))
    context['form'] = form
    context['avatar_url'] = userext.avatar.url if userext.avatar and type(userext.avatar) == ImageFieldFile else '/static/account/img/Default-avatar.jpg'
    context['hide_add_item_input'] = True
    return render(request, 'account/avatar.html', context)

def demo(request):
    demouserpassword = settings.DJANGO_DEMOUSER_PWRD
    if not User.objects.filter(username = 'demouser').exists():
        user = User.objects.create_user('demouser', settings.EMAIL_DEMOUSER, demouserpassword)
    user = authenticate(username='demouser', password=demouserpassword)
    if user is not None:
        auth_login(request, user)
    return HttpResponseRedirect(reverse_lazy('index'))

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def react_demo(request):
    demouserpassword = settings.DJANGO_DEMOUSER_PWRD
    if not User.objects.filter(username = 'demouser').exists():
        user = User.objects.create_user('demouser', settings.EMAIL_DEMOUSER, demouserpassword)
    user = authenticate(username='demouser', password=demouserpassword)
    if user is None:
        result = { 'ok': False, 'info': 'User "demouser" not found.' }
    else:
        auth_login(request, user)
        if not user.is_authenticated:
            result = { 'ok': False, 'info': 'User "demouser" is not authenticated.' }
        else:
            result = { 'ok': True, 'info': user.get_username() }
    return Response(result)

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def react_login(request):
    username = request.data['username']
    password = request.data['password']
    if not username or not password:
        result = { 'ok': False, 'info': 'The "username" and "password" fields must be filled in.' }
    else:
        user = None
        if username and password:
            user = authenticate(request, username=username, password=password)
        if not user:
            result = { 'ok': False, 'info': 'Please enter a correct username and password. Note that both fields may be case-sensitive.' }
        else:
            auth_login(request, user)
            result = { 'ok': True, 'info': user.get_username() }
    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def react_logout(request):
    auth_logout(request)
    result = { 'ok': True, 'username': '' }
    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def get_app_username(request):
    if request.user and request.user.is_authenticated:
        result = { 'ok': 'ok', 'username': request.user.username }
    result = { 'ok': 'ok', 'username': None }
    return Response(result)
