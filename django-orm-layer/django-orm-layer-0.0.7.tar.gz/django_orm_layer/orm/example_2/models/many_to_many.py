from .base import CommonInfo, models

# https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ManyToManyField
# https://docs.djangoproject.com/en/2.2/ref/models/fields/

# `python -m orm.manage sqlmigrate example_2 0001` print all the sql.


class Image(CommonInfo):
    origin_url = models.CharField(
        max_length=200, null=False, unique=True, db_column='origin_url', verbose_name='原始地址')
    thumbnail_url = models.CharField(
        max_length=200, null=False, unique=True, db_column='thumbnail_url', verbose_name='缩略图地址')
    scale = models.FloatField(verbose_name='缩放尺寸')


class Blog(CommonInfo):
    """
        CREATE TABLE "example_2_blog"
          (
             "id"         SERIAL NOT NULL PRIMARY KEY,
             "created_at" TIMESTAMP WITH time zone NOT NULL,
             "updated_at" TIMESTAMP WITH time zone NOT NULL
          );

        CREATE TABLE "example_2_blog_images"
          (
             "id"       SERIAL NOT NULL PRIMARY KEY,
             "blog_id"  INTEGER NOT NULL,
             "image_id" INTEGER NOT NULL
          );

    add images: blog.images.set([image1, image2, image3, ...])
    query images: blog.images.all()
    """
    images = models.ManyToManyField('Image', related_name='blogs', related_query_name='blogs')


class Person(models.Model):
    """
        CREATE TABLE "example_2_person"
          (
             "id" SERIAL NOT NULL PRIMARY KEY
          );

        CREATE TABLE "example_2_person_friends"
          (
             "id"             SERIAL NOT NULL PRIMARY KEY,
             "from_person_id" INTEGER NOT NULL,
             "to_person_id"   INTEGER NOT NULL
          );
    """
    friends = models.ManyToManyField('self')
