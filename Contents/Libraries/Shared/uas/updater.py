class GithubUpdater(object):
    """docstring for GithubUpdater"""
    def __init__(self, model):
        super(GithubUpdater, self).__init__()
        self.model = model

    def is_outdated(self):
        return self.model.branch

class ChannelModel(object):
    """docstring for ChannelModel"""
    def __init__(self, attrs):
        super(ChannelModel, self).__init__()
        self.attrs = attrs
        for k, v in attrs.iteritems():
            setattr(self, k, v)

def all_plugins():
    import json
    f = file('plugin_details.json')
    r = f.read()
    all_plugins = json.loads(r)
    f.close()

    return all_plugins

def id_to_model(id):
    for attrs in all_plugins():
        if attrs['title'] == id:
            return ChannelModel(attrs)

model = id_to_model('SS Plex')
updater = GithubUpdater(model)
print updater.is_outdated()
#strategy    = strategy.github
#environment = ss.environment.default

def notify_master(id):
    #HTTP.Request('/video/unsupportedappstore/notify-updated?title=%s' % q(id), immediate = True)
    pass

def check(**kwargs):
    klass = strategy(**kwargs)

    if klass.is_outdated():
        def perform_update():
            klass.update()
            notify_master(kwargs['id'])

        thread(perform_update)
        return dialog('updating')
    else:
        return dialog('fresh')
