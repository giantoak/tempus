from __future__ import print_function
from hotqueue import HotQueue
import redis
import multiprocessing
import requests
import logging
import urllib
import usaddress
import json

class GetLoc(object):
    census_reporter = 'http://api.censusreporter.org/1.0/geo/elasticsearch?'
    sentinel = 'Xksm3k443209sfjxjzkz -- end --'    
    def __init__(self, queue_name='loc_queue', connection='localhost', reset_stats=False):
        self.q, self.r = self.get_redis(queue_name, connection)
        if reset_stats:
            self.reset_redis_stats()
    
    def get_redis(self, name, connection):
        return HotQueue(name), redis.Redis(connection)
    
    def retrieve(self, name, timeout=2):
        params = {'q': name, 'size': 1}
        url = self.census_reporter + urllib.urlencode(params)
        req = requests.get(url)
        if req.status_code != requests.codes.ok:
            logging.error(u'Error requesting {}: {}'.format(name, req.status_code))
            return 'error'
        else:
            try:
                res = req.json()['results']
            except:
                logging.error(u'Error parsing request for {}'.format(name))
                return 'error'
            
            try:
                resobj = res[0]
                logging.debug(u'Successfully geocoded {}'.format(name))
                return resobj
            except IndexError:
                logging.warning(u'No geocode found for {}'.format(name))
                return 'miss'
        
        return

    def retriever(self, worker_id, q, r, timeout=2):
        """Continuously grab geoids from Census Reporter"""

        
        for item in q.consume():

            # end loop
            if item == self.sentinel:
                logging.info('Received sentinel at {}'.format(worker_id))
                break
            
            # unpack tuple
            name, count = item

            logging.debug(u'Sending request for {} from worker {}'
                    .format(name, worker_id))
            resobj = self.retrieve(name, timeout)
            if isinstance(resobj, dict):
                # check if response state matches

                b = self.parse(name)

                if b['state'] in resobj['display_name']:
                    logging.debug(u'Matched {} with {}'.format(
                        resobj['display_name'], name))
                    
                    resobj['count'] = count
                    r.hset('_hits', name, resobj)
                    r.incr('success')
                else:
                    logging.debug(u'{} not found in {}'.format(
                        b['state'], resobj['display_name']))
                    r.incr('miss')
                    r.hset('_misses', name, {'count': count})

            elif resobj:
                # returned error
                r.incr(resobj)
                r.hset('_misses', name, {'count': count})
                    
        return

    def retrieve_all(self, locs, num_workers=1, timeout=2):
        workers = []
        logging.info('Putting locs into queue...')
        for (loc, count) in locs:
            self.q.put((loc, count))
        
        self.q.put(self.sentinel)
        for i in range(num_workers):
            p = multiprocessing.Process(target=self.retriever, args=(i, self.q, self.r, timeout))
            p.start()
            logging.info('Starting worker {}'.format(i))
            workers.append(p)

        for w in workers:
            w.join()
    
    def parse(self, name):
        usa = ', USA'
        if name.endswith(usa):
            name = name[:-len(usa)]
        
        try:
            parts = usaddress.parse(name)
        except UnicodeDecodeError:
            parts = ()
        
        place_parts = []
        state = ''
        
        for n, t in parts:
            if t == 'PlaceName':
                place_parts.append(n.strip(' ,'))
            elif t == 'StateName':
                state = n.strip(' ,')

        return {
                'place': ' '.join(place_parts),
                'state': state
                }


    def reset_redis_stats(self):
            self.r.set('success', 0)
            self.r.set('miss', 0)
            self.r.set('error', 0)
