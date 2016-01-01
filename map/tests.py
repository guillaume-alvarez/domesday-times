from django.test import TestCase

# Create your tests here.
from map.models import Place
from map.management.commands.loadmap import guess_coordinates


class LoadmapTestCase(TestCase):
    def test_guess_coordinates(self):
        place = Place()
        guess_coordinates(place, "POINT (1.0322657208099999 52.5630827919000012)")
        self.assertEqual(place.latitude, 52.5630827919)
        self.assertEqual(place.longitude, 1.03226572081)