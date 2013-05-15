import plex_nose

class TestBridgePrefKeys(plex_nose.TestCase):
    def test_avoid_flv_streaming():
        eq_(bridge.settings.get('avoid_flv_streaming'), Prefs['avoid_flv_streaming'])

    def test_avoid_flv_downloading():
        eq_(bridge.settings.get('avoid_flv_downloading'), Prefs['avoid_flv_downloading'])

    def test_download_limit():
        eq_(bridge.settings.get('download_limit'), Prefs['download_limit'])

    def test_download_strategy():
        eq_(bridge.settings.get('download_strategy'), Prefs['download_strategy'])

class TestRefreshSection(plex_nose.TestCase):
    def setUp(self):
        plex_nose.publish_local_file('Contents/Tests/library.xml', 'library_')
        plex_nose.publish_local_file('Contents/Tests/library-advanced.xml', 'library_advanced_')

    def test_show():
        import mock

        @mock.patch.object(bridge_init.XML, 'ElementFromURL', return_value = XML.ElementFromString(library_))
        @mock.patch.object(bridge_init.HTTP, 'Request')
        def test(update_mock, *a):
            bridge_init.refresh_section('show')
            update_mock.assert_called_once_with('http://127.0.0.1:32400/library/sections/2/refresh', immediate = True)

        test()

class TestMediaDestinations(plex_nose.TestCase):
    def setUp(self):
        plex_nose.publish_local_file('Contents/Tests/library.xml', 'library_')
        plex_nose.publish_local_file('Contents/Tests/library-advanced.xml', 'library_advanced_')

    def test_show_destination():
        import mock

        @mock.patch.object(bridge_init.XML, 'ElementFromURL', return_value = XML.ElementFromString(library_))
        def test(*a):
            eq_(bridge.settings.get('show_destination'), '/mnt/tc/video/incoming')

        test()

    def test_show_destination_advanced():
        import mock

        @mock.patch.object(bridge_init.XML, 'ElementFromURL', return_value = XML.ElementFromString(library_advanced_))
        def test(*a):
            eq_(bridge.settings.get('show_destination'), 'D:/Media/TV-Series/ssp')

        test()

    def test_movie_destination():
        import mock

        @mock.patch.object(bridge_init.XML, 'ElementFromURL', return_value = XML.ElementFromString(library_))
        def test(*a):
            eq_(bridge.settings.get('movie_destination'), '/mnt/tc/video/movies')

        test()

    def test_movie_destination_advanced():
        import mock

        @mock.patch.object(bridge_init.XML, 'ElementFromURL', return_value = XML.ElementFromString(library_advanced_))
        def test(*a):
            eq_(bridge.settings.get('movie_destination'), 'D:/Media/Video/ssp')

        test()

class TestAutoDownloadStrategy(plex_nose.TestCase):
    def test_macos():
        import mock

        @mock.patch.object(bridge_init, 'platform_os', return_value = 'MacOSX')
        def test(*a): eq_(bridge_init.download_strategy('auto'), 'curl')

        test()

    def test_windows():
        import mock

        @mock.patch.object(bridge_init, 'platform_os', return_value = 'Windows')
        def test(*a): eq_(bridge_init.download_strategy('auto'), 'curl')

        test()

    def test_linux():
        import mock

        @mock.patch.object(bridge_init, 'platform_os', return_value = 'Linux')
        def test(*a): eq_(bridge_init.download_strategy('auto'), 'wget')

        test()

    def test_other():
        import mock

        @mock.patch.object(bridge_init, 'platform_os', return_value = 'Unknown')
        def test(*a): eq_(bridge_init.download_strategy('auto'), 'curl')

        test()
