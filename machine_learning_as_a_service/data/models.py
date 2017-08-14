from django.db import models
from picklefield.fields import PickledObjectField

# Create your models here.
class Data(models.Model):
    data_frame = PickledObjectField()
