from django.shortcuts import render
from django.http import HttpResponse

import logging

from .models import Place

# Create your views here.


log = logging.getLogger(__name__)

GPS_FACTOR = 100
LONGITUDE_MIN = int(-6.5 * GPS_FACTOR)
LONGITUDE_MAX = int(1.8 * GPS_FACTOR)
LATITUDE_MIN = int(49 * GPS_FACTOR)
LATITUDE_MAX = int(54.7 * GPS_FACTOR)


def england_map(request):
    places = [[list() for longitude in range(LONGITUDE_MAX - LONGITUDE_MIN)] for latitude in range(LATITUDE_MAX - LATITUDE_MIN)]
    for p in Place.objects.all():
        row = int(p.latitude * GPS_FACTOR) - LATITUDE_MIN
        if row >= len(places):
            log.warn('No row %d for %s', row, repr(p))
            continue
        col = int(p.longitude * GPS_FACTOR) - LONGITUDE_MIN
        if col >= len(places[row]):
            log.warn('No column %d for %s', col, repr(p))
            continue
        places[row][col].append(p)
    return render(request, 'map/index.html', {'places':places})