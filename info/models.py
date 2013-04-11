from django.db import models
# from PIL import *
import PIL

# Create your models here.
class User(models.Model):
    email = models.EmailField()
    items = models.ManyToManyField('Item', null=True, blank=True)

    def __unicode__(self):
        return u'%s' %(self.email)

class Item(models.Model):
    status = models.BooleanField()
    category = models.CharField(max_length=100)
    student = models.ForeignKey('User', null=True, blank=True, default=None)
    desc = models.CharField(max_length=250)
    sub_date = models.DateField(null=True)
    event_date = models.DateField(null=True)
    location = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='photos', blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.category)


