from django.db import models

FIELD_LENGTH = 100


class Package(models.Model):
    name = models.CharField(max_length=FIELD_LENGTH)
    source = models.CharField(max_length=FIELD_LENGTH)


class Build(models.Model):
    version = models.CharField(max_length=FIELD_LENGTH)
    date = models.DateTimeField()
    package = models.ForeignKey(Package, default='')
