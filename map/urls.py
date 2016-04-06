from django.conf.urls import url, include

from . import views, rest

urlpatterns = [
    url(r'^$', views.index, name='map'),
    url(r'^table/$', views.map_table, name='map-table'),
    url(r'^pixi/$', views.map_pixi, name='map-table'),
    url(r'^api/', include(rest.router.urls)),

    url(r'^api/search_places/', views.search_places, name='search-places'),
]