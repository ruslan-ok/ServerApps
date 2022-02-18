import os, shutil
from datetime import datetime
from todo.models import Grp, Lst, Task as OldTask, Step as OldStep
from note.models import Note
from task.models import Task, Step, Group, TaskGroup, Urls, Hist, GIQ_ADD_TASK
from apart.models import Apart, Meter, Bill, Price
from store.models import Entry
from proj.models import Projects, Expenses
from fuel.models import Car, Fuel, Part, Repl
from trip.models import Person, Trip
from health.models import Biomarker, Incident
from task.const import *
from todo.get_info import get_info as todo_get_info
from note.get_info import get_info as note_get_info
from news.get_info import get_info as news_get_info
from apart.views.apart import get_info as apart_get_info
from apart.views.meter import get_info as meter_get_info
from apart.views.price import get_info as price_get_info
from apart.views.bill import get_info as bill_get_info
from store.get_info import get_info as store_get_info
from expen.views import get_info as expen_get_info
from fuel.views.car import get_info as car_get_info
from fuel.views.fuel import get_info as fuel_get_info
from fuel.views.serv import get_info as repl_get_info
from fuel.views.part import get_info as part_get_info
from health.views.incident import get_info as incident_get_info
from health.views.marker import get_info as marker_get_info

from fuel.views.fuel import get_item_name as get_fuel_name
from fuel.views.serv import get_item_name as get_serv_name
from health.views.marker import get_item_name as get_marker_name

from rusel.secret import storage_dvlp, storage_dvlp_v2
from rusel.files import get_attach_path

storage_path_v2 = storage_dvlp_v2
storage_path = storage_dvlp

STAGES = {
    APP_TODO:   0,
    APP_NOTE:   0,
    APP_NEWS:   0,
    APP_STORE:  1,
    APP_EXPEN:  0,
    APP_TRIP:   0,
    APP_FUEL:   0,
    APP_APART:  0,
    APP_WORK:   0,
    APP_HEALTH: 0,
    APP_DOCS:   0,
    APP_WARR:   0,
    APP_PHOTO:  0,
}

def convert_v3():
    result = {}
    result['start'] = datetime.now()
    init(result)
    convert(result)
    result['stop'] = datetime.now()
    done(result)
    return result

def set(result, app, role, table, oper, qnt: int):
    if (qnt == 0) and (table not in result[app][role]):
        return
    if (qnt == 0) and (oper not in result[app][role][table]):
        return
    if (table not in result[app][role]):
        result[app][role][table] = {}
    result[app][role][table][oper] = qnt

def inc(result, app, role, table, oper):
    if (table not in result[app][role]):
        result[app][role][table] = {}
    if (oper not in result[app][role][table]):
        result[app][role][table][oper] = 1
    else:
        result[app][role][table][oper] += 1

def get_excluded(app, kind):
    return []
    # if (app != APP_TODO):
    #     return []
    # leave_groups = Group.objects.filter(name__contains='Сайт 3.0')
    # if (kind == 'Group'):
    #     return leave_groups
    # leave_tgs = TaskGroup.objects.filter(role=ROLE_TODO).filter(group__in=leave_groups)
    # if (kind == 'TaskGroup'):
    #     return leave_tgs
    # return leave_tgs.values('task')

