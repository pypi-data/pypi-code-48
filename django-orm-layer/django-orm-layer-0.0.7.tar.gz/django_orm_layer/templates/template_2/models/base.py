from django.db import models


class CommonInfo(models.Model):
    # auto_now_add=True是创建时添加时间，auto_now=True每次修改时更新时间，不能同时为True
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True
        ordering = ['id']
