from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core import serializers

import logging
import json

from .models import Place

log = logging.getLogger(__name__)


# Create your views here.


def index(request):
    return redirect(map_pixi)


GPS_FACTOR = 100
LONGITUDE_MIN = int(-6.5 * GPS_FACTOR)
LONGITUDE_MAX = int(1.8 * GPS_FACTOR)
LATITUDE_MIN = int(49 * GPS_FACTOR)
LATITUDE_MAX = int(54.7 * GPS_FACTOR)


def map_table(request):
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
    return render(request, 'map/table.html', {'places':places})


def map_pixi(request):
    return render(request, 'map/pixi.html')


def search_places(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        places = Place.objects.filter(name__icontains=q).order_by('name')[:20]
        results = []
        for place in places:
            place_json = dict(
                id=place.id,
                label=place.name + ' (' + place.county + ')',
                value=place.name,
            )
            results.append(place_json)
        return JsonResponse(results, safe=False)
    else:
        return HttpResponse('fail', 'application/json')