def delete_task_role(app, role, result):
    data = Task.get_role_tasks(None, app, role).exclude(id__in=get_excluded(app, 'Task'))
    if (app == APP_TODO):
        qnt = data.update(app_task=NONE)
    if (app == APP_NOTE):
        qnt = data.update(app_note=NONE)
    if (app == APP_NEWS):
        qnt = data.update(app_news=NONE)
    if (app == APP_STORE):
        qnt = data.update(app_store=NONE)
    if (app == APP_DOCS):
        qnt = data.update(app_doc=NONE)
    if (app == APP_WARR):
        qnt = data.update(app_warr=NONE)
    if (app == APP_EXPEN):
        qnt = data.update(app_expen=NONE)
    if (app == APP_TRIP):
        qnt = data.update(app_trip=NONE)
    if (app == APP_FUEL):
        qnt = data.update(app_fuel=NONE)
    if (app == APP_APART):
        qnt = data.update(app_apart=NONE)
    if (app == APP_HEALTH):
        qnt = data.update(app_health=NONE)
    if (app == APP_WORK):
        qnt = data.update(app_work=NONE)
    if (app == APP_PHOTO):
        qnt = data.update(app_photo=NONE)
    set(result, app, role, 'Task', 'reset_role', qnt)
    to_kill = Task.objects.filter(app_task=NONE, app_note=NONE, app_news=NONE, 
                        app_store=NONE, app_doc=NONE, app_warr=NONE, app_expen=NONE, app_trip=NONE, 
                        app_fuel=NONE, app_apart=NONE, app_health=NONE, app_work=NONE, app_photo=NONE)
    set(result, app, role, 'Step', 'delete', Step.objects.filter(task__in=to_kill).delete()[0])
    set(result, app, role, 'Urls', 'delete', Urls.objects.filter(task__in=to_kill).delete()[0])
    set(result, app, role, 'Hist', 'delete', Hist.objects.filter(task__in=to_kill).delete()[0])
    set(result, app, role, 'Task', 'delete', to_kill.delete()[0])

def init(result):
    for app in STAGES:
        if STAGES[app]:
            result[app] = {}
            for role in ROLES_IDS[app]:
                result[app][role] = {}
                delete_task_role(app, role, result)
                set(result, app, role, 'TaskGroup', 'delete', TaskGroup.objects.filter(role=role).exclude(id__in=get_excluded(app, 'TaskGroup')).delete()[0])
                set(result, app, role, 'Group', 'delete', Group.objects.filter(app=app).exclude(id__in=get_excluded(app, 'Group')).delete()[0])

def convert(result):
    for app in STAGES:
        if STAGES[app]:
            for role in ROLES_IDS[app]:
                transfer_grp(result, app, role, None, None)
                transfer_lst(result, app, role, None, None)
            if (app == APP_TODO):
                transfer_task(result, None, None)
            if (app == APP_NOTE):
                transfer_note(result, app, role, None, None)
            if (app == APP_NEWS):
                transfer_note(result, app, role, None, None)
            if (app == APP_STORE):
                transfer_store(result, None, None)
            if (app == APP_DOCS):
                pass
            if (app == APP_WARR):
                pass
            if (app == APP_EXPEN):
                transfer_expen_proj(result)
                transfer_expenses(result)
            if (app == APP_TRIP):
                transfer_person(result)
                transfer_trip(result)
            if (app == APP_FUEL):
                transfer_car(result)
                transfer_fuel(result)
                transfer_part(result)
                transfer_repl(result)
            if (app == APP_APART):
                transfer_apart(result)
                transfer_meter(result)
                transfer_price(result)
                transfer_bill(result)
            if (app == APP_HEALTH):
                transfer_incident(result)
                transfer_biomarker(result)
            if (app == APP_WORK):
                pass
            if (app == APP_PHOTO):
                pass

def done(result):
    print(result)

def transfer_grp(result, app, role, grp_node, task_grp_node):
    if (app != role):
        return
    grps = Grp.objects.filter(app=app, node=grp_node)
    for grp in grps:
        task_grp = Group.objects.create(user=grp.user, 
                                        app=grp.app, 
                                        role=grp.app, 
                                        node=task_grp_node, 
                                        name=grp.name, 
                                        sort=grp.sort, 
                                        created=grp.created, 
                                        last_mod=grp.last_mod, 
                                        act_items_qty=0,
                                        use_sub_groups=True,
                                        )
        inc(result, app, role, 'Group', 'added')
        transfer_grp(result, app, role, grp, task_grp)
        transfer_lst(result, app, role, grp, task_grp)

