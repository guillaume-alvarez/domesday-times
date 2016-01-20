from django.core.management.base import BaseCommand, CommandError
from map.models import *

import logging
import aiohttp
import asyncio
import re
import traceback
import json

API_URL = 'http://opendomesday.org/api/1.0/'
log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Load the map from the OpenDomesday website data'

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument('--actions',
            default='all',
            help='Select actions to execute, by default execute all')

    def handle(self, *args, **options):
        """Just call the actions required by user."""
        for action in options['actions'].split(','):
            getattr(self, action)()

    def download(self, endpoints, action):
        """retrieve data from endpoints added to base url"""
        log.info('Will load %s from %s', ', '.join(endpoints), API_URL)
        loop = asyncio.get_event_loop()
        session = aiohttp.ClientSession(loop=loop)
        max_requests = asyncio.Semaphore(20)
        results = []

        async def load(endpoint):
            url = API_URL + endpoint
            log.debug('Load data from %s ...', url)
            while True:
                async with max_requests:
                    try:
                        async with session.get(url, compress=True) as resp:
                            try:
                                if resp.status != 200:
                                    raise Exception('Error %d' % resp.status)
                                data = await resp.json()
                                results.extend(action(data, url))
                                log.debug('...loaded data from %s', url)
                                break
                            except Exception as ex:
                                log.exception('Cannot load %s: %s', url, ex)
                                # help debug by reporting it in console
                                traceback.print_exc(file=self.stderr)
                                break
                    except Exception as get_ex:
                        if isinstance(get_ex, aiohttp.errors.ServerDisconnectedError) \
                                or isinstance(get_ex.__cause__, aiohttp.errors.ServerDisconnectedError):
                            log.warning('Failure to get %s: %s, will retry', url, repr(get_ex))
                            continue
        loop.run_until_complete(asyncio.wait([load(endpoint) for endpoint in endpoints]))
        session.close()
        log.info('Loaded %d items.', len(results))
        return results

    def download_domesday(self):
        DomesdayData.objects.all().delete()

        # load counties and hundreds data
        # we use them to list places
        places = set()

        def load_counties(data, url):
            for county in data:
                places.update([place['id'] for place in county['places_in_county']])
                yield DomesdayData(fid=county['id'], type='county', url=url+county['id'], data=json.dumps(county))
        DomesdayData.objects.bulk_create(self.download(['county/'], load_counties))

        def load_hundreds(data, url):
            for hundred in data:
                places.update([place['id'] for place in hundred['places_in_hundred']])
                yield DomesdayData(fid=hundred['id'], type='hundred', url=url+hundred['id'], data=json.dumps(hundred))
        DomesdayData.objects.bulk_create(self.download(['hundred/'], load_hundreds))

        # then load the places in DB from web data (and collect manors ids)
        manors = set()
        def load_place(place, url):
            for manor in place['manors']:
                manors.add(manor['id'])
            yield DomesdayData(fid=place['id'], type='place', url=url, data=json.dumps(place))
        DomesdayData.objects.bulk_create(self.download(['place/' + str(id) for id in places if int(id)], load_place))

        # and do the same for manors
        def load_manor(manor, url):
            yield DomesdayData(fid=manor['id'], type='manor', url=url, data=json.dumps(manor))
        DomesdayData.objects.bulk_create(self.download(['manor/' + str(id) for id in manors], load_manor))

        self.stdout.write(self.style.SUCCESS('Successfully loaded Domesday Book data from "%s"' % API_URL))

    def load_places(self):
        """Use downloaded data to create places by our rules."""
        # clean the content in DB
        Place.objects.all().delete()

        counties = {c['id']: c['name'] for c in
                    map(DomesdayData.data_as_dict, DomesdayData.objects.filter(type='county'))}
        hundreds = {h['id']: h['name'] for h in
                    map(DomesdayData.data_as_dict, DomesdayData.objects.filter(type='hundred'))}
        hundreds[None] = None

        # then create the places in DB from web data
        places = []
        for p in DomesdayData.objects.filter(type='place'):
            data = p.data_as_dict()
            if not data['location']:
                continue
            place = Place(data_id=data['id'], name=data['vill'],
                          county=counties[sub(data, 'county', 0, 'id')],
                          hundred=hundreds[sub(data, 'hundred', 0, 'id')])
            parse_coordinates(place, data['location'])
            places.append(place)
        Place.objects.bulk_create(places)

        self.stdout.write(self.style.SUCCESS('Successfully loaded %d places.' % Place.objects.count()))

    def load_settlements(self):
        """Use downloaded data to create settlements and lords by our rules."""

        # clean the content in DB
        Settlement.objects.all().delete()
        Lord.objects.all().delete()

        places = {p.data_id: p for p in Place.objects.all()}

        settlements = []
        for data in DomesdayData.objects.filter(type='manor'):
            try:
                manor = data.data_as_dict()
                place_id = str(manor['place'][0]['id'])
                if place_id in places:
                    lord = get_lord(first(manor, 'lord86', 'lord66', 'teninchief', 'overlord66')[0])
                    overlord = get_lord(first(manor, 'teninchief', 'overlord66', 'lord86', 'lord66')[0])
                    settlements.append(Settlement(data_id=manor['id'], place=places[place_id],
                                                  head_of_manor=manor['headofmanor'],
                                                  value=check(0.0, first, manor, 'value86', 'value66', 'geld', 'villtax', 'millvalue', 'payments', 'burgesses'),
                                                  lord=lord, overlord=overlord))
            except Exception as ex:
                log.exception('Cannot load %s: %s', manor, ex)
                # help debug by reporting it in console
                traceback.print_exc(file=self.stderr)
        Settlement.objects.bulk_create(settlements)

        self.stdout.write(self.style.SUCCESS('Successfully loaded %d settlements and %s lords.' % (Settlement.objects.count(), Lord.objects.count())))

    def create_roads(self):
        """Compute the roads between the different places"""
        Road.objects.all().delete()

        points = {}
        for place in Place.objects.all():
            point = (float(place.longitude), float(place.latitude))
            if point in points:
                log.warn('Cannot replace %s by %s for %s', points[point], place, point)
            else:
                points[point] = place
        from map.pyshull import PySHull
        points_list = list(set(points.keys()))
        triangles = PySHull(points_list)
        self.stdout.write(self.style.SUCCESS('Computed %d triangles from %d points.' % (len(points), len(triangles))))

        segments = set()
        for tri in triangles:
            p0 = points_list[tri[0]]
            p1 = points_list[tri[1]]
            p2 = points_list[tri[2]]
            # order between points does not matter: all in all it's the same link
            segments.add(frozenset([p0, p1]))
            segments.add(frozenset([p0, p2]))
            segments.add(frozenset([p1, p2]))

        roads = []
        for s in segments:
            l = list(s)
            place0 = points[l[0]]
            place1 = points[l[1]]
            roads.append(Road(start=points[l[0]], end=points[l[1]]))
        Road.objects.bulk_create(roads)
        self.stdout.write(self.style.SUCCESS('Created %d roads from %d places.' % (Road.objects.count(), Place.objects.count())))

    def all(self):
        self.download_domesday()
        self.load_places()
        self.load_settlements()
        self.create_roads()


def check(default, func, *args):
    try:
        return func(*args)
    except Exception as e:
        log.warn(repr(e))
        return default


def sub(data, *keys):
    current = data
    for k in keys:
        try:
            current = current[k]
            if not current:
                return None
        except KeyError:
            log.exception('Cannot get %s from %s in %s', k, current, data)
    return current


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
    raise Exception('No %s in %s' % (', '.join(fields), data))


def get_lord(id):
    lords = Lord.objects.filter(name=id)
    if lords:
        return lords[0]

    lord = Lord(name=id, data_id=id)
    lord.save()
    return lord


POINT = re.compile(r"POINT\s+\((-?\d+\.\d+)\s+(\d+\.\d+)\)")


def parse_coordinates(place, location):
    '''
    Translate coordinates from web set to longitude/latitude.
    :param place: a Place object to enrich with coordinates
    :param location: "POINT (1.0322657208099999 52.5630827919000012)"
    '''
    m = POINT.match(location)
    place.longitude = float(m.group(1))
    place.latitude = float(m.group(2))