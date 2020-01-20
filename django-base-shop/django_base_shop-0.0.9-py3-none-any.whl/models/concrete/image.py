from django.db import models


class Image(models.Model):
    handle = models.CharField(max_length=200, unique=True, db_index=True)
    image = models.ImageField(upload_to="images/")

    def __str__(self):
        return self.handle
