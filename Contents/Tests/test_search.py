import plex_nose

class SearchTests(plex_nose.TestCase):
    def test_main_menu():
        import mock

        saved_searches = [ 'a', 'z', 'the middle' ]

        @mock.patch.object(bridge.search, 'collection', return_value = saved_searches)
        def test(*a):
            return search.MainMenu()

        container = test()
        eqL_(container.title1, 'heading.search')
        eqL_(container.objects[0].title, 'a')
        eqcb_(container.objects[0].key,  search.ResultsMenu,  query = 'a',  foo = 1)

        eqL_(container.objects[1].title, 'the middle')
        eqL_(container.objects[2].title, 'z')

    def test_results_menu():
        import mock

        query = 'query'

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(bridge.search, 'includes', return_value = False)
        def test(render_call, includes_call):
            container = search.ResultsMenu(query)
            render_call.assert_called_once_with(query)
            return container

        container = test()
        eqL_(container.objects[0].title, 'search.heading.add')
        eqcb_(container.objects[0].key, search.Toggle, query = query)

    def test_results_menu_when_existing():
        import mock

        query = 'query'

        @mock.patch.object(JSON, 'ObjectFromURL')
        @mock.patch.object(bridge.search, 'includes', return_value = True)
        def test(render_call, includes_call):
            container = search.ResultsMenu(query)
            render_call.assert_called_once_with(query)
            return container

        container = test()
        eqL_(container.objects[0].title, 'search.heading.remove')
        eqcb_(container.objects[0].key, search.Toggle, query = query)

    def test_toggle():
        import mock

        query = 'q'
        @mock.patch.object(bridge.search, 'collection', return_value = [])
        def test(*a):
            container = search.Toggle(query)
            ok_(bridge.search.includes(query))
            return container

        container = test()

        eqL_(container.message, 'search.response.added')

    def test_toggle_when_existing():
        import mock

        query = 'q'
        @mock.patch.object(bridge.search, 'collection', return_value = [query])
        def test(*a):
            container = search.Toggle(query)
            ok_(not bridge.search.includes(query))
            return container

        container = test()

        eqL_(container.message, 'search.response.removed')
