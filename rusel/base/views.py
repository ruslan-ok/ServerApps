import os, json
from datetime import date
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Q
from django.core.exceptions import FieldError
from django.contrib.auth.mixins import LoginRequiredMixin
from rusel.apps import get_related_roles
from rusel.utils import extract_get_params, get_search_mode
from rusel.base.forms import GroupForm
from rusel.base.context import Context
from rusel.search import search_in_files
from task.const import *
from task.models import Task, Group, TaskGroup, Urls, GIQ_ADD_TASK, GIQ_DEL_TASK

BG_IMAGES = [
    'beach',
    'desert',
    'fern',
    'field',
    'gradient',
    'lighthouse',
    'safari',
    'sea',
    'tv_tower'
]

#----------------------------------------------------------------------
class BaseListView(ListView, Context, LoginRequiredMixin):

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)
        self.template_name = 'base/list.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404
        ret = super().get(request, *args, **kwargs)
        nav_role = Task.get_nav_role(self.config.app)
        cur_role = self.config.get_cur_role()
        if nav_role and (nav_role != cur_role):
            if (self.config.group_entity not in request.GET):
                nav_item = Task.get_active_nav_item(request.user.id, self.config.app)
                if nav_item:
                    return HttpResponseRedirect(request.path + '?' + self.config.group_entity + '=' + str(nav_item.id))
        return ret

    def get_queryset(self):
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
            app = self.request.GET.get('app')
            if (app == APP_DOCS or app == APP_PHOTO):
                return query
        data = self.get_sorted_items(query)
        if self.config.limit_list:
            data = data[:self.config.limit_list]
        if query:
            for task in data:
                task = self.highlight_search(query, task)
        return data

    def highlight_search(self, query, task):
        strong = '<strong>' + query + '</strong>'
        if query in task.name:
            task.name = strong.join(task.name.split(query))
        if task.info and query in task.info:
            if (len(task.info) < 200):
                fnd_info = task.info
            else:
                prefix = ''
                pos = task.info.find(query)
                if (pos > 80):
                    pos -= 80
                    prefix = '... '
                else:
                    pos = 0
                fnd_info = prefix + task.info[pos:pos+200] + ' ...'
            task.found = strong.join(fnd_info.split(query))
        return task

    def get_success_url(self):
        if (self.config.get_cur_role() == self.config.base_role):
            return reverse(self.config.app + ':item', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)
        return reverse(self.config.app + ':' + self.config.get_cur_role() + '-item', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        self.object = None
        context = super().get_context_data(**kwargs)
        use_sub_groups = self.config.use_sub_groups and self.config.cur_view_group.use_sub_groups
        context['use_sub_groups'] = use_sub_groups
        if use_sub_groups:
            sub_groups = self.load_sub_groups()
            for task in self.get_queryset():
                grp_id, name = self.get_sub_group(task)
                group = self.find_sub_group(sub_groups, grp_id, name)
                group['items'].append(task)
            self.save_sub_groups(sub_groups)
            context['sub_groups'] = sorted(sub_groups, key = lambda group: group['id'])

        search_qty = None
        query = None
        folder = ''
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
            app = self.request.GET.get('app')
            folder = self.request.GET.get('folder')
        if query:
            search_in_files_result = search_in_files(self.request.user, app, folder, query)
            context['files_list'] = search_in_files_result
            search_qty = 0
            if not app:
                search_qty += len(self.object_list)
            else:
                self.object_list = []
            search_qty += len(search_in_files_result)
        nav_items = self.get_nav_items()
        upd_context = self.get_app_context(self.request.user.id, search_qty, icon=self.config.view_icon, nav_items=nav_items, **kwargs)
        context.update(upd_context)

        if self.config.view_sorts:
            context['sorts'] = self.get_sorts(self.config.view_sorts)
        elif self.config.app_sorts:
            context['sorts'] = self.get_sorts(self.config.app_sorts)

        themes = []
        for x in range(24):
            if (x < 14) or (x == 23):
                themes.append({'id': x+1, 'style': 'theme-' + str(x+1)})
            else:
                themes.append({'id': x+1, 'img': self.get_bg_img(x)})
        context['themes'] = themes

        if self.config.cur_view_group and self.config.cur_view_group.theme:
            context['theme_id'] = self.config.cur_view_group.theme
            context['dark_theme'] = self.config.cur_view_group.dark_theme

        if self.config.cur_view_group.items_sort:
            context['sort_id'] = self.config.cur_view_group.items_sort
            context['sort_reverse'] = self.config.cur_view_group.items_sort[0] == '-'
            if self.config.view_sorts:
                sorts = self.config.view_sorts
            else:
                sorts = self.config.app_sorts
            for sort in sorts:
                if (sort[0] == self.config.cur_view_group.items_sort.replace('-', '')):
                    context['sort_name'] = _(sort[1]).capitalize()
                    break

        return context

    def get_bg_img(self, num):
        return BG_IMAGES[num-14]

    def load_sub_groups(self):
        cur_group = self.config.cur_view_group
        ret = []
        if not cur_group:
            return ret
        if not cur_group.sub_groups:
            return ret
        sgs = json.loads(cur_group.sub_groups)
        for sg in sgs:
            ret.append({'id': sg['id'], 'name': sg['name'], 'is_open': sg['is_open'], 'items': [], 'qty': 0 })
        return ret

    def save_sub_groups(self, sub_groups):
        cur_group = self.config.cur_view_group
        if not cur_group:
            return
        sub_groups_json = []
        for sg in sub_groups:
            if sg['id']:
                sub_groups_json.append({'id': sg['id'], 'name': sg['name'], 'is_open': sg['is_open']})
        sub_groups_str = json.dumps(sub_groups_json)
        cur_group.sub_groups = sub_groups_str
        cur_group.save()

    def get_sub_group(self, task):
        use_sub_groups = self.config.use_sub_groups and self.config.cur_view_group.use_sub_groups
        if not use_sub_groups:
            return 0, ''
        if (task.app_apart == NUM_ROLE_PRICE):
            return task.price_service, APART_SERVICE[task.price_service]
        if (task.app_fuel == NUM_ROLE_SERVICE):
            if not task.task_2:
                return 0, ''
            else:
                return task.task_2.id, task.task_2.name
        if task.completed and self.config.cur_view_group:
            grp_id = GRP_PLANNED_DONE
        elif (not task.stop) or not ((self.config.cur_view_group.determinator == 'view' and self.config.cur_view_group.view_id == 'planned')):
            grp_id = GRP_PLANNED_NONE
        else:
            today = date.today()
            if (task.stop.date() == today):
                grp_id = GRP_PLANNED_TODAY
            else:
                days = (task.stop.date() - today).days
                if (days == 1):
                    grp_id = GRP_PLANNED_TOMORROW
                elif (days < 0):
                    grp_id = GRP_PLANNED_EARLIER
                elif (days < 8):
                    grp_id = GRP_PLANNED_ON_WEEK
                else:
                    grp_id = GRP_PLANNED_LATER
        return grp_id, GRPS_PLANNED[grp_id].capitalize()

    def find_sub_group(self, groups, grp_id, name):
        for group in groups:
            if (group['id'] == grp_id):
                group['qty'] += 1
                return group
        group = {'id': grp_id, 'name': name, 'is_open': True, 'items': [], 'qty': 1 }
        groups.append(group)
        return group

    def get_sorted_items(self, query):
        data = self.get_filtered_items(query)
        if not self.config.cur_view_group.items_sort:
            if self.config.default_sort:
                return self.sort_data(data, self.config.default_sort)
            return data
        return self.sort_data(data, self.config.cur_view_group.items_sort)

    def get_base_dataset(self):
        nav_role = Task.get_nav_role(self.config.app)
        if nav_role and (nav_role != self.config.get_cur_role()):
            if (self.config.group_entity in self.request.GET):
                active_nav_item_id = self.request.GET[self.config.group_entity]
                Task.set_active_nav_item(self.request.user.id, self.config.app, active_nav_item_id)
        self.config.set_view(self.request)
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        nav_item = None

        nav_role = Task.get_nav_role(self.config.app)
        cur_role = self.config.get_cur_role()
        if nav_role and (nav_role != cur_role):
            if (self.config.group_entity in self.request.GET):
                active_nav_item_id = self.request.GET[self.config.group_entity]
                nav_item = Task.set_active_nav_item(self.request.user.id, self.config.app, active_nav_item_id)
            else:
                nav_item = Task.get_active_nav_item(self.request.user.id, self.config.app)

        if nav_role and (nav_role != self.config.get_cur_role()):
            nav_item = Task.get_active_nav_item(self.request.user.id, self.config.app)
        return self.get_dataset(self.config.cur_view_group, query, nav_item)

    def get_filtered_items(self, query):
        ret = self.get_base_dataset()
        search_mode = get_search_mode(query)
        lookups = None
        if (search_mode == 0):
            return ret
        elif (search_mode == 1):
            lookups = Q(name__icontains=query) | Q(info__icontains=query) | Q(categories__icontains=query)
        elif (search_mode == 2):
            lookups = Q(categories__icontains=query[1:])
        return ret.filter(lookups)

    def sort_data(self, data, sort, reverse=False):
        if not data or not sort:
            return data

        sort_fields = sort.split()
        if reverse:
            revers_list = []
            for sf in sort_fields:
                if (sf[0] == '-'):
                    revers_list.append(sf[1:])
                else:
                    revers_list.append('-' + sf)
            sort_fields = revers_list

        try:
            if (len(sort_fields) == 1):
                data = data.order_by(sort_fields[0])
            elif (len(sort_fields) == 2):
                data = data.order_by(sort_fields[0], sort_fields[1])
            elif (len(sort_fields) == 3):
                data = data.order_by(sort_fields[0], sort_fields[1], sort_fields[2])
        except FieldError:
            pass

        return data

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        self.config.set_view(self.request)
        return response
    
#----------------------------------------------------------------------
class BaseDetailView(UpdateView, Context, LoginRequiredMixin):

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)
        self.template_name = config['name'] + '/' + self.config.get_cur_role() + '.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404
        ret = super().get(request, *args, **kwargs)
        return ret

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if obj.user != self.request.user:
            raise Http404
        return obj

    def get_success_url(self):
        if (self.config.get_cur_role() == self.config.base_role):
            return reverse(self.config.app + ':item', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)
        return reverse(self.config.app + ':' + self.config.get_cur_role() + '-item', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request, detail=True)
        self.template_name = self.config.app + '/' + self.config.get_cur_role() + '.html'
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon, nav_items=self.get_nav_items()))
        urls = []
        for url in Urls.objects.filter(task=self.object.id):
            if (self.request.path not in url.href):
                urls.append(url)
            else:
                fake_url = url
                fake_url.href = '#'
                urls.append(fake_url)
        context['urls'] = urls
        context['files'] = self.object.get_files_list(self.config.get_cur_role())
        context['item'] = self.object
        related_roles, possible_related = get_related_roles(self.get_object(), self.config)
        context['related_roles'] = related_roles
        context['possible_related'] = possible_related
        return context

    def form_valid(self, form):
        self.config.set_view(self.request, detail=True)
        item = form.instance
        role = self.config.get_cur_role()
        old_item = Task.objects.filter(id=item.id).get()
        old_item.correct_groups_qty(GIQ_DEL_TASK, role=role)
        if ('url' in form.changed_data):
            url = form.cleaned_data['url']
            qty = len(Urls.objects.filter(task=item.id))
            Urls.objects.create(task=item, num=qty, href=url)
        if ('upload' in self.request.FILES):
            self.handle_uploaded_file(self.request.FILES['upload'], item)
        ret = super().form_valid(form)
        grp_id = None
        if ('grp' in form.changed_data):
            grp = form.cleaned_data['grp']
            if grp:
                grp_id = grp.id
        item.correct_groups_qty(GIQ_ADD_TASK, grp_id)
        return ret

    def handle_uploaded_file(self, f, item):
        path = item.get_attach_path(self.config.get_cur_role())
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

