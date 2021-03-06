from django.db import models

FIELD_LENGTH = 100


class Package(models.Model):
    """
    Package class represent one PKGBUILD. This may contains multiple artifacts.
    """
    name = models.CharField(max_length=FIELD_LENGTH)
    ignore = models.BooleanField(default=False)
    OFFICIAL = 'OFFICIAL'
    server = models.CharField(max_length=FIELD_LENGTH, default=OFFICIAL)

    def __str__(self):
        return '{} ignore: {}'.format(self.name, self.ignore)


class Artifact(models.Model):
    """
    Artifact class represent one of *.pkg.tar.xz which are generated by a PKGBUILD.
    """
    package = models.ForeignKey(Package)
    name = models.CharField(max_length=FIELD_LENGTH)

    def __str__(self):
        return '{} {}'.format(self.package, self.name)


class Build(models.Model):
    """
    Build class represent a build result.
    """
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
    sha256 = models.CharField(max_length=FIELD_LENGTH * 10, default='')

    def __str__(self):
        return '{} {} {} {}'.format(self.package, self.version, self.date, self.status)
