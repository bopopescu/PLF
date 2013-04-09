from django.db import models

# Create your models here.
class User(models.Model):
    email = models.EmailField()
    items = models.ManyToManyField('Item')

class Item(models.Model):
    status = models.BooleanField()
    category = models.CharField(max_length=100)
    student = models.ForeignKey('User')
    desc = models.CharField(max_length=250)
    sub_date = models.DateField(null=True)
    event_date = models.DateField(null=True)
    location = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='pics', null=True)

    def __unicode__(self):
        return u'%s' % (self.category)