class BaseGroupView(UpdateView, Context, LoginRequiredMixin):
    model = Group
    template_name = 'base/group_detail.html'
    form_class = GroupForm

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if obj.user != self.request.user:
            raise Http404
        obj.check_items_qty()
        return obj

    def get_success_url(self):
        return reverse(self.config.app + ':group', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request, detail=True)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon='journals'))
        context['title'] = self.object.name
        context['is_group_form'] = self.object.name
        context['delete_question'] = _('delete group').capitalize()
        if Group.objects.filter(node=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are subordinate groups').capitalize()
        else:
            if TaskGroup.objects.filter(group=self.object.id).exists():
                context['ban_on_deletion'] = _('deletion is prohibited because the group contains items').capitalize()
            else:
                context['ban_on_deletion'] = ''
        return context


GRP_PLANNED_NONE     = 0
GRP_PLANNED_EARLIER  = 1
GRP_PLANNED_TODAY    = 2
GRP_PLANNED_TOMORROW = 3
GRP_PLANNED_ON_WEEK  = 4
GRP_PLANNED_LATER    = 5
GRP_PLANNED_DONE     = 6

GRPS_PLANNED = {
    GRP_PLANNED_NONE:     '',
    GRP_PLANNED_EARLIER:  _('earlier'),
    GRP_PLANNED_TODAY:    _('today'),
    GRP_PLANNED_TOMORROW: _('tomorrow'),
    GRP_PLANNED_ON_WEEK:  _('on the week'),
    GRP_PLANNED_LATER:    _('later'),
    GRP_PLANNED_DONE:     _('completed'),
}  
