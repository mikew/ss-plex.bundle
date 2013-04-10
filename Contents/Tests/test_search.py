import plex_nose

class SearchTests(plex_nose.TestCase):
    def test_main_menu():
        import search
        import mock

        saved_searches = [ 'a', 'z', 'the middle' ]

        @mock.patch.object(bridge.search, 'collection', return_value = saved_searches)
        def test(*a):
            return search.MainMenu()

        container = test()
        eq_l('a', container.objects[0].title)
        eq_(Callback(search.ResultsMenu, query = 'a', foo = 1), container.objects[0].key)
        eq_l('the middle', container.objects[1].title)
        eq_l('z', container.objects[2].title)

    def test_results_menu():
        import search
        import mock

        query = 'query'

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(search.bridge.search, 'includes', return_value = False)
        def test(render_call, includes_call):
            container = search.ResultsMenu(query)
            render_call.assert_called_once_with(query)
            return container

        container = test()
        eq_l('search.heading.add', container.objects[0].title)
        eq_(Callback(search.Toggle, query = query), container.objects[0].key)

    def test_results_menu_when_saved():
        import search
        import mock

        query = 'query'

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(search.bridge.search, 'includes', return_value = True)
        def test(render_call, includes_call):
            container = search.ResultsMenu(query)
            render_call.assert_called_once_with(query)
            return container

        container = test()
        eq_l('search.heading.remove', container.objects[0].title)
        eq_(Callback(search.Toggle, query = query), container.objects[0].key)
