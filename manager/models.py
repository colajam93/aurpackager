from django.db import models

FIELD_LENGTH = 100


class Package(models.Model):
    name = models.CharField(max_length=FIELD_LENGTH)
    source = models.CharField(max_length=FIELD_LENGTH)

    def __str__(self):
        return self.name


class Build(models.Model):
    package = models.ForeignKey(Package, default='')
    version = models.CharField(max_length=FIELD_LENGTH)
    date = models.DateTimeField()
    result_path = models.CharField(max_length=FIELD_LENGTH, default='')
    log_path = models.CharField(max_length=FIELD_LENGTH, default='')
    STATUS_CHOICES = (
        ('BUILDING', 'Building'),
        ('SUCCESS', 'Success'),
        ('FAILURE', 'Failure')
    )
    status = models.CharField(max_length=FIELD_LENGTH, choices=STATUS_CHOICES, default=STATUS_CHOICES[0])

    def __str__(self):
        return '{} {} {}'.format(self.package, self.version, self.date)
