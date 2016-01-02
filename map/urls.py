from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='map'),
    url(r'^table/$', views.map_table, name='map-table'),
    url(r'^pixi/$', views.map_pixi, name='map-table'),
    url(r'^places.json$', views.get_places, name='map-places'),
]