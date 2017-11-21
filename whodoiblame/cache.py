import hashlib
from pymemcache.client.base import Client
import pickle


def get_md5(to_hash):
    m = hashlib.md5()
    m.update(to_hash.encode('utf8'))
    return m.hexdigest()


class CacheClient:
    def __init__(self, config):
        self.cache_client = self.get_cache_client(config)

    def get_cache_client(self, config):
        return Client((config['MEMCACHE_HOST'], config['MEMCACHE_PORT']))

    def get(self, key):
        md5_key = get_md5(key)
        cache_pickle = self.cache_client.get(md5_key)
        if cache_pickle:
            cached_data = pickle.loads(cache_pickle)
            print("pulled data from cache %s" % (key))
            return cached_data
        return None

    def set(self, key, structure, expire=3600):
        md5_key = get_md5(key)
        self.cache_client.set(md5_key, pickle.dumps(structure), expire=expire)
        print("set data to cache %s, %s" % (key, structure))
