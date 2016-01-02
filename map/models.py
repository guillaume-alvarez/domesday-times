from django.db import models

# Create your models here.


class Lord(models.Model):
    name = models.CharField(max_length=128, db_index=True)
    url = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Place(models.Model):
    name = models.CharField(max_length=128)
    county = models.CharField(max_length=128)
    hundred = models.CharField(max_length=128, null=True)
    longitude = models.DecimalField(decimal_places=10, max_digits=20)
    latitude = models.DecimalField(decimal_places=10, max_digits=20)
    url = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Settlement(models.Model):
    place = models.ForeignKey(Place)
    head_of_manor = models.CharField(max_length=128, null=True)
    lord = models.ForeignKey(Lord)
    overlord = models.ForeignKey(Lord, related_name='+')
    value = models.DecimalField(decimal_places=2, max_digits=20)
    url = models.CharField(max_length=256)

    def __str__(self):
        return self.place.name + '>' + str(self.head_of_manor) + '>' + self.lord.name + '>' + self.overlord.name


