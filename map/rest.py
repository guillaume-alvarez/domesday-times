from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets, renderers

from .models import Place, Settlement


# Serializers define the API representation.
class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'


class SettlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settlement
        fields = '__all__'


# ViewSets define the view behavior.
class PlaceViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    renderer_classes = (renderers.JSONRenderer, )


class SettlementViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    renderer_classes = (renderers.JSONRenderer, )


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'places', PlaceViewset, base_name='place')
router.register(r'settlements', SettlementViewset, base_name='settlement')

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
]
