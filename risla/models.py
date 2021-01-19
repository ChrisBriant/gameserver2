from django.db import models
from django.db.models import Count
import random

# slug               object
# name               object
# occupation         object
# bplace_country     object
# birthdate          object
# birthyear         float64
# dplace_name        object
# dplace_country     object
# deathdate          object
# age               float64

class PersonManager(models.Manager):
    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = random.randint(0, count - 1)
        return self.all()[random_index]

class Person(models.Model):
    slug = models.CharField(max_length=75,null=False)
    name = models.CharField(max_length=75,null=False)
    occupation = models.CharField(max_length=50)
    bplace_country = models.CharField(max_length=50)
    birthdate = models.DateTimeField(null=True)
    birthyear = models.IntegerField(null=True)
    dplace_name = models.CharField(max_length=50)
    dplace_country = models.CharField(max_length=50)
    deathdate = models.DateTimeField(null=True)
    age = models.IntegerField(null=True)
    random_objects = PersonManager()


class Question(models.Model):
    question = models.CharField(max_length=255,null=False)
