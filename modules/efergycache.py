from diskcache import Cache
import json
from functools import wraps
import boto3
from datetime import datetime
import os

class EfergyCache():

    _CACHE_LOCATION  =  '/tmp/efergy'
        
    def add_items(self, key, item):
        value =  self._serialize_json(item)
        with Cache(self._CACHE_LOCATION) as cache:
            cache.add(key,value)
    
    def get_items(self, key):
        with Cache(self._CACHE_LOCATION) as cache:
            value = cache.get(key)
            if value:
                return self._deserialize_json(value)
            
            return False
    
    def delete_items(self,  key):
        with Cache(self._CACHE_LOCATION) as cache:
            cache.delete(key)
        
    def clear_cache(self):
        with Cache(self._CACHE_LOCATION) as cache:
            cache.clear()
        
    def _serialize_json(self, item):
        return json.dumps(item).encode('utf-8')
    
    def _deserialize_json(self, item):
        return json.loads(item)

# Decorators


def get_cached_items(*args, **kwargs):

    func = None
    if len(args) == 1 and __builtins__.callable(args[0]):
        func = args[0]

    if not func:
        key = kwargs.get('key')
    
    def callable(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            cache = EfergyCache()
            if len(args) > 1:
                item = cache.get_items(args[1])
            else:
                item = cache.get_items(key)
            if not item:
                item  = func(*args, **kwargs)
                cache.add_items(key, item)
            return item
        return wrapped
    return callable(func) if func else callable

def delete_items(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        cache = EfergyCache()
        cache.clear_cache()
        item = func(*args, **kwargs)
        return item
    return wrapper

def clear_worker_cache(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        client = boto3.client("lambda")
        msg = {"key":"clear_cache", "at":datetime.utcnow().isoformat()}
        client.invoke(
            FunctionName=os.getenv("WORKER_LAMBDA_NAME"),
            InvocationType="Event",
            Payload=json.dumps(msg)
        )
        item = func(*args, **kwargs)
        return item
    return wrapper