def transfer_lst(result, app, role, grp, task_grp):
    if (app != role):
        return
    lsts = Lst.objects.filter(app=app, grp=grp)
    for lst in lsts:
        task_grp_ = Group.objects.create(user=lst.user, 
                                         src_id=lst.id,
                                         app=lst.app, 
                                         role=lst.app, 
                                         node=task_grp, 
                                         name=lst.name, 
                                         sort=lst.sort, 
                                         created=lst.created, 
                                         last_mod=lst.last_mod,
                                         act_items_qty=0,
                                         use_sub_groups=True,
                                         )
        inc(result, app, role, 'Group', 'added')
        if (role == ROLE_TODO):
            transfer_task(result, lst, task_grp_)
        if (role == ROLE_NOTE) or (role == ROLE_NEWS):
            transfer_note(result, app, role, lst, task_grp_)
        if (role == ROLE_STORE):
            transfer_store(result, lst, task_grp_)

def transfer_task(result, lst, task_grp):
    tasks = OldTask.objects.filter(lst=lst)
    for task in tasks:
        atask = Task.objects.create(user=task.user,
                                    src_id=task.id,
                                    app_task=NUM_ROLE_TODO,
                                    name=task.name,
                                    start=task.start,
                                    stop=task.stop,
                                    completed=task.completed,
                                    completion=task.completion,
                                    in_my_day=task.in_my_day,
                                    important=task.important,
                                    remind=task.remind,
                                    last_remind=task.last_remind,
                                    repeat=task.repeat,
                                    repeat_num=task.repeat_num,
                                    repeat_days=task.repeat_days,
                                    categories=task.categories,
                                    info=str(task.info).replace('\\r\\n', '\n') if task.info else '',
                                    created=task.created,
                                    last_mod=task.last_mod)
        inc(result, APP_TODO, ROLE_TODO, 'Task', 'added')
        
        for step in OldStep.objects.filter(task=task.id):
            Step.objects.create(user=step.task.user, task=atask, name=step.name, sort=step.sort, completed=step.completed)
            inc(result, APP_TODO, ROLE_TODO, 'Step', 'added')
        
        check_grp(result, APP_TODO, ROLE_TODO, atask, task_grp)
        check_url(result, APP_TODO, ROLE_TODO, task, task.url)
        copy_attachments(task.user.id, 'todo', 'task', task.id, APP_TODO, ROLE_TODO, atask)
        atask.set_item_attr(APP_TODO, todo_get_info(atask))

def transfer_note(result, app, role, lst, task_grp):
    notes = Note.objects.filter(lst=lst)
    for note in notes:
        if (note.kind == 'note') and (role != ROLE_NOTE):
            continue
        if (note.kind == 'news') and (role != ROLE_NEWS):
            continue
        note_role = NONE
        news_role = NONE
        if note.kind == 'note':
            note_role = NUM_ROLE_NOTE
        else:
            news_role = NUM_ROLE_NEWS
        atask = Task.objects.create(user=note.user,
                                    src_id=note.id,
                                    app_note=note_role,
                                    app_news=news_role,
                                    name=note.name,
                                    event=note.publ,
                                    categories=note.categories,
                                    info=str(note.descr).replace('\\r\\n', '\n') if note.descr else '',
                                    created=note.publ,
                                    last_mod=note.last_mod)
        inc(result, app, role, 'Task', 'added')
        check_grp(result, app, role, atask, task_grp)
        check_url(result, app, role, atask, note.url)
        copy_attachments(note.user.id, 'note', note.kind, note.id, APP_NOTE, ROLE_NOTE, atask)
        if note.kind == 'note':
            atask.set_item_attr(APP_NOTE, note_get_info(atask))
        else:
            atask.set_item_attr(APP_NEWS, news_get_info(atask))

def transfer_apart(result):
    items = Apart.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.user,
                                    src_id=item.id,
                                    app_apart=NUM_ROLE_APART,
                                    name=item.name,
                                    info=item.addr if item.addr else '',
                                    apart_has_el=True, #item.has_el,
                                    apart_has_hw=True, #item.has_hw,
                                    apart_has_cw=True, #item.has_cw,
                                    apart_has_gas=item.has_gas,
                                    apart_has_ppo=item.has_ppo,
                                    apart_has_tv=False, #item.has_tv,
                                    apart_has_phone=False, #item.has_phone,
                                    apart_has_zkx=False, #item.has_zkx,
                                    )
        inc(result, APP_APART, ROLE_APART, 'Task', 'added')
        atask.set_item_attr(APP_APART, apart_get_info(atask))

def transfer_meter(result):
    items = Meter.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.apart.user,
                                    src_id=item.id,
                                    app_apart=NUM_ROLE_METER,
                                    event=item.reading,
                                    name=item.period.strftime('%Y.%m'),
                                    start=item.period,
                                    info=item.info if item.info else '',
                                    meter_el=item.el,
                                    meter_hw=item.hw,
                                    meter_cw=item.cw,
                                    meter_ga=item.ga,
                                    meter_zkx=item.zhirovka,
                                    task_1=link_task(item.apart.user, item.apart.id, role_apart=NUM_ROLE_APART),
                                    )
        inc(result, APP_APART, ROLE_METER, 'Task', 'added')
        atask.set_item_attr(APP_APART, meter_get_info(atask))

def transfer_price(result):
    items = Price.objects.all()
    for item in items:
        name = item.start.strftime('%Y.%m.%d')
        service_id = 0
        if item.serv:
            name += ' ' + item.serv.name
            service_id = item.serv.id
        atask = Task.objects.create(user=item.apart.user,
                                    src_id=item.id,
                                    app_apart=NUM_ROLE_PRICE,
                                    start=item.start,
                                    name=name,
                                    info=str(item.info).replace('\\r\\n', '\n') if item.info else '',
                                    price_service=service_id,
                                    price_tarif=item.tarif,
                                    price_border=item.border,
                                    price_tarif2=item.tarif2,
                                    price_border2=item.border2,
                                    price_tarif3=item.tarif3,
                                    price_unit=item.unit,
                                    task_1=link_task(item.apart.user, item.apart.id, role_apart=NUM_ROLE_APART),
                                    )
        inc(result, APP_APART, ROLE_PRICE, 'Task', 'added')
        atask.set_item_attr(APP_APART, price_get_info(atask))

def transfer_bill(result):
    items = Bill.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.apart.user,
                                    src_id=item.id,
                                    app_apart=NUM_ROLE_BILL,
                                    event=item.payment,
                                    name=item.period.strftime('%Y.%m'),
                                    start=item.period,
                                    info=str(item.info).replace('\\r\\n', '\n') if item.info else '',
                                    bill_el_pay=item.el_pay,
                                    bill_tv_bill=item.tv_bill,
                                    bill_tv_pay=item.tv_pay,
                                    bill_phone_bill=item.phone_bill,
                                    bill_phone_pay=item.phone_pay,
                                    bill_zhirovka=item.zhirovka,
                                    bill_hot_pay=item.hot_pay,
                                    bill_repair_pay=item.repair_pay,
                                    bill_zkx_pay=item.ZKX_pay,
                                    bill_water_pay=item.water_pay,
                                    bill_gas_pay=item.gas_pay,
                                    bill_rate=item.rate,
                                    bill_poo=item.PoO,
                                    bill_poo_pay=item.PoO_pay,
                                    task_1=link_task(item.apart.user, item.apart.id, role_apart=NUM_ROLE_APART),
                                    task_2=link_task(item.apart.user, item.prev.id, role_apart=NUM_ROLE_METER),
                                    task_3=link_task(item.apart.user, item.curr.id, role_apart=NUM_ROLE_METER),
                                    )
        inc(result, APP_APART, ROLE_BILL, 'Task', 'added')
        
        check_url(result, APP_APART, ROLE_BILL, atask, item.url)
        copy_attachments(item.apart.user.id, 'apart', 'bill', item.id, APP_APART, ROLE_BILL, atask)
        atask.set_item_attr(APP_APART, bill_get_info(atask))

