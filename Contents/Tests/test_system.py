import plex_nose

class SystemMenuTests(plex_nose.TestCase):
    def test_main_menu():
        import system

        container = system.MainMenu()

        eq_(3, len(container.objects))
        eq_l('heading.system', container.title1)

        eq_l('system.heading.reset',          container.objects[0].title)
        eq_(Callback(system.ResetMenu),       container.objects[0].key)

        eq_l('system.heading.status',         container.objects[1].title)
        eq_(Callback(system.StatusMenu),      container.objects[1].key)

        eq_l('system.heading.dispatch-force', container.objects[2].title)
        eq_(Callback(DownloadsDispatchForce), container.objects[2].key)

    def test_reset_menu():
        import system

        container = system.ResetMenu()

        eq_(6, len(container.objects))
        eq_l('system.heading.reset', container.title1)

        eq_l('system.heading.reset-favorites',            container.objects[0].title)
        eq_(Callback(system.ConfirmResetFavorites),       container.objects[0].key)

        eq_l('system.heading.reset-search',               container.objects[1].title)
        eq_(Callback(system.ConfirmResetSearches),        container.objects[1].key)

        eq_l('system.heading.reset-download-history',     container.objects[2].title)
        eq_(Callback(system.ConfirmResetDownloads),       container.objects[2].key)

        eq_l('system.heading.reset-download-failed',      container.objects[3].title)
        eq_(Callback(system.ConfirmResetDownloadsFailed), container.objects[3].key)

        eq_l('system.heading.reset-ss-cache',             container.objects[4].title)
        eq_(Callback(system.ConfirmResetSSCache),         container.objects[4].key)

        eq_l('system.heading.reset-factory',              container.objects[5].title)
        eq_(Callback(system.ConfirmResetFactory),         container.objects[5].key)

    def test_status_menu():
        import system
        import mock

        @mock.patch.object(bridge.plex, 'section_destination')
        def test(dest):
            container = system.StatusMenu()
            call = mock.call
            eq_([ call('movie'), call('show') ], dest.call_args_list)
            return container

        container = test()
        eq_(4, len(container.objects))

        eq_f('system.status.movie-destination', container.objects[0].title)
        eq_f('system.status.show-destination',  container.objects[1].title)
        eq_f('system.status.download-strategy', container.objects[2].title)
        eq_f('system.status.version',           container.objects[3].title)

    def test_confirmations():
        import system

        container = system.ConfirmResetFavorites()
        eq_l('system.warning.reset-favorites', container.header)
        eq_l('confirm.yes', container.objects[0].title)

        container = system.ConfirmResetSearches()
        eq_l('system.warning.reset-search', container.header)
        eq_l('confirm.yes', container.objects[0].title)

        container = system.ConfirmResetDownloads()
        eq_l('system.warning.reset-download-history', container.header)
        eq_l('confirm.yes', container.objects[0].title)

        container = system.ConfirmResetDownloadsFailed()
        eq_l('system.warning.reset-download-failed', container.header)
        eq_l('confirm.yes', container.objects[0].title)

        container = system.ConfirmResetSSCache()
        eq_l('system.warning.reset-ss-cache', container.header)
        eq_l('confirm.yes', container.objects[0].title)

        container = system.ConfirmResetFactory()
        eq_l('system.warning.reset-factory', container.header)
        eq_l('confirm.yes', container.objects[0].title)

    def test_actual_resets():
        import system
        import mock

        @mock.patch.object(bridge.favorite, 'clear')
        def test_reset(reset_call):
            container = system.ResetFavorites()
            reset_call.assert_called_once_with()
            eq_l('heading.system', container.header)
            eq_l('system.response.reset-favorites', container.message)

        test_reset()

        @mock.patch.object(bridge.search, 'clear')
        def test_reset(reset_call):
            container = system.ResetSearches()
            reset_call.assert_called_once_with()
            eq_l('heading.system', container.header)
            eq_l('system.response.reset-search', container.message)

        test_reset()

        @mock.patch.object(bridge.download, 'clear_history')
        def test_reset(reset_call):
            container = system.ResetDownloads()
            reset_call.assert_called_once_with()
            eq_l('heading.system', container.header)
            eq_l('system.response.reset-download-history', container.message)

        test_reset()

        @mock.patch.object(bridge.download, 'clear_failed')
        def test_reset(reset_call):
            container = system.ResetDownloadsFailed()
            reset_call.assert_called_once_with()
            eq_l('heading.system', container.header)
            eq_l('system.response.reset-download-failed', container.message)

        test_reset()

        @mock.patch.object(system.ss.util, 'clear_cache')
        def test_reset(reset_call):
            container = system.ResetSSCache()
            reset_call.assert_called_once_with()
            eq_l('heading.system', container.header)
            eq_l('system.response.reset-ss-cache', container.message)

        test_reset()

        @mock.patch.object(Dict, 'Reset')
        @mock.patch.object(Dict, 'Save')
        @mock.patch.object(system.ss.util, 'clear_cache')
        def test_reset(dict_reset, dict_save, ss_cache):
            container = system.ResetFactory()
            dict_reset.assert_called_once_with()
            dict_save.assert_called_once_with()
            ss_cache.assert_called_once_with()
            eq_l('heading.system', container.header)
            eq_l('system.response.reset-factory', container.message)

        test_reset()
