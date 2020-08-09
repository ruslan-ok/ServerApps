from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required

from hier.utils import get_base_context, save_folder_id, process_common_commands, get_trash, get_param
from hier.models import Param, Folder
from trip.models import trip_summary

#----------------------------------
# Index
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def index(request):
    process_common_commands(request)
    title = ''
    context = get_base_context(request, 0, 0, title, 'content_list')

    if request.user.is_authenticated:
        save_folder_id(request.user, 0)
        title = _('applications')
        hide_title = False
    else:
        title = context['site']
        hide_title = True

    context['title'] = title
    context['hide_title'] = hide_title
    context['trip_summary'] = trip_summary(request.user.id)
    param = get_param(request.user)
    if param and param.last_url:
        context['last_visited_url'] = reverse(param.last_url)
        context['last_visited_app'] = param.last_app
        context['last_visited_page'] = param.last_page

    template = loader.get_template('index.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
# Feedback
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def feedback(request):
    context = get_base_context(request, 0, 0, _('feedback'))
    template = loader.get_template('feedback.html')
    return HttpResponse(template.render(context, request))


#----------------------------------
# Notes
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def note(request):
    folder_id = 0
    top_folders = Folder.objects.filter(user = request.user.id, node = 0, model_name = '')
    for f in top_folders:
        if Folder.objects.filter(user = request.user.id, node = f.id, model_name = 'note:note_list').exists():
            folder_id = Folder.objects.filter(user = request.user.id, node = f.id, model_name = 'note:note_list').get().id
            break
    return HttpResponseRedirect(reverse('hier:folder_list', args = [folder_id]))

#----------------------------------
# News
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def news(request):
    folder_id = 0
    top_folders = Folder.objects.filter(user = request.user.id, node = 0, model_name = '')
    for f in top_folders:
        if Folder.objects.filter(user = request.user.id, node = f.id, model_name = 'note:news_list').exists():
            folder_id = Folder.objects.filter(user = request.user.id, node = f.id, model_name = 'note:news_list').get().id
            break
    return HttpResponseRedirect(reverse('hier:folder_list', args = [folder_id]))

#----------------------------------
# Store
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def store(request):
    folder_id = 0
    top_folders = Folder.objects.filter(user = request.user.id, node = 0, model_name = '')
    for f in top_folders:
        if Folder.objects.filter(user = request.user.id, node = f.id, model_name = 'store:entry').exists():
            folder_id = Folder.objects.filter(user = request.user.id, node = f.id, model_name = 'store:entry').get().id
            break
    return HttpResponseRedirect(reverse('hier:folder_list', args = [folder_id]))

#----------------------------------
# Trash
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def trash(request):
    return HttpResponseRedirect(reverse('hier:folder_list', args = [get_trash(request.user).id]))

