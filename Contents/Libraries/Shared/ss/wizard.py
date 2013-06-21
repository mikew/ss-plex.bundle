import util
from consumer import Consumer
import environment
import cache

log = util.getLogger('ss.wizard')

def get_payload(endpoint):
    ttl      = cache.TIME_HOUR / 2
    endpoint = util.sources_endpoint(endpoint)

    return environment.json_from_url(endpoint, expires = ttl)

def translate(foreign):
    final_url = foreign.get('final_url')

    if final_url:
        return final_url
    else:
        endpoint = util.translate_endpoint( foreign['original_url'], foreign['foreign_url'])
        response = environment.json_from_url(endpoint)

        return util.translated_from(response)

class Wizard(object):
    def __init__(self, endpoint, avoid_flv = False, start_at = 0):
        self.endpoint    = endpoint
        self.file_hint   = None
        self.avoid_flv   = avoid_flv
        self.consumer    = None
        self.start_at    = start_at
        self.source_list = []

        try:
            self.payload     = get_payload(self.endpoint)
            self.source_list = self.payload.get('items', [])
            self.file_hint   = str(self.payload['resource']['display_title'])

            log.debug('%s has %s sources' % (self.file_hint, len(self.source_list)))
        except Exception, e:
            log.exception('Unable to get wizard info for %s' % endpoint)
            pass

    def sources(self, cb):
        all_sources = self.source_list[self.start_at:]

        for foreign in all_sources:
            translated = None
            try:
                translated = translate(foreign)
                consumer   = Consumer(translated)

                if self.avoid_flv and '.flv' in consumer.asset_url():
                    log.info('Avoiding .flv')
                    raise Exception('Avoiding .flv')

                cb(consumer)
                self.consumer = consumer
                break
            except Exception, e:
                log.exception('Error on %s' % translated)
                self.consumer = None
                continue
