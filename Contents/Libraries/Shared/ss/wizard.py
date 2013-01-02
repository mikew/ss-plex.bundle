from consumer import Consumer
import util
import environment
import cache

class Wizard(object):
    def __init__(self, endpoint, environment = environment.default, avoid_flv = False):
        super(Wizard, self).__init__()
        self.endpoint    = endpoint
        self.file_hint   = None
        self.avoid_flv   = avoid_flv
        self.environment = environment

        try:
            def get_sources():
                return util.gzip_request(util.sources_endpoint(self.endpoint))

            self.payload   = self.environment.str_to_json(cache.fetch('%s-sources' % self.endpoint, get_sources, expires = cache.TIME_HOUR / 2))
            self.file_hint = self.payload['resource']['display_title']
        except Exception, e:
            util.print_exception(e)
            pass

    def filtered_sources(self):
        filtered = []

        try:
            sources  = self.payload.get('items', [])
            filtered = filter(lambda x: x['_type'] == 'foreign', sources)
        except: pass

        return filtered

    def translate(self, foreign):
        final_url = foreign.get('final_url')

        if final_url:
            return final_url
        else:
            response = self.environment.json( util.translate_endpoint( foreign['original_url'], foreign['foreign_url'] ) )
            return util.translated_from(response)

    #def sources(self):
        #for foreign in self.filtered_sources():
            #try:
                #consumer = Consumer(self.translate(foreign), environment = self.environment)
                #consumer.consume()
                #yield consumer
                #break
            #except GeneratorExit:
                #pass
            #except Exception, e:
                #util.print_exception(e)
                #continue

    def sources(self, cb):
        for foreign in self.filtered_sources():
            try:
                consumer = Consumer(self.translate(foreign), environment = self.environment)

                if self.avoid_flv and '.flv' in consumer.asset_url():
                    raise Exception('Avoiding .flv')

                cb(consumer)
                break
            except Exception, e:
                util.print_exception(e)
                continue

if __name__ == '__main__':
    import os, sys
    args     = sys.argv
    test_url = args[1]

    found = None
    def test():
        w = Wizard(test_url)
        print w.file_hint

        def print_url(c):
            global found
            found = c.asset_url()

        def print_every_url(c):
            print c.url
            print c.asset_url()
            print c.file_name()

            raise Exception('moving on.')

        #w.sources(print_url)
        #print found
        w.sources(print_every_url)

    test()
