import plex_nose

class UIHelpersTest(plex_nose.TestCase):
    def test_plobj():
        from ui import plobj
        subject = plobj(DirectoryObject, 'title', noop, icon = PLUGIN_ART)

        eq_('DirectoryObject', subject.__class__.__name__)
        eq_l('title', subject.title)
        eq_(R(PLUGIN_ART), subject.thumb)
        eq_(Callback(noop), subject.key)

    def test_plobj_with_f():
        from ui import plobj
        subject = plobj(DirectoryObject, F('system.status.version', '1.0'), noop, icon = PLUGIN_ART)

        eq_('DirectoryObject', subject.__class__.__name__)
        eq_f('system.status.version', subject.title)
        eq_(R(PLUGIN_ART), subject.thumb)
        eq_(Callback(noop), subject.key)

    def test_input_button():
        subject = input_button('foo', 'prompt', noop)

        eq_('InputDirectoryObject', subject.__class__.__name__)
        eq_l('foo', subject.title)
        eq_l('prompt', subject.prompt)
        eq_(Callback(noop), subject.key)

    def test_popup_button():
        subject = popup_button('title', noop)
        eq_('PopupDirectoryObject', subject.__class__.__name__)
        eq_l('title', subject.title)
        eq_(Callback(noop), subject.key)

    def test_button():
        subject = button('title', noop)
        eq_('DirectoryObject', subject.__class__.__name__)
        eq_l('title', subject.title)
        eq_(Callback(noop), subject.key)

    def test_warning():
        pass
    def test_confirm():
        pass
    def test_dialog():
        pass
