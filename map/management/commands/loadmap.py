from django.core.management.base import BaseCommand, CommandError
from map.models import *

import requests
import re
import traceback

API_URL = 'http://opendomesday.org/api/1.0/'


class Command(BaseCommand):
    help = 'Load the map from the OpenDomesday website data'

    # retrieve updated data
    def load_data(self, endpoints, action):
        s = requests.Session()
        for endpoint in endpoints:
            url = API_URL + endpoint
            self.stdout.write('Load data from %s' % url)
            try:
                r = s.get(url)
                r.raise_for_status()
                data = r.json()
                action(data, url)
            except Exception as ex:
                self.stderr.write('Cannot load %s: %s' % (url, ex))
                traceback.print_exc(file=self.stderr)

    def handle(self, *args, **options):
        # clean the content in DB
        Settlement.objects.all().delete()
        Lord.objects.all().delete()
        Place.objects.all().delete()

        # first list existing places
        places = set()
        counties = {}
        hundreds = {}

        def load_counties(data, url):
            for county in data:
                counties[county['id']] = county['name']
                places.update([place['id'] for place in county['places_in_county']])
        self.load_data(['county/'], load_counties)

        def load_hundreds(data, url):
            for hundred in data:
                hundreds[hundred['id']] = hundred['name']
                places.update([place['id'] for place in hundred['places_in_hundred']])
        self.load_data(['hundred/'], load_hundreds)

        manors_to_places = {}

        # then create the places in DB from web data
        def load_place(data, url):
            if not data['location']:
                return

            place = Place(name=data['vill'], url=url,
                          county=counties[data['county'][0]['id']], hundred=hundreds[data['hundred'][0]['id']])
            guess_coordinates(place, data['location'])
            place.save()
            for manor in data['manors']:
                manors_to_places[manor['id']] = place
        self.load_data(['place/' + str(id) for id in places if id < 100], load_place)

        # and do the same for settlements with a leader
        def load_manor(manor, url):
            lord = get_lord(first(manor, 'lord86', 'lord66', 'teninchief', 'overlord66')[0])
            overlord = get_lord(first(manor, 'teninchief', 'overlord66', 'lord86', 'lord66')[0])
            overlord.save()
            Settlement(place=manors_to_places[manor['id']],
                       head_of_manor=manor['headofmanor'], value=first(manor, 'value86', 'geld'),
                       lord=lord, overlord=overlord,
                       url=url).save()
        self.load_data(['manor/' + str(id) for id in manors_to_places], load_manor)

        self.stdout.write(self.style.SUCCESS('Successfully loaded map data from  "%s"' % API_URL))


def first(data, *fields):
    for f in fields:
        if f in data:
            value = data[f]
            if isinstance(value, list):
                if len(value) > 0:
                    return value
            else:
                if value:
                    return value
    return None

def get_lord(name):
    lords = Lord.objects.filter(name=name)
    if lords:
        return lords[0]

    lord = Lord(name=name, url=API_URL)
    lord.save()
    return lord


POINT = re.compile(r"POINT\s+\((-?\d+\.\d+)\s+(\d+\.\d+)\)")


def guess_coordinates(place, location):
    '''
    Translate coordinates from web set to longitude/latitude.
    :param place: a Place object to enrich with coordinates
    :param location: "POINT (1.0322657208099999 52.5630827919000012)"
    '''
    m = POINT.match(location)
    place.longitude = float(m.group(1))
    place.latitude = float(m.group(2))