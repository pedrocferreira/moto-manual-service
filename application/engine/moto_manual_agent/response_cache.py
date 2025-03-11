import hashlib
import json
import os
from datetime import datetime, timedelta

class ResponseCache:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_duration = timedelta(hours=24)
    
    def _get_cache_key(self, query):
        return hashlib.md5(query.encode()).hexdigest()
    
    def get_cached_response(self, query):
        cache_key = self._get_cache_key(query)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                
            # Verifica se o cache ainda é válido
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time <= self.cache_duration:
                return cache_data['response']
        
        return None
    
    def cache_response(self, query, response):
        cache_key = self._get_cache_key(query)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        cache_data = {
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f) 