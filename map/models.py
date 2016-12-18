from django.db import models

BURGERS = 'B'
PEASANTS = 'P'
KNIGHTS = 'L'
MONKS = 'M'
POPULATION_TYPES = (
    (BURGERS, 'Burgers'),
    (PEASANTS, 'Peasants'),
    (KNIGHTS, 'Knights'),
    (MONKS, 'Monks'),
)
POPULATION_TYPES_DICT = dict(POPULATION_TYPES)


# Create your models here.


class DomesdayData(models.Model):
    fid = models.CharField(max_length=128, db_index=True)
    type = models.CharField(max_length=128, db_index=True)
    url = models.CharField(max_length=256, unique=True)
    data = models.TextField()

    class Meta:
        unique_together = ("id", "type")
        index_together = ["id", "type"]

    def __str__(self):
        return self.url

    def data_as_dict(self):
        import json
        return json.loads(self.data)


class Lord(models.Model):
    data_id = models.CharField(max_length=128, db_index=True, unique=True)
    name = models.CharField(max_length=128, db_index=True)

    def __str__(self):
        return self.name


class Place(models.Model):
    data_id = models.CharField(max_length=128, db_index=True, unique=True)
    name = models.CharField(max_length=128, db_index=True, unique=True)
    county = models.CharField(max_length=128)
    hundred = models.CharField(max_length=128, null=True)
    longitude = models.DecimalField(decimal_places=10, max_digits=20)
    latitude = models.DecimalField(decimal_places=10, max_digits=20)
    roads = models.ManyToManyField("self", related_name="roads")

    def __str__(self):
        return '%s (%f, %f)' % (self.name, self.latitude, self.longitude)

    def main_settlement_type(self):
        types = {}
        for s in self.settlement_set.all():
            types[s.population_type] = types.get(s.population_type, 0) + s.population
        if types:
            return POPULATION_TYPES_DICT[max(types, key=types.get)]
        else:
            return POPULATION_TYPES_DICT[PEASANTS]


class Settlement(models.Model):
    data_id = models.CharField(max_length=128, db_index=True, unique=True)
    place = models.ForeignKey(Place)
    head_of_manor = models.CharField(max_length=128, null=True)
    lord = models.ForeignKey(Lord)
    overlord = models.ForeignKey(Lord, related_name='+')
    value = models.DecimalField(decimal_places=2, max_digits=20)

    population_type = models.CharField(max_length=1,
                                       choices=POPULATION_TYPES,
                                       default=PEASANTS)
    population = models.IntegerField(default=0)

    def __str__(self):
        return self.place.name + '>' + str(self.head_of_manor) + '>' + self.lord.name + '>' + self.overlord.name


