from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets, renderers

from .models import Place, Settlement, Lord


# Serializers define the API representation.
class SettlementSerializer(serializers.ModelSerializer):
    lord = serializers.SlugRelatedField(read_only=True, slug_field='name')
    lord_id = serializers.PrimaryKeyRelatedField(read_only=True)
    overlord = serializers.SlugRelatedField(read_only=True, slug_field='name')
    overlord_id = serializers.PrimaryKeyRelatedField(read_only=True)
    population_type = serializers.CharField(source='get_population_type_display')
    place_name = serializers.SerializerMethodField()
    class Meta:
        model = Settlement
        fields = '__all__'

    def get_place_name(self, obj):
        return obj.place.name


class PlaceSerializer(serializers.ModelSerializer):
    roads = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    type = serializers.CharField(source='main_settlement_type')
    class Meta:
        model = Place
        fields = ('id', 'longitude', 'latitude', 'roads', 'type', 'name')


class PlaceDetailSerializer(serializers.ModelSerializer):
    settlement_set = SettlementSerializer(many=True, read_only=True)
    roads = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    type = serializers.CharField(source='main_settlement_type')
    class Meta:
        model = Place
        fields = '__all__'



class LordSerializer(serializers.ModelSerializer):
    settlement_set = SettlementSerializer(many=True, read_only=True)
    class Meta:
        model = Lord
        fields = '__all__'


# ViewSets define the view behavior.
class PlaceViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Place.objects.all()
    renderer_classes = (renderers.JSONRenderer, )
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PlaceDetailSerializer
        else:
            return PlaceSerializer


class SettlementViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Settlement.objects.all()
    serializer_class = SettlementSerializer
    renderer_classes = (renderers.JSONRenderer, )


class LordViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Lord.objects.all()
    serializer_class = LordSerializer
    renderer_classes = (renderers.JSONRenderer, )


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'places', PlaceViewset, base_name='place')
router.register(r'settlements', SettlementViewset, base_name='settlement')
router.register(r'lords', LordViewset, base_name='lord')

# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^', include(router.urls)),
]
