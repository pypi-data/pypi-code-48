import logging

from bitfield import BitField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.models.tree_audit import TreeAuditModelManager

from kaf_pas.ckk.models.item import Item

logger = logging.getLogger(__name__)


class Item_refsQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def _check(self, **kwargs):
        if kwargs.get('parent') != None:
            if isinstance(kwargs.get('parent'), Item):
                parent = kwargs.get('parent').id
            else:
                parent = kwargs.get('parent')

            if isinstance(kwargs.get('child'), Item):
                child = kwargs.get('child').id
            else:
                child = kwargs.get('child')

            if parent == child:
                raise Exception(f'Attempt to write circular reference id ({parent})')

    def create(self, **kwargs):
        self._check(**kwargs)
        return super().create(**kwargs)

    def update(self, **kwargs):
        self._check(**kwargs)
        return super().update(**kwargs)

    def get_or_create(self, defaults=None, **kwargs):
        self._check(**kwargs)
        return super().get_or_create(defaults, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        self._check(**kwargs)
        return super().update_or_create(defaults, **kwargs)

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Item_refsManager(AuditManager):

    @staticmethod
    def props():
        return BitField(flags=(
            ('relevant', 'Актуальность'),  # 1
        ), default=3, db_index=True)

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'child_id': record.child.id,
            'parent_id': record.parent.id if record.parent else None,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Item_refsQuerySet(self.model, using=self._db)


class Item_refs(AuditModel):
    child = ForeignKeyProtect(Item, related_name='child')
    parent = ForeignKeyProtect(Item, related_name='parent', blank=True, null=True)

    props = Item_refsManager.props()

    objects = TreeAuditModelManager()

    def __str__(self):
        return f'\nID={self.id}, child=[{self.child}], parent=[{self.parent}]'

    class Meta:
        verbose_name = 'Item_refs'
        unique_together = ('child', 'parent')
