import logging

from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyCascade, ForeignKeyProtect
from isc_common.models.audit import AuditModel, AuditManager, AuditQuerySet
from isc_common.models.tree_audit import TreeAuditModelManager
from kaf_pas.kd.models.lotsman_documents_hierarcy import Lotsman_documents_hierarcy

logger = logging.getLogger(__name__)


class Lotsman_documents_hierarcy_refsQuerySet(AuditQuerySet):
    def delete(self):
        return super().delete()

    def _check(self, **kwargs):
        if kwargs.get('parent') != None:
            if isinstance(kwargs.get('parent'), Lotsman_documents_hierarcy):
                parent = kwargs.get('parent').id
            else:
                parent = kwargs.get('parent')

            if isinstance(kwargs.get('child'), Lotsman_documents_hierarcy):
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


class Lotsman_documents_hierarcy_refsManager(AuditManager):

    @staticmethod
    def getRecord(record):
        res = {
            'id': record.id,
            'editing': record.editing,
            'deliting': record.deliting,
        }
        return res

    def get_queryset(self):
        return Lotsman_documents_hierarcy_refsQuerySet(self.model, using=self._db)


class Lotsman_documents_hierarcy_refs(AuditModel):
    child = ForeignKeyProtect(Lotsman_documents_hierarcy, related_name='Lotsman_documents_hierarcy_child')
    parent = ForeignKeyProtect(Lotsman_documents_hierarcy, related_name='Lotsman_documents_hierarcy_parent', null=True, blank=True)

    section = CodeField(verbose_name="Раздел", null=True, blank=True)
    subsection = CodeField(verbose_name="Подраздел", null=True, blank=True)

    objects = Lotsman_documents_hierarcy_refsManager()
    objects_tree = TreeAuditModelManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Кросс таблица'
        unique_together = (('child', 'parent', 'section', 'subsection'),)
