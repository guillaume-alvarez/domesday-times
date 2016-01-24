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

    def download_domesday(self):
        DomesdayData.objects.all().delete()

        # load counties and hundreds data
        # we use them to list places
        places = set()

        def load_counties(data, url):
            for county in data:
                places.update([place['id'] for place in county['places_in_county']])
                yield DomesdayData(fid=county['id'], type='county', url=url+county['id'], data=json.dumps(county))
        DomesdayData.objects.bulk_create(download([API_URL + 'county/'], load_counties))

        def load_hundreds(data, url):
            for hundred in data:
                places.update([place['id'] for place in hundred['places_in_hundred']])
                yield DomesdayData(fid=hundred['id'], type='hundred', url=url+hundred['id'], data=json.dumps(hundred))
        DomesdayData.objects.bulk_create(download([API_URL + 'hundred/'], load_hundreds))

        # then load the places in DB from web data (and collect manors ids)
        manors = set()
        def load_place(place, url):
            for manor in place['manors']:
                manors.add(manor['id'])
            yield DomesdayData(fid=place['id'], type='place', url=url, data=json.dumps(place))
        DomesdayData.objects.bulk_create(download([API_URL + 'place/' + str(id) for id in places if int(id)], load_place))

        # and do the same for manors
        def load_manor(manor, url):
            yield DomesdayData(fid=manor['id'], type='manor', url=url, data=json.dumps(manor))
        DomesdayData.objects.bulk_create(download([API_URL + 'manor/' + str(id) for id in manors], load_manor))

        self.stdout.write(self.style.SUCCESS('Successfully loaded Domesday Book data from "%s"' % API_URL))

    def download_names(self):
        import bs4 as BeautifulSoup
        import string
        URL = re.compile(r"/name/(\d+)/([a-zA-Z0-9_-]+)/")
        def load_names(html, url):
            soup = BeautifulSoup.BeautifulSoup(html, "html.parser")
            for li in soup.find_all('li', {'class': None, 'id': None}):
                if li.a:
                    url = URL.match(li.a['href'])
                    if url:
                        id = url.group(1)
                        slug = url.group(2)
                        name = li.get_text(strip=True)
                        yield DomesdayData(fid=url.group(1), type='name', url=url,
                                           data=json.dumps(dict(id=id, slug=slug, name=name)))

        names = download(['http://opendomesday.org/name/?indexChar=' + str(c) for c in string.ascii_uppercase],
                         load_names, json=False)
        DomesdayData.objects.bulk_create(names)
        self.stdout.write(self.style.SUCCESS(
                'Successfully loaded Domesday Book %d names from "http://opendomesday.org/name/"'
                % DomesdayData.objects.filter(type='name').count()))

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

    def load_lords(self):
        import csv
        Lord.objects.all().delete()
        TO_DELETE = re.compile('[' + re.escape('<>[]()') + ']')
        COMMA = re.compile(r"(.+), (.+)")
        def normalize_name(name):
            name = TO_DELETE.sub('', name)
            comma = COMMA.match(name)
            if comma:
                name = comma.group(2) + ' ' + comma.group(1)
            return name
        lords = {}
        with open('map/data/Names.csv', newline='') as file:
            for lord in csv.DictReader(file, delimiter=';', quotechar='"'):
                try:
                    id = lord['NamesIdx']
                    lords[id] = Lord(data_id=id, name=normalize_name(lord['Name']))
                except Exception as ex:
                    log.exception('Cannot load %s: %s', lord, ex)
                    # help debug by reporting it in console
                    traceback.print_exc(file=self.stderr)

        for data in DomesdayData.objects.filter(type='name'):
            lord = data.data_as_dict()
            try:
                id = lord['id']
                if id not in lords:
                    lords[id] = Lord(data_id=id, name=normalize_name(lord['name']))
            except Exception as ex:
                log.exception('Cannot load %s: %s', lord, ex)
                # help debug by reporting it in console
                traceback.print_exc(file=self.stderr)
        Lord.objects.bulk_create(lords.values())
        self.stdout.write(self.style.SUCCESS('Successfully loaded %d lords.' % Lord.objects.count()))

    def load_settlements(self):
        """Use downloaded data to create settlements and lords by our rules."""

        # clean the content in DB
        Settlement.objects.all().delete()

        places = {p.data_id: p for p in Place.objects.all()}

        settlements = []
        for data in DomesdayData.objects.filter(type='manor'):
            try:
                manor = data.data_as_dict()
                place_id = str(manor['place'][0]['id'])
                if place_id in places:
                    lord = get_lord(manor, 'lord86', 'lord66', 'teninchief', 'overlord66')
                    overlord = get_lord(manor, 'teninchief', 'overlord66', 'lord86', 'lord66')
                    settlements.append(Settlement(data_id=manor['id'], place=places[place_id],
                                                  head_of_manor=manor['headofmanor'],
                                                  value=settlement_value(manor),
                                                  lord=lord, overlord=overlord))
            except Exception as ex:
                log.exception('Cannot load %s: %s', manor, ex)
                # help debug by reporting it in console
                traceback.print_exc(file=self.stderr)
        Settlement.objects.bulk_create(settlements)
        self.stdout.write(self.style.SUCCESS('Successfully loaded %d settlements.' % Settlement.objects.count()))

    def create_roads(self):
        """Compute the roads between the different places"""

        ThroughModel = Place.roads.through
        ThroughModel.objects.all().delete()

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
        self.stdout.write(self.style.SUCCESS('Computed %d triangles from %d points.' % (len(triangles), len(points))))

        segments = set()
        for tri in triangles:
            p0 = points_list[tri[0]]
            p1 = points_list[tri[1]]
            p2 = points_list[tri[2]]
            # order between points does not matter: all in all it's the same link
            segments.add(frozenset([p0, p1]))
            segments.add(frozenset([p0, p2]))
            segments.add(frozenset([p1, p2]))
        self.stdout.write(self.style.SUCCESS('Computed %d roads from %d places.' % (len(segments), Place.objects.count())))

        segments_list = [tuple(iter(s)) for s in segments]
        def filter_longer(l):
            # recompute the links every time to avoid unconnected nodes
            nb_links = {}
            for s in l:
                nb_links[s[0]] = nb_links.get(s[0], 0) + 1
                nb_links[s[1]] = nb_links.get(s[1], 0) + 1
            def distance(segment):
                p0 = segment[0]
                p1 = segment[1]
                return ((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2) * (2 ** min(nb_links[p0], nb_links[p1]))
            l.sort(key=distance)
            return l[:int(0.99 * float(len(l)))]
        for _ in range(1,10):
            segments_list = filter_longer(segments_list)

        roads = []
        for s in segments_list:
            p0 = points[s[0]]
            p1 = points[s[1]]
            roads.append(ThroughModel(from_place_id=p0.pk, to_place_id=p1.pk))
            roads.append(ThroughModel(from_place_id=p1.pk, to_place_id=p0.pk))
        ThroughModel.objects.bulk_create(roads)
        self.stdout.write(self.style.SUCCESS('Stored %d roads items in DB.' % ThroughModel.objects.count()))

    def all(self):
        self.download_domesday()
        self.load_places()
        self.load_lords()
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


def settlement_value(manor):
    try:
        return first(manor, 'value86', 'value66', 'valueqr', 'geld', 'villtax', 'payments')
    except:
        value = 0.0
        for key in ['lordsland', 'ploughlands', 'villagers', 'slaves', 'smallholders', 'femaleslaves', 'freemen', 'free2men', 'cottagers', 'otherpop', 'miscpop', 'burgesses', 'woodland', 'mills', 'millvalue', 'meadow', 'pasture', 'woodland', 'fisheries', 'salthouses', 'payments', 'churches', 'churchland', 'cobs_1086', 'cobs_1066', 'cattle_1086', 'cattle_1066', 'cows_1086', 'cows_1066', 'pigs_1086', 'pigs_1066', 'sheep_1086', 'sheep_1066', 'goats_1086', 'goats_1066', 'beehives_1086', 'beehives_1066', 'wild_mares_1086', 'wild_mares_1066']:
            try:
                value += int(manor[key] or 0.0)
            except Exception as e:
                log.debug(e)
                pass
        return value


def get_lord(manor, *fields):
    id = first(manor, *fields)[0]
    lords = Lord.objects.filter(data_id=id)
    if lords:
        return lords[0]

    log.warn('Could not find lord for %s for %s', id, manor)
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


def download(urls, action, json=True):
    """retrieve data from endpoints added to base url"""
    log.info('Will load %s', ', '.join(urls))
    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    max_requests = asyncio.Semaphore(20)
    results = []

    async def load(url, json):
        log.debug('Load data from %s ...', url)
        while True:
            async with max_requests:
                try:
                    async with session.get(url, compress=True) as resp:
                        try:
                            if resp.status != 200:
                                raise Exception('Error %d' % resp.status)
                            if json:
                                data = await resp.json()
                            else:
                                data = await resp.read()
                            results.extend(action(data, url))
                            log.debug('...loaded data from %s', url)
                            break
                        except Exception as ex:
                            log.exception('Cannot load %s: %s', url, ex)
                            # help debug by reporting it in console
                            traceback.print_exc()
                            break
                except Exception as get_ex:
                    if isinstance(get_ex, aiohttp.errors.ServerDisconnectedError) \
                            or isinstance(get_ex.__cause__, aiohttp.errors.ServerDisconnectedError):
                        log.warning('Failure to get %s: %s, will retry', url, repr(get_ex))
                        continue
    loop.run_until_complete(asyncio.wait([load(url, json) for url in urls]))
    session.close()
    log.info('Loaded %d items.', len(results))
    return results