def transfer_store(result, lst, task_grp):
    items = Entry.objects.filter(lst=lst, actual=1)
    for item in items:
        item_info = str(item.notes).replace('\\r\\n', '\n') if item.notes else ''
        if item.uuid:
            if item_info:
                item_info += '\n\n'
            item_info += 'UUID: ' + item.uuid
        atask = Task.objects.create(user=item.user,
                                    src_id=item.id,
                                    app_store=NUM_ROLE_STORE,
                                    name=item.title,
                                    categories=item.categories,
                                    info=item_info,
                                    completed=(item.actual==0),
                                    store_username=item.username,
                                    store_value=item.value,
                                    store_params=item.params,
                                    created=item.created,
                                    last_mod=item.last_mod,
                                    )
        inc(result, APP_STORE, ROLE_STORE, 'Task', 'added')
        check_grp(result, APP_STORE, ROLE_STORE, atask, task_grp)
        check_url(result, APP_STORE, ROLE_STORE, atask, item.url)
        atask.set_item_attr(APP_STORE, store_get_info(atask))

    items = Entry.objects.filter(lst=lst, actual=0)
    for item in items:
        parent_task = None
        if task_grp:
            atasks = Task.objects.filter(user=item.user.id, name=item.title, app_store=NUM_ROLE_STORE, groups__id=task_grp.id)
        else:
            atasks = Task.objects.filter(user=item.user.id, name=item.title, app_store=NUM_ROLE_STORE, groups__id=None)

        if (len(atasks) > 1):
            raise Exception('Duplication of Store items')

        if (len(atasks) == 1):
            parent_task = atasks[0]
            check_url(result, APP_STORE, ROLE_STORE, atask, item.url)
        hist_dt = item.last_mod
        if not hist_dt:
            hist_dt = item.created
        if not hist_dt:
            hist_dt = datetime.now()

        if parent_task:
            Hist.objects.create(task=parent_task,
                                valid_until=hist_dt,
                                store_username=item.username,
                                store_value=item.value,
                                store_params=item.params,
                                info=str(item.notes).replace('\\r\\n', '\n') if item.notes else '',
                                store_uuid=item.uuid,
                                )
            inc(result, APP_STORE, ROLE_STORE_HIST, 'Hist', 'added_hist_Entry')
            check_url(result, APP_STORE, ROLE_STORE, parent_task, item.url)
            parent_task.set_item_attr(APP_STORE, store_get_info(parent_task))
        else:
            item_info = str(item.notes).replace('\\r\\n', '\n') if item.notes else ''
            if item.uuid:
                if item_info:
                    item_info += '\n\n'
                item_info += 'UUID: ' + item.uuid
            atask = Task.objects.create(user=item.user,
                                        src_id=item.id,
                                        app_store=NUM_ROLE_STORE,
                                        name=item.title,
                                        categories=item.categories,
                                        info=item_info,
                                        completed=True,
                                        store_username=item.username,
                                        store_value=item.value,
                                        store_params=item.params,
                                        created=item.created,
                                        last_mod=item.last_mod,
                                        )
            inc(result, APP_STORE, ROLE_STORE, 'Task', 'added_archive_Entry')
            check_url(result, APP_STORE, ROLE_STORE, atask, item.url)
            check_grp(result, APP_STORE, ROLE_STORE, atask, task_grp)
            atask.set_item_attr(APP_STORE, store_get_info(atask))


def transfer_expen_proj(result):
    items = Projects.objects.all()
    for item in items:
        Group.objects.create(user=item.user,
                            src_id=item.id,
                            app=APP_EXPEN,
                            role=ROLE_EXPENSE,
                            node=None,
                            name=item.name,
                            created=item.created,
                            last_mod=item.last_mod,
                            expen_byn=item.tot_byn,
                            expen_usd=item.tot_usd,
                            expen_eur=item.tot_eur,
                            act_items_qty=0,
                            use_sub_groups=True,
                            )
        inc(result, APP_EXPEN, ROLE_EXPENSE, 'Group', 'added')

