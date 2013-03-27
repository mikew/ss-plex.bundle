all_channels = None

try:
    JSON
except NameError, e:
    import bridge
    JSON = bridge.plex.config['JSON']

class ChannelInfo(object):
    def __init__(self, attrs):
        super(ChannelInfo, self).__init__()
        self.attrs        = attrs
        self.title        = attrs['title']
        self.bundle_name  = attrs['bundle']
        self.types        = attrs['type']
        self.description  = attrs['description']
        self.repo         = attrs['repo']
        self.branch       = attrs['branch']
        self.icon         = attrs['icon']
        self.hidden       = attrs['hidden']
        self.added_on     = attrs['date added']
        self.tracking_url = attrs['tracking url']

def info_for(bundle_name):
    channel = filter(lambda x: bundle_name == x['bundle'], channels_from_json())
    if channel:
        return ChannelInfo(channel[0])

def channels_from_json():
    global all_channels

    if not all_channels:
        all_channels = JSON.ObjectFromURL('http://raw.github.com/mikedm139/UnSupportedAppstore.bundle/master/Contents/Resources/plugin_details.json')

    return all_channels
