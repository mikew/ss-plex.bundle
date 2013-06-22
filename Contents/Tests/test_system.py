import plex_nose

class SystemMenuTests(plex_nose.TestCase):
    def test_main_menu():
        container = system.MainMenu()

        eq_(len(container), 4)
        eqL_(container.title1,      'heading.system')

        eqL_(container.objects[0].title, 'system.heading.reset')
        eqcb_(container.objects[0].key,  system.ResetMenu)

        eqL_(container.objects[1].title, 'system.heading.status')
        eqcb_(container.objects[1].key,  system.StatusMenu)

        eqL_(container.objects[2].title, 'system.heading.dispatch-force')
        eqcb_(container.objects[2].key,  downloads.DispatchForce)

        eqL_(container.objects[3].title, 'system.heading.sync-favorites')
        eqcb_(container.objects[3].key,  favorites.Sync)

    def test_reset_menu():
        container = system.ResetMenu()

        eq_(len(container), 6)
        eqL_(container.title1,      'system.heading.reset')

        eqL_(container.objects[0].title, 'system.heading.reset-favorites')
        eqcb_(container.objects[0].key,  system.ConfirmResetFavorites)

        eqL_(container.objects[1].title, 'system.heading.reset-search')
        eqcb_(container.objects[1].key,  system.ConfirmResetSearches)

        eqL_(container.objects[2].title, 'system.heading.reset-download-history')
        eqcb_(container.objects[2].key,  system.ConfirmResetDownloads)

        eqL_(container.objects[3].title, 'system.heading.reset-download-failed')
        eqcb_(container.objects[3].key,  system.ConfirmResetDownloadsFailed)

        eqL_(container.objects[4].title, 'system.heading.reset-ss-cache')
        eqcb_(container.objects[4].key,  system.ConfirmResetSSCache)

        eqL_(container.objects[5].title, 'system.heading.reset-factory')
        eqcb_(container.objects[5].key,  system.ConfirmResetFactory)

    def test_status_menu():
        import mock

        @mock.patch.object(plex_bridge, 'section_destination')
        def test(dest):
            container = system.StatusMenu()
            call = mock.call
            eq_(dest.call_args_list, [ call('movie'), call('show') ])
            return container

        container = test()
        eq_(len(container), 4)

        eqF_(container.objects[0].title,  'system.status.version')
        eqF_(container.objects[1].title,  'system.status.movie-destination')
        eqF_(container.objects[2].title,  'system.status.show-destination')
        eqF_(container.objects[3].title,  'system.status.download-strategy')

    def test_confirmations():
        container = system.ConfirmResetFavorites()
        eqL_(container.header,            'system.warning.reset-favorites')
        eqL_(container.objects[0].title,  'confirm.yes')

        container = system.ConfirmResetSearches()
        eqL_(container.header,            'system.warning.reset-search')
        eqL_(container.objects[0].title,  'confirm.yes')

        container = system.ConfirmResetDownloads()
        eqL_(container.header,            'system.warning.reset-download-history')
        eqL_(container.objects[0].title,  'confirm.yes')

        container = system.ConfirmResetDownloadsFailed()
        eqL_(container.header,            'system.warning.reset-download-failed')
        eqL_(container.objects[0].title,  'confirm.yes')

        container = system.ConfirmResetSSCache()
        eqL_(container.header,            'system.warning.reset-ss-cache')
        eqL_(container.objects[0].title,  'confirm.yes')

        container = system.ConfirmResetFactory()
        eqL_(container.header,            'system.warning.reset-factory')
        eqL_(container.objects[0].title,  'confirm.yes')

    def test_actual_resets():
        import mock

        @mock.patch.object(bridge.favorite, 'clear')
        def test_reset(reset_call):
            container = system.ResetFavorites()
            reset_call.assert_called_once_with()
            eqL_(container.header, 'heading.system')
            eqL_(container.message, 'system.response.reset-favorites')

        test_reset()

        @mock.patch.object(bridge.search, 'clear')
        def test_reset(reset_call):
            container = system.ResetSearches()
            reset_call.assert_called_once_with()
            eqL_(container.header, 'heading.system')
            eqL_(container.message, 'system.response.reset-search')

        test_reset()

        @mock.patch.object(bridge.download, 'clear_history')
        def test_reset(reset_call):
            container = system.ResetDownloads()
            reset_call.assert_called_once_with()
            eqL_(container.header, 'heading.system')
            eqL_(container.message, 'system.response.reset-download-history')

        test_reset()

        @mock.patch.object(bridge.download, 'clear_failed')
        def test_reset(reset_call):
            container = system.ResetDownloadsFailed()
            reset_call.assert_called_once_with()
            eqL_(container.header, 'heading.system')
            eqL_(container.message, 'system.response.reset-download-failed')

        test_reset()

        @mock.patch.object(system.ss.cache, 'reset')
        def test_reset(reset_call):
            container = system.ResetSSCache()
            reset_call.assert_called_once_with()
            eqL_(container.header, 'heading.system')
            eqL_(container.message, 'system.response.reset-ss-cache')

        test_reset()

        @mock.patch.object(system.Dict, 'Save')
        @mock.patch.object(system.Dict, 'Reset')
        @mock.patch.object(system.ss.cache, 'reset')
        def test_reset(*a):
            container = system.ResetFactory()

            for _m in a:
                _m.assert_called_once_with()

            eqL_(container.header, 'heading.system')
            eqL_(container.message, 'system.response.reset-factory')

        test_reset()
