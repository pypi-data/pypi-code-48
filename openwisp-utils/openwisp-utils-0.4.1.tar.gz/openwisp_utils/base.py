import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField
from openwisp_utils.utils import get_random_key
from openwisp_utils.validators import key_validator


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedEditableModel(UUIDModel):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created = AutoCreatedField(_('created'), editable=True)
    modified = AutoLastModifiedField(_('modified'), editable=True)

    class Meta:
        abstract = True


class KeyField(models.CharField):
    def __init__(self,
                 max_length: int = 64,
                 unique: bool = False,
                 db_index: bool = False,
                 help_text: str = None,
                 *args, **kwargs):
        kwargs.update({
            'default': get_random_key,
            'validators': [key_validator],
        })
        super().__init__(max_length=max_length,
                         unique=unique,
                         db_index=db_index,
                         help_text=help_text,
                         *args, **kwargs)
