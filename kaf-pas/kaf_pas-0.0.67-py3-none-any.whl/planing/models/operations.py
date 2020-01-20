import logging

from django.conf import settings
from django.db import transaction, connection
from django.db.models import TextField
from django.forms import model_to_dict

from isc_common import StackElementNotExist
from isc_common.common.mat_views import create_tmp_mat_view, drop_mat_view
from isc_common.datetime import DateToStr
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditModel, AuditQuerySet
from isc_common.ws.progressStack import ProgressStack
from kaf_pas.planing.models.operation_types import Operation_types
from kaf_pas.planing.models.status_operation_types import Status_operation_types
from kaf_pas.production.models.launch_operation_material import Launch_operations_material
from kaf_pas.production.models.launch_operation_resources import Launch_operation_resources
from kaf_pas.production.models.launch_operations_item import Launch_operations_item

logger = logging.getLogger(__name__)


class OperationsQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Rout_item():

    def __init__(self, item_id, first_operation, last_operation):
        self.item_id = item_id
        self.first_operation = first_operation
        self.last_operation = last_operation


class OperationsManager(AuditManager):

    @staticmethod
    def make_routing(data):
        from isc_common.auth.models.user import User
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from kaf_pas.planing.models.operation_level import Operation_level
        from kaf_pas.planing.models.operation_locations import Operation_locations
        from kaf_pas.planing.models.operation_material import Operation_material
        from kaf_pas.planing.models.operation_refs import Operation_refs
        from kaf_pas.planing.models.operation_resources import Operation_resources
        from kaf_pas.planing.models.operation_standard_prod import Operation_standard_prod
        from kaf_pas.planing.models.operation_value import Operation_value
        from kaf_pas.production.models.launches import Launches
        from kaf_pas.planing.models.operation_item import Operation_item
        from kaf_pas.ckk.models.ed_izm import Ed_izm

        logger.debug(f'data: {data}')

        OperationsManager.clean_routing(data=data)

        launch_id = data.get('id')

        launch = Launches.objects.get(id=launch_id)

        user = User.objects.get(id=data.get('user_id'))
        edizm = Ed_izm.objects.get(code='шт')

        progress = ProgressStack(
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'common_{user.username}',
        )

        id_progress1 = f'launch_{launch.id}_{user.id}'
        try:

            demand_str = f'<h3>Расчет маршрутизации: Запуск № {launch.code} от {DateToStr(launch.date)}</h3>'

            sql_str = f'''with recursive r as (
                                                    select *,
                                                           1 as level
                                                    from production_launch_item_refs
                                                    where parent_id is null
                                                      and launch_id = {launch_id}
                                                    union all
                                                    select production_launch_item_refs.*,
                                                           r.level + 1 as level
                                                    from production_launch_item_refs
                                                             join r
                                                                  on
                                                                      production_launch_item_refs.parent_id = r.child_id)
                                                
                                                select r1.id,
                                                       r1.parent_id,
                                                       r1.child_id,
                                                       r1.launch_id,
                                                       r1.stmp1,
                                                       r1.stmp2,
                                                       r1.qty,
                                                       r1.level
                                                from (select distinct r.id,
                                                                      r.parent_id,
                                                                      r.child_id,
                                                                      stmp1.value_str                         stmp1,
                                                                      stmp2.value_str                         stmp2,
                                                                      r.launch_id,
                                                                      (
                                                                          select coalesce(kda.value_int, kda.value_str::numeric(19, 4), 0)
                                                                          from production_launch_item_line plil
                                                                                   join kd_document_attributes kda on kda.id = plil."SPC_CLM_COUNT_id"
                                                                          where plil.child_id = r.child_id
                                                                            and plil.parent_id = r.parent_id
                                                                            and plil.launch_id = r.launch_id) qty,
                                                                      (
                                                                          select plil.section
                                                                          from production_launch_item_line plil
                                                                          where plil.child_id = r.child_id
                                                                            and plil.parent_id = r.parent_id
                                                                            and plil.launch_id = r.launch_id) section,
                                                                      level
                                                      from r
                                                               join ckk_item ci on ci.id = r.child_id
                                                               join kd_document_attributes stmp1 on stmp1.id = ci."STMP_1_id"
                                                               join kd_document_attributes stmp2 on stmp2.id = ci."STMP_2_id"
                                                      where r.launch_id = {launch_id}
                                                      order by level desc) r1
                                                where lower(r1.section) != 'документация'
    
                                                        '''
            with transaction.atomic():

                mat_view_name = create_tmp_mat_view(sql_str=sql_str, indexes=['parent_id', 'child_id'])
                with connection.cursor() as cursor:

                    cursor.execute(f'select count(*) from {mat_view_name}')
                    count, = cursor.fetchone()

                    logger.debug(f'{mat_view_name} count(*): {count}')

                    progress.show(
                        title=f'<b>Обработано товарных позиций</b>',
                        label_contents=demand_str,
                        cntAll=count * 2,
                        id=id_progress1
                    )

                    cursor.execute(f'select * from {mat_view_name} order by level desc')
                    rows = cursor.fetchall()
                    cnt = 0
                    from isc_common import Stack
                    outcome_items = Stack()

                    for row in rows:
                        def make_oparetions(row, mode='chlid'):
                            id, parent_id, child_id, launch_id, stmp1, stmp2, qty, level = row

                            if mode == 'child':
                                cursor.execute(f'select sum(qty) from {mat_view_name} where child_id = %s', [child_id])
                                qty, = cursor.fetchone()
                            elif mode == 'parent':
                                child_id = parent_id

                            if len(outcome_items.find(lambda outcome_item: outcome_item.item_id == child_id)) == 0:
                                income_operation = None
                                cnt1 = Launch_operations_item.objects.filter(item_id=child_id, launch_id=launch_id).count()
                                if cnt1 > 0:
                                    first_operation = None
                                    for launch_operations_item in Launch_operations_item.objects.filter(item_id=child_id, launch_id=launch_id).order_by('num'):
                                        outcome_operation = Operations.objects.create(
                                            opertype=settings.OPERS_TYPES_STACK.ROUTING_TASK,
                                        )

                                        Operation_launches.objects.create(operation=outcome_operation, launch=launch)
                                        Operation_item.objects.create(operation=outcome_operation, item=launch_operations_item.item)
                                        Operation_level.objects.create(operation=outcome_operation, level=level)
                                        if qty != None:
                                            Operation_value.objects.create(operation=outcome_operation, value=qty, edizm=edizm)

                                        if income_operation == None:
                                            first_operation = outcome_operation

                                        for launch_operation_material in Launch_operations_material.objects.filter(launch_operationitem=launch_operations_item):
                                            if launch_operation_material.material_askon != None:
                                                Operation_material.objects.get_or_create(operation=outcome_operation, material=launch_operation_material.material_askon)
                                            if launch_operation_material.material != None:
                                                Operation_standard_prod.objects.get_or_create(operation=outcome_operation, material=launch_operation_material.material)

                                        if Launch_operation_resources.objects.filter(launch_operationitem=launch_operations_item) == 0:
                                            raise Exception(f'Для : {stmp1} : {stmp2} ID={child_id} не задан ресурс.')

                                        for launch_operation_resources in Launch_operation_resources.objects.filter(launch_operationitem=launch_operations_item):
                                            if launch_operation_resources.resource != None:
                                                Operation_resources.objects.get_or_create(operation=outcome_operation, resource=launch_operation_resources.resource)
                                            if launch_operation_resources.location != None:
                                                Operation_locations.objects.get_or_create(operation=outcome_operation, location=launch_operation_resources.location)

                                        Operation_refs.objects.get_or_create(income=income_operation, outcome=outcome_operation)
                                        income_operation = outcome_operation
                                        cnt1 -= 1
                                        if cnt1 == 0:
                                            outcome_items.push(Rout_item(item_id=child_id, first_operation=first_operation, last_operation=outcome_operation))
                                else:
                                    raise Exception(f'Для : {stmp1} : {stmp2} ID={child_id} не задано ни одной операции. Запустите анализатор готовности к запуску.')

                        make_oparetions(row=row)

                        cnt += 1
                        progress.setCntDone(cnt=cnt, id=id_progress1)

                    for row in rows:
                        id, parent_id, child_id, launch_id, stmp1, stmp2, qty, level = row

                        try:
                            first_operation = outcome_items.find_one(lambda outcome_item: outcome_item.item_id == parent_id)
                        except StackElementNotExist:
                            make_oparetions(row=row, mode='parent')
                            first_operation = outcome_items.find_one(lambda outcome_item: outcome_item.item_id == parent_id)

                        cursor.execute(f'''select child_id, stmp1, stmp2 from {mat_view_name} where parent_id = %s''', [parent_id])
                        parents_rows = cursor.fetchall()
                        for parents_row in parents_rows:
                            _child_id, stmp1, stmp2 = parents_row
                            _child = outcome_items.find_one(lambda item: item.item_id == _child_id)

                            Operation_refs.objects.get_or_create(income=_child.last_operation, outcome=first_operation.last_operation)
                            deleted, _ = Operation_refs.objects.filter(income__isnull=True, outcome=first_operation.last_operation).delete()
                        progress.setCntDone(cnt=cnt, id=id_progress1)
                        cnt += 1

                    progress.close(id=id_progress1)
                    drop_mat_view(mat_view_name)

                launch.props |= Launches.props.routing_made
                launch.save()
                settings.EVENT_STACK.EVENTS_PRODUCTION_MAKE_ROUTING.send_message(f'<h3>Выполнен Расчет маршрутизации: Запуск № {launch.code} от {DateToStr(launch.date)}</h3><p/>')

        except Exception as ex:
            progress.close(id=id_progress1)
            raise ex

    def clean_routing(data):
        from kaf_pas.production.models.launches import Launches
        from kaf_pas.planing.models.operation_launches import Operation_launches
        from isc_common.auth.models.user import User

        logger.debug(f'data: {data}')

        launch_id = data.get('id')
        launch = Launches.objects.get(id=launch_id)

        cntAll = Operation_launches.objects.filter(launch=launch).count()

        if cntAll > 0:
            user = User.objects.get(id=data.get('user_id'))

            progress = ProgressStack(
                host=settings.WS_HOST,
                port=settings.WS_PORT,
                channel=f'common_{user.username}',
            )

            id_progress1 = f'launch_{launch.id}_{user.id}'
            try:
                with transaction.atomic():
                    demand_str = f'<h3>Удаление маршрутизации : Запуск № {launch.code} от {DateToStr(launch.date)}</h3>'

                    launch.props &= ~Launches.props.routing_made
                    launch.save()

                    progress.show(
                        title=f'<b>Обработано товарных позиций</b>',
                        label_contents=demand_str,
                        cntAll=cntAll,
                        id=id_progress1
                    )

                    cnt = 0

                    for operation_launches in Operation_launches.objects.filter(launch=launch):
                        operation_launches.operation.delete()
                        progress.setCntDone(cnt=cnt, id=id_progress1)
                        cnt += 1

                    progress.close(id=id_progress1)
                    settings.EVENT_STACK.EVENTS_PRODUCTION_DELETE_ROUTING.send_message(f'<h3>Выполнено Удаление маршрутизации: Запуск № {launch.code} от {DateToStr(launch.date)}</h3><p/>')
            except Exception as ex:
                progress.close(id=id_progress1)
                raise ex

        return model_to_dict(launch)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'opertype_id': record.opertype.id,
            'opertype__full_name': record.opertype.full_name,
            'status_id': record.status.id if record.status else None,
            'status__code': record.status.code if record.status else None,
            'status__name': record.status.name if record.status else None,
        }
        return res

    def get_queryset(self):
        return OperationsQuerySet(self.model, using=self._db)


class Operations(AuditModel):
    opertype = ForeignKeyProtect(Operation_types)
    status = ForeignKeyProtect(Status_operation_types, null=True, blank=True)
    description = TextField(null=True, blank=True)

    objects = OperationsManager()

    def __str__(self):
        return f"ID:{self.id}, opertype: [{self.opertype}], status: [{self.status}]"

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Опреации системные'
