from django.db import models
from picklefield.fields import PickledObjectField

# Create your models here.
class Data(models.Model):
    data_frame = PickledObjectField()

    source_url = models.URLField(null=True)

    def __str__(self):
        if (self.source_url):
            return self.source_url
        else:
            return 'unknown source'
