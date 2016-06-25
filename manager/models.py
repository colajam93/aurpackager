from django.db import models

FIELD_LENGTH = 100


class Package(models.Model):
    name = models.CharField(max_length=FIELD_LENGTH)
    ignore = models.BooleanField(default=False)

    def __str__(self):
        return '{} ignore: {}'.format(self.name, self.ignore)


class Build(models.Model):
    package = models.ForeignKey(Package, default='')
    version = models.CharField(max_length=FIELD_LENGTH, default='')
    date = models.DateTimeField()
    BUILDING = 'BUILDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'
    STATUS_CHOICES = (
        (BUILDING, 'Building'),
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure')
    )
    status = models.CharField(max_length=FIELD_LENGTH, choices=STATUS_CHOICES, default=BUILDING)
    sha256 = models.CharField(max_length=FIELD_LENGTH, default='')

    def __str__(self):
        return '{} {} {} {}'.format(self.package, self.version, self.date, self.status)
