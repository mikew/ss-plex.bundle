import plex_nose

class TestDownloads(plex_nose.TestCase):
    def test_main_menu():
        import mock

        @mock.patch.object(bridge.download, 'queue', return_value = [])
        @mock.patch.object(bridge.download, 'failed', return_value = [])
        def test(*a):
            container = downloads.MainMenu()
            [m.assert_called_once_with() for m in a]
            return container

        container = test()
        # the refresh button
        eq_(len(container), 1)

    def test_main_menu_when_downloading():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'assumed_running', return_value = True)
        @mock.patch.object(bridge.download, 'current', return_value = download)
        def test(*a):
            container = downloads.MainMenu()
            return container

        container = test()
        title_button = container.objects[0]
        progress_button = container.objects[1]
        speed_button = container.objects[2]

        eqL_(title_button.title, download['title'])
        eqL_(progress_button.title, '- 0% of ?')
        eqL_(speed_button.title, '- ? remaining; 0 average.')
        eqcb_(title_button.key, downloads.Options,
                endpoint = download['endpoint'])

    def test_main_menu_with_queue():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'queue', return_value = [download])
        def test(*a):
            container = downloads.MainMenu()
            return container

        container = test()
        subject = container.objects[0]

        eqL_(subject.title, download['title'])
        eqcb_(subject.key, downloads.Options,
                endpoint = download['endpoint'])

    def test_main_menu_with_failed():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'failed', return_value = [download])
        def test(*a):
            container = downloads.MainMenu()
            return container

        container = test()
        subject = container.objects[0]

        eqL_(subject.title, download['title'])
        eqcb_(subject.key, downloads.Options,
                endpoint = download['endpoint'])

    def test_options():
        import mock

        @mock.patch.object(bridge.download, 'from_queue', return_value = None)
        @mock.patch.object(bridge.download, 'from_failed', return_value = None)
        def test(*a):
            return downloads.Options('/')

        container = test()
        eqL_(container.header, 'heading.error')
        eqF_(container.message, 'download.response.not-found')

    def test_options_for_current():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'from_queue', return_value = download)
        @mock.patch.object(bridge.download, 'from_failed', return_value = None)
        @mock.patch.object(bridge.download, 'is_current', return_value = True)
        @mock.patch.object(bridge.download, 'curl_running', return_value = True)
        def test(*a):
            return downloads.Options(download['endpoint'])

        container = test()
        eq_(container.title1, download['title'])
        eq_(len(container), 2)

        eqL_(container.objects[0].title, 'download.heading.next')
        eqcb_(container.objects[0].key, downloads.NextSource)

        eqL_(container.objects[1].title, 'download.heading.cancel')
        eqcb_(container.objects[1].key, downloads.Cancel, endpoint = download['endpoint'])

    def test_options_for_current_when_stalled():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'from_queue', return_value = download)
        @mock.patch.object(bridge.download, 'from_failed', return_value = None)
        @mock.patch.object(bridge.download, 'is_current', return_value = True)
        @mock.patch.object(bridge.download, 'curl_running', return_value = False)
        def test(*a):
            return downloads.Options(download['endpoint'])

        container = test()
        eq_(container.title1, download['title'])
        eq_(len(container), 1)

        eqL_(container.objects[0].title, 'download.heading.repair')
        eqcb_(container.objects[0].key, downloads.DispatchForce)

    def test_options_for_queue():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'from_queue', return_value = download)
        @mock.patch.object(bridge.download, 'from_failed', return_value = None)
        def test(*a):
            return downloads.Options(download['endpoint'])

        container = test()
        eq_(container.title1, download['title'])
        eq_(len(container), 1)

        eqL_(container.objects[0].title, 'download.heading.cancel')
        eqcb_(container.objects[0].key, downloads.Cancel, endpoint = download['endpoint'])

    def test_options_for_failed():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'from_queue', return_value = None)
        @mock.patch.object(bridge.download, 'from_failed', return_value = download)
        def test(*a):
            return downloads.Options(download['endpoint'])

        container = test()
        eq_(container.title1, download['title'])
        eq_(len(container), 1)

        eqL_(container.objects[0].title, 'download.heading.cancel')
        eqcb_(container.objects[0].key, downloads.Cancel, endpoint = download['endpoint'])
