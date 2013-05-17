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
        eqcb_(title_button.key, downloads.OptionsForCurrent)

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
        eqcb_(subject.key, downloads.OptionsForQueue,
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
        eqcb_(subject.key, downloads.OptionsForFailed,
                endpoint = download['endpoint'])

    def test_options_for_endpoint():
        import mock

        @mock.patch.object(bridge.download, 'from_queue', return_value = None)
        @mock.patch.object(bridge.download, 'from_failed', return_value = None)
        def test(*a):
            return downloads.OptionsForEndpoint('/')

        container = test()
        eqL_(container.header, 'heading.error')
        eqF_(container.message, 'download.response.not-found')

    def test_options_for_current():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'current', return_value = download)
        @mock.patch.object(bridge.download, 'curl_running', return_value = True)
        def test(*a):
            return downloads.OptionsForCurrent()

        container = test()
        eq_(container.title1, download['title'])
        eq_(len(container), 2)

        eqL_(container.objects[0].title, 'download.heading.next')
        eqcb_(container.objects[0].key, downloads.NextSource)

        eqL_(container.objects[1].title, 'download.heading.cancel')
        eqcb_(container.objects[1].key, downloads.RemoveCurrent)

    def test_options_for_current_when_stalled():
        import mock

        download = dict(title = 'foo', endpoint = '/')
        @mock.patch.object(bridge.download, 'current', return_value = download)
        @mock.patch.object(bridge.download, 'curl_running', return_value = False)
        def test(*a):
            return downloads.OptionsForCurrent()

        container = test()
        eq_(container.title1, download['title'])
        eq_(len(container), 2)

        eqL_(container.objects[0].title, 'download.heading.force-success')
        eqcb_(container.objects[0].key, downloads.ForceSuccess)

        eqL_(container.objects[1].title, 'download.heading.force-failure')
        eqcb_(container.objects[1].key, downloads.ForceFailure)

    def test_options_for_queue():
        import mock

        download = dict(title = 'foo', endpoint = '/', media_hint = 'show')
        @mock.patch.object(bridge.download, 'from_queue', return_value = download)
        def test(*a):
            return downloads.OptionsForQueue(download['endpoint'])

        container = test()
        eq_(container.title1, download['title'])
        eq_(len(container), 1)

        eqL_(container.objects[0].title, 'download.heading.cancel')
        eqcb_(container.objects[0].key, downloads.Remove, endpoint = download['endpoint'])

    def test_options_for_failed():
        import mock

        download = dict(title = 'foo', endpoint = '/', media_hint = 'show')
        @mock.patch.object(bridge.download, 'from_failed', return_value = download)
        def test(*a):
            return downloads.OptionsForFailed(download['endpoint'])

        container = test()
        eq_(container.title1, download['title'])
        eq_(len(container), 2)

        eqL_(container.objects[0].title, 'download.heading.retry')
        eqcb_(container.objects[0].key, downloads.Queue, **download)

        eqL_(container.objects[1].title, 'download.heading.cancel')
        eqcb_(container.objects[1].key, downloads.RemoveFailed, endpoint = download['endpoint'])

    def test_queue():
        import mock

        download = dict(title = 'foo', endpoint = '/', media_hint = 'show')
        @mock.patch.object(downloads, 'dispatch_download_threaded')
        def test(*a):
            return downloads.Queue(**download)

        container = test()
        eqL_(container.header, 'heading.download')
        eqF_(container.message, 'download.response.added')

    def test_queue_when_exists():
        import mock

        download = dict(title = 'foo', endpoint = '/', media_hint = 'show')
        @mock.patch.object(bridge.download, 'queue', return_value = [ download ])
        @mock.patch.object(downloads, 'dispatch_download_threaded')
        def test(*a):
            return downloads.Queue(**download)

        container = test()
        eqL_(container.header, 'heading.download')
        eqF_(container.message, 'download.response.exists')

    def test_remove():
        import mock
        download = dict(title = 'foo', endpoint = '/', media_hint = 'show')
        @mock.patch.object(bridge.download, 'queue', return_value = [download])
        def test(*a):
            container = downloads.Remove(endpoint = download['endpoint'])
            ok_(download not in bridge.download.history())
            return container

        container = test()
        eqL_(container.header, 'heading.download')
        eqF_(container.message, 'download.response.cancel')

    def test_remove_current():
        import mock
        download = dict(title = 'foo', endpoint = '/', media_hint = 'show')
        @mock.patch.object(bridge.download, 'current', return_value = download)
        @mock.patch.object(bridge.download, 'is_current', return_value = True)
        @mock.patch.object(bridge.download, 'command')
        def test(command_mock, *a):
            container = downloads.RemoveCurrent()
            command_mock.asset_called_once_with('cancel')
            return container

        container = test()
        eqL_(container.header, 'heading.download')
        eqF_(container.message, 'download.response.cancel')

    def test_remove_failed():
        pass

    def test_force_success():
        import mock

        bridge.download.force_success = mock.Mock()
        container = downloads.ForceSuccess()

        eqL_(container.header, 'heading.download')
        eqL_(container.message, 'download.response.force-success')
        bridge.download.force_success.assert_called_once_with()

    def test_force_failure():
        import mock

        bridge.download.force_failure = mock.Mock()
        container = downloads.ForceFailure()

        eqL_(container.header, 'heading.download')
        eqL_(container.message, 'download.response.force-failure')
        bridge.download.force_failure.assert_called_once_with()
