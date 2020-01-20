from unittest import TestCase

from ..oceania import (
    Australia,
    MarshallIslands,
    NewZealand,
    # Australian territories
    AustralianCapitalTerritory,
    NewSouthWales,
    NorthernTerritory,
    Queensland,
    SouthAustralia,
    Tasmania,
    # FIXME: there's no ISO code for this city. Shall we add it?
    # Hobart,
    Victoria,
    WesternAustralia
)

from ..registry import registry

AUSTRALIAN_TERRITORIES = (
    AustralianCapitalTerritory,
    NewSouthWales,
    NorthernTerritory,
    Queensland,
    SouthAustralia,
    Tasmania,
    Victoria,
    WesternAustralia
)


class RegistryOceania(TestCase):
    def test_oceania(self):
        classes = (v for k, v in registry.region_registry.items())
        classes = list(classes)
        self.assertIn(Australia, classes)
        self.assertIn(MarshallIslands, classes)
        self.assertIn(NewZealand, classes)
        for klass in AUSTRALIAN_TERRITORIES:
            self.assertIn(klass, classes)

    def test_australia_territories(self):
        # Get all the subregions
        classes = (v for k, v in registry.get_subregions('AU').items())
        classes = list(classes)
        for klass in AUSTRALIAN_TERRITORIES:
            self.assertIn(klass, classes)
