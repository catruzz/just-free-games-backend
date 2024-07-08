from django.test import TestCase
from backend.models import Giveaway
from backend.scraper.utils import lib


class LibTest(TestCase):
    # def setUp(self):

    def test_get_game_type(self):
        """Correctly detect GAME type"""
        self.assert_type_found(['game'], Giveaway.Type.GAME)

    def test_get_loot_type(self):
        """Correctly detect LOOT type"""
        types = ['pack', 'gift', 'crate', 'skin', 'kit', 'loot']
        self.assert_type_found(types, Giveaway.Type.LOOT)

    def test_get_dlc_type(self):
        """Correctly detect DLC type"""
        types = ['dlc']
        self.assert_type_found(types, Giveaway.Type.DLC)

    def test_get_beta_type(self):
        """Correctly detect BETA type"""
        self.assert_type_found(['beta'], Giveaway.Type.BETA)

    def test_get_alpha_type(self):
        """Correctly detect ALPHA type"""
        self.assert_type_found(['alpha'], Giveaway.Type.ALPHA)

    def test_get_membership_type(self):
        """Correctly detect MEMBERSHIP type"""
        self.assert_type_found(['membership'], Giveaway.Type.MEMBERSHIP)

    def test_get_demo_type(self):
        """Correctly detect DEMO type"""
        self.assert_type_found(['demo'], Giveaway.Type.DEMO)

    def test_get_other_type(self):
        """Correctly detect OTHER type"""
        self.assert_type_found(['asd'], Giveaway.Type.OTHER)

    def assert_type_found(self, types, expected_title):
        result = lib.get_giveaway_type(' '.join(types))
        self.assertNotEqual(result, None)
        self.assertEqual(result, expected_title)

        for type in types:
            result = lib.get_giveaway_type(type)
            self.assertNotEqual(result, None)
            self.assertEqual(result, expected_title)

    def assert_type_not_found(self, types, unexpected_title):
        result = lib.get_giveaway_type(' '.join(types))
        self.assertNotEqual(result, unexpected_title)

        for type in types:
            result = lib.get_giveaway_type(type)
            self.assertNotEqual(result, unexpected_title)
