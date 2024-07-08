from django.test import TestCase
from backend.scraper.utils import lib


class LibTest(TestCase):
    # def setUp(self):

    def test_remove_keywords_from_game_title(self):
        """Correctly removes keywords from game title"""
        titles = ['GTAV key', 'GTAV keys', 'GTAV giveaway', 'GTAV demo', 'GTAV dlc', 'GTAV closed beta', 'GTAV beta',
                  'GTAV alpha', 'GTAV closed alpha', 'GTAV preview', 'GTAV game',
                  'GTAV on steam', 'GTAV on gog', 'GTAV on epic games', 'GTAV on epic games store', 'GTAV on egs',
                  'GTAV on uplay', 'GTAV on ubisoft', 'GTAV on ubisoft connect',
                  'GTAV on pc', 'GTAV on playstation', 'GTAV on ps4', 'GTAV on ps5',
                  'GTAV on xb', 'GTAV on xbox', 'GTAV on xbox one', 'GTAV on xbox 1', 'GTAV on xbox 360',
                  'GTAV on nintendo switch', 'GTAV on switch']
        self.assert_title_found(titles, 'GTAV')

    def test_keeps_keywords_from_game_title(self):
        """Correctly keeps keywords from game title"""
        self.assert_title_found(['GTAV game pack'], 'GTAV game pack')
        self.assert_title_found(['GTAV game of'], 'GTAV game of')

    def test_doesnt_get_any_title(self):
        """Correctly detect no title"""
        titles = ['key', 'keys', 'giveaway', 'demo', 'dlc', 'closed beta', 'beta',
                  'alpha', 'closed alpha', 'preview', 'in-game', 'game',
                  'on steam', 'on gog', 'on epic games', 'on epic games store', 'on egs',
                  'on uplay', 'on ubisoft', 'on ubisoft connect',
                  'on pc', 'on playstation', 'on ps4', 'on ps5',
                  'on xb', 'on xbox', 'on xbox one', 'on xbox 1', 'on xbox 360',
                  'on nintendo switch', 'on switch']
        self.assert_title_found(titles, '')

    def assert_title_found(self, titles, expected_title):
        for title in titles:
            result = lib.get_giveaway_title(title)
            self.assertNotEqual(result, None)
            self.assertEqual(result, expected_title)

    def assert_title_not_found(self, titles, unexpected_title):
        for title in titles:
            result = lib.get_giveaway_title(title)
            self.assertNotEqual(result, unexpected_title)
