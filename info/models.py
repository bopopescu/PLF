from django.db import models
from stdimage import StdImageField
# from PIL import *
import PIL

# Create your models here.
class User(models.Model):
    email = models.EmailField()
    items = models.ManyToManyField('Item', null=True, blank=True)
    count = models.IntegerField()

    def __unicode__(self):
        return u'%s' %(self.email)

class Item(models.Model):
    status = models.BooleanField()
    category = models.CharField(max_length=100)
    student = models.ForeignKey('User', null=True, blank=True, default=None)
    desc = models.CharField(max_length=250)
    name = models.CharField(max_length=20)
    sub_date = models.DateField(null=True)
    event_date = models.DateField(null=True)
    location = models.CharField(max_length=100)
    picture = StdImageField(upload_to='photos', size=(640, 480, True))
    claimed = models.NullBooleanField(null=True, blank=True, default=False)

    def __unicode__(self):
        return u'%s' % (self.name)
