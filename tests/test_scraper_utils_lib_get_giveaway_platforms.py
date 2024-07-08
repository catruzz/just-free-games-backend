from django.test import TestCase
from backend.scraper.utils import lib


class LibTest(TestCase):
    # def setUp(self):

    def test_get_steam_platform(self):
        """Correctly detect steam platform"""
        self.assert_platform_found(['Steam', 'Humblebundle'], 'steam')

    def test_get_gog_platform(self):
        """Correctly detect GOG platform"""
        self.assert_platform_found(['GOG'], 'gog')

    def test_get_epic_games_store_platform(self):
        """Correctly detect Epic Games Store platform"""
        platforms = ['Epic Games', 'EpicGames',
                     'Epic Games Store', 'EpicGamesStore', 'EGS']
        self.assert_platform_found(platforms, 'epic_games')

        results = lib.get_giveaway_platforms('epic')
        self.assertEqual(results, None)

    def test_get_ubisoft_platform(self):
        """Correctly detect Ubisoft Connect platform"""
        platforms = ['Ubisoft', 'Uplay', 'Ubisoft Connect', 'Ubisoft Connect']
        self.assert_platform_found(platforms, 'ubisoft_connect')

    def test_get_battlenet_platform(self):
        """Correctly detect Battle.net platform"""
        platforms = ['Blizzard', 'Battlenet', 'Battle.net']
        self.assert_platform_found(platforms, 'battle_net')

    def test_get_origin_platform(self):
        """Correctly detect Origin platform"""
        platforms = ['Origin', 'EA Games', 'EAGames',
                     'Electronic Arts', 'ElectronicArts']
        self.assert_platform_found(platforms, 'origin')

    def test_get_indiegala_platform(self):
        """Correctly detect Indiegala platform"""
        self.assert_platform_found(['Indiegala'], 'indiegala')

    def test_get_microsoft_platform(self):
        """Correctly detect Microsoft platform"""
        self.assert_platform_found(['Microsoft'], 'microsoft')

    def test_get_itch_io_platform(self):
        """Correctly detect Itch.io platform"""
        self.assert_platform_found(['Itch.io', 'Itchio', 'Itch'], 'itch_io')
        self.assert_platform_not_found(['switch'], 'itch_io')

    def test_get_rockstar_games_platform(self):
        """Correctly detect Rockstar Games platform"""
        self.assert_platform_found(['Rockstar'], 'rockstar_games')

    def test_get_oculus_platform(self):
        """Correctly detect Oculus platform"""
        self.assert_platform_found(['Oculus'], 'oculus')

    def test_get_pc_platform(self):
        """Correctly detect PC platform"""
        self.assert_platform_found(['PC'], 'pc')

    def test_get_ps4_platform(self):
        """Correctly detect PS4 platform"""
        platforms = ['Playstation 4', 'Playstation4', 'PS4']
        self.assert_platform_found(platforms, 'ps4')
        self.assert_platform_not_found(['ps'], 'ps4')

    def test_get_ps5_platform(self):
        """Correctly detect PS5 platform"""
        platforms = ['Playstation 5', 'Playstation5', 'PS5']
        self.assert_platform_found(platforms, 'ps5')
        self.assert_platform_not_found(['ps'], 'ps5')

    def test_get_playstation_platform(self):
        """Correctly detect Playstation platform"""
        self.assert_platform_found(['Playstation', 'PS'], 'playstation')
        self.assert_platform_not_found(['ps4', 'ps5'], 'playstation')

    def test_get_xbox_one_platform(self):
        """Correctly detect Xbox One platform"""
        platforms = ['Xbox One', 'XB One', 'Xbox One', 'XBOne', 'Xbox1', 'XB1']
        self.assert_platform_found(platforms, 'xbox_one')
        self.assert_platform_not_found(['Xbox', 'Xbox 360'], 'xbox_one')

    def test_get_xbox_360_platform(self):
        """Correctly detect Xbox 360 platform"""
        platforms = ['Xbox 360', 'XB 360', 'Xbox 360', 'XB360']
        self.assert_platform_found(platforms, 'xbox_360')
        platforms = ['Xbox', 'Xbox One', 'XB One',
                     'Xbox One', 'XBOne', 'Xbox1', 'XB1']
        self.assert_platform_not_found(platforms, 'xbox_360')

    def test_get_xbox_platform(self):
        """Correctly detect Xbox platform"""
        platforms = ['Xbox', 'XB']
        self.assert_platform_found(platforms, 'xbox')
        platforms = ['Xbox One', 'XB One', 'Xbox One', 'XBOne',
                     'Xbox1', 'XB1', 'Xbox 360', 'XB 360', 'Xbox 360', 'XB360']
        self.assert_platform_not_found(platforms, 'xbox')

    def test_get_switch_platform(self):
        """Correctly detect Switch platform"""
        self.assert_platform_found(['Switch'], 'switch')
        self.assert_platform_not_found(['Nintendo'], 'switch')

    def test_get_nintendo_platform(self):
        """Correctly detect Nintendo platform"""
        self.assert_platform_found(['Nintendo'], 'nintendo')
        self.assert_platform_not_found(['Switch'], 'nintendo')

    def test_get_amazon_platform(self):
        """Correctly detect Amazon Prime Gaming platform"""
        platforms = ['Amazon', 'Prime']
        self.assert_platform_found(platforms, 'amazon')

    def test_get_legacy_games_platform(self):
        """Correctly detect Legacy Games platform"""
        platforms = ['Legacy Games', 'legacy games']
        self.assert_platform_found(platforms, 'legacy_games')

    def test_get_ios_platform(self):
        """Correctly detect iOS platform"""
        platforms = ['iOS']
        self.assert_platform_found(platforms, 'ios')

    def test_get_android_platform(self):
        """Correctly detect Android platform"""
        platforms = ['Android']
        self.assert_platform_found(platforms, 'android')

    def test_get_mobile_platform(self):
        """Correctly detect Mobile platform"""
        platforms = ['Mobile']
        self.assert_platform_found(platforms, 'mobile')

    def test_doesnt_get_any_platform(self):
        """Correctly detect no platform"""
        results = lib.get_giveaway_platforms('asd')
        self.assertEqual(results, None)

    def assert_platform_found(self, platforms, expected_title):
        results = lib.get_giveaway_platforms(' '.join(platforms))
        self.assertNotEqual(results, None)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], expected_title)

        for platform in platforms:
            results = lib.get_giveaway_platforms(platform)
            self.assertNotEqual(results, None)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0], expected_title)

    def assert_platform_not_found(self, platforms, unexpected_title):
        results = lib.get_giveaway_platforms(' '.join(platforms))
        for result in results:
            self.assertNotEqual(result, unexpected_title)

        for platform in platforms:
            results = lib.get_giveaway_platforms(platform)
            for result in results:
                self.assertNotEqual(result, unexpected_title)