def transfer_expenses(result):
    items = Expenses.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.direct.user,
                                    src_id=item.id,
                                    app_expen=NUM_ROLE_EXPENSE,
                                    event=item.date,
                                    name = item.description,
                                    created=item.created,
                                    last_mod=item.last_mod,
                                    info=str(item.text).replace('\\r\\n', '\n') if item.text else '',
                                    expen_qty=item.qty,
                                    expen_price=item.price,
                                    expen_rate=item.rate,
                                    expen_rate_2=item.rate_2,
                                    expen_usd=item.usd,
                                    expen_eur=item.eur,
                                    expen_kontr=item.kontr,
                                    )
        inc(result, APP_EXPEN, ROLE_EXPENSE, 'Task', 'added')
        if Group.objects.filter(user=atask.user_id, app=APP_EXPEN, src_id=ROLE_EXPENSE).exists():
            task_grp = Group.objects.filter(user=atask.user_id, app=APP_EXPEN, src_id=ROLE_EXPENSE).get()
            check_grp(result, APP_EXPEN, ROLE_EXPENSE, atask, task_grp)
        atask.set_item_attr(APP_EXPEN, expen_get_info(atask))

def transfer_person(result):
    items = Person.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.user,
                                    src_id=item.id,
                                    app_trip=NUM_ROLE_PERSON,
                                    name=item.name,
                                    pers_dative=item.dative,
                                    active=item.me,
                                    )
        inc(result, APP_TRIP, ROLE_PERSON, 'Task', 'added')
        #atask.set_item_attr(APP_TRIP, pers_get_info(atask))

def transfer_trip(result):
    items = Trip.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.user,
                                    src_id=item.id,
                                    app_trip=NUM_ROLE_TRIP,
                                    event=datetime.strptime('{}-W{}'.format(item.year, item.week), "%Y-W%W"),
                                    trip_days=item.days,
                                    trip_oper=item.oper,
                                    trip_price=item.price,
                                    info=item.text,
                                    last_mod=item.modif,
                                    task_1=link_task(item.user, item.driver.id, role_trip=NUM_ROLE_PERSON),
                                    task_2=link_task(item.user, item.passenger.id, role_trip=NUM_ROLE_PERSON),
                                    )
        inc(result, APP_TRIP, ROLE_TRIP, 'Task', 'added')
        #atask.set_item_attr(APP_TRIP, trip_get_info(atask))

def transfer_car(result):
    items = Car.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.user,
                                    src_id=item.id,
                                    app_fuel=NUM_ROLE_CAR,
                                    name=item.name,
                                    car_plate=item.plate,
                                    )
        inc(result, APP_FUEL, ROLE_CAR, 'Task', 'added')
        atask.set_item_attr(APP_FUEL, car_get_info(atask))

def transfer_fuel(result):
    items = Fuel.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.car.user,
                                    src_id=item.id,
                                    app_fuel=NUM_ROLE_FUEL,
                                    event=item.pub_date,
                                    name=get_fuel_name(item.pub_date),
                                    car_odometr=item.odometr,
                                    fuel_volume=item.volume,
                                    fuel_price=item.price,
                                    info=item.comment.strip(),
                                    created=item.created,
                                    last_mod=item.last_mod,
                                    task_1=link_task(item.car.user, item.car.id, role_fuel=NUM_ROLE_CAR),
                                    )
        inc(result, APP_FUEL, ROLE_FUEL, 'Task', 'added')
        atask.set_item_attr(APP_FUEL, fuel_get_info(atask))

def transfer_part(result):
    items = Part.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.car.user,
                                    src_id=item.id,
                                    app_fuel=NUM_ROLE_PART,
                                    name=item.name,
                                    part_chg_km=item.chg_km,
                                    part_chg_mo=item.chg_mo,
                                    info=str(item.comment).replace('\\r\\n', '\n') if item.comment else '',
                                    task_1=link_task(item.car.user, item.car.id, role_fuel=NUM_ROLE_CAR),
                                    )
        inc(result, APP_FUEL, ROLE_PART, 'Task', 'added')

