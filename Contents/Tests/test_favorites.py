import plex_nose

class FavoritesTests(plex_nose.TestCase):
    def test_main_menu():
        import mock

        show = dict(title = 'foo', artwork = 'foo.jpg', endpoint = '/')

        @mock.patch.object(bridge.favorite, 'collection', return_value = {'/':show})
        def test(*a):
            return favorites.MainMenu()

        container = test()
        eqL_(container.title1, 'heading.favorites')

        subject = container.objects[0]
        eq_(subject.title, show['title'])
        eq_(subject.thumb, show['artwork'])
        eqcb_(subject.key, generic.ListTVShow,
                refresh = 0,
                endpoint = show['endpoint'],
                show_title = show['title']
                )

    def test_toggle():
        import mock

        show = dict(title = 'foo', artwork = 'foo.jpg', endpoint = '/')

        @mock.patch.object(bridge.favorite, 'collection', return_value = {})
        def test(*a):
            container = favorites.Toggle(show['endpoint'], show['title'], show['artwork'])
            ok_(bridge.favorite.includes(show['endpoint']))
            return container

        container = test()
        eqF_(container.message, 'favorites.response.added')

    def test_toggle_when_existing():
        import mock

        show = dict(title = 'foo', artwork = 'foo.jpg', endpoint = '/')

        @mock.patch.object(bridge.favorite, 'collection', return_value = {'/':show})
        def test(*a):
            container = favorites.Toggle(show['endpoint'], show['title'], show['artwork'])
            ok_(not bridge.favorite.includes(show['endpoint']))
            return container

        container = test()
        eqF_(container.message, 'favorites.response.removed')
