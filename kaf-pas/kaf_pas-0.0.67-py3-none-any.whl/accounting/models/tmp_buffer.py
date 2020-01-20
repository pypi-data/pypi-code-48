import logging

from django.db.models import DecimalField

from isc_common.auth.models.user import User
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditManager, AuditQuerySet, AuditModel
from kaf_pas.ckk.models.ed_izm import Ed_izm
from kaf_pas.ckk.models.item import Item
from kaf_pas.ckk.models.locations import Locations

logger = logging.getLogger(__name__)


class Tmp_bufferQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def create(self, **kwargs):
        return super().create(**kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Tmp_bufferManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'location_id': record.location.id,
            'location__code': record.location.code,
            'location__name': record.location.name,
            'location__full_name': record.location.full_name,
            'item_id': record.item.id,
            'item__STMP_1_id': record.item.STMP_1.id if record.item.STMP_1 else None,
            'item__STMP_1__value_str': record.item.STMP_1.value_str if record.item.STMP_1 else None,
            'item__STMP_2_id': record.item.STMP_2.id if record.item.STMP_2 else None,
            'item__STMP_2__value_str': record.item.STMP_2.value_str if record.item.STMP_2 else None,
            'edizm_id': record.edizm.id,
            'edizm__code': record.edizm.code,
            'edizm__name': record.edizm.name,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Tmp_bufferQuerySet(self.model, using=self._db)


class Tmp_buffer(AuditModel):
    item = ForeignKeyProtect(Item)
    location = ForeignKeyProtect(Locations)
    user = ForeignKeyProtect(User)
    edizm = ForeignKeyProtect(Ed_izm)
    value = DecimalField(max_digits=19, decimal_places=4)

    objects = Tmp_bufferManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Временное хранилищи данных для буферов'