def transfer_repl(result):
    items = Repl.objects.all()
    for item in items:
        part = None
        if item.part:
            part = link_task(item.car.user, item.part.id, role_fuel=NUM_ROLE_PART)
        else:
            pass
        atask = Task.objects.create(user=item.car.user,
                                    src_id=item.id,
                                    app_fuel=NUM_ROLE_SERVICE,
                                    event=item.dt_chg,
                                    name=get_serv_name(part, item.dt_chg),
                                    car_odometr=item.odometr,
                                    repl_manuf=item.manuf,
                                    repl_part_num=item.part_num,
                                    repl_descr=item.descr,
                                    info=str(item.comment).replace('\\r\\n', '\n') if item.comment else '',
                                    created=item.created,
                                    last_mod=item.last_mod,
                                    task_1=link_task(item.car.user, item.car.id, role_fuel=NUM_ROLE_CAR),
                                    task_2=part,
                                    )
        inc(result, APP_FUEL, ROLE_SERVICE, 'Task', 'added')
        atask.set_item_attr(APP_FUEL, repl_get_info(atask))

    for part in Task.objects.filter(app_fuel=NUM_ROLE_PART):
        part.set_item_attr(APP_FUEL, part_get_info(part))

def transfer_incident(result):
    items = Incident.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.user,
                                    src_id=item.id,
                                    app_health=NUM_ROLE_INCIDENT,
                                    name=item.name,
                                    start=item.beg,
                                    stop=item.end,
                                    diagnosis=item.diagnosis,
                                    info=str(item.info).replace('\\r\\n', '\n') if item.info else '',
                                    )
        inc(result, APP_HEALTH, ROLE_INCIDENT, 'Task', 'added')
        atask.set_item_attr(APP_HEALTH, incident_get_info(atask))

def transfer_biomarker(result):
    items = Biomarker.objects.all()
    for item in items:
        atask = Task.objects.create(user=item.user,
                                    src_id=item.id,
                                    app_health=NUM_ROLE_MARKER,
                                    event=item.publ,
                                    name=get_marker_name(item.publ),
                                    bio_height=item.height,
                                    bio_weight=item.weight,
                                    bio_temp=item.temp,
                                    bio_waist=item.waist,
                                    bio_systolic=item.systolic,
                                    bio_diastolic=item.diastolic,
                                    bio_pulse=item.pulse,
                                    info=str(item.info).replace('\\r\\n', '\n') if item.info else '',
                                    )
        inc(result, APP_HEALTH, ROLE_MARKER, 'Task', 'added')
        atask.set_item_attr(APP_HEALTH, marker_get_info(atask))



def link_task(user_id, todo_grp_id, role_trip=NONE, role_fuel=NONE, role_apart=NONE):
    if Task.objects.filter(user=user_id, app_trip=role_trip, app_fuel=role_fuel, app_apart=role_apart, src_id=todo_grp_id).exists():
        return Task.objects.filter(user=user_id, app_trip=role_trip, app_fuel=role_fuel, app_apart=role_apart, src_id=todo_grp_id).get()
    return None

def check_grp(result, app, role, task, task_grp):
    if task_grp:
        task.correct_groups_qty(GIQ_ADD_TASK, task_grp.id)
        inc(result, app, role, 'TaskGroup', 'added')

def check_url(result, app, role, task, href):
    if href and not Urls.objects.filter(task=task, href=href).exists():
        num = len(Urls.objects.filter(task=task)) + 1
        Urls.objects.create(task=task, num=num, href=href)
        inc(result, app, role, 'Urls', 'added')

def copy_attachments(user, src_app, src_role, src_item_id, dst_app, dst_role, dst_item):
    src_path = storage_path_v2.format(user.id) + '{}/{}_{}/'.format(src_app, src_role, src_item_id)
    if not os.path.exists(src_path):
        return
    dst_path = get_attach_path(user, dst_app, dst_role, dst_item, 3)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    src_files = os.listdir(src_path)
    for file_name in src_files:
        full_file_name = os.path.join(src_path, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, dst_path)