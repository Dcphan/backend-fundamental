import redis
import json

class CachingLayer:
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379, decode_responses=True)

    def getSongByArtist(self, artist: str):
        data = self.r.get(f"artist_search:{artist.lower()}")
        return json.loads(data)
    
    def setSongByArtist(self, artist: str, songs: list[dict], ttl: int):
        key = f"artist_search:{artist.lower()}"

        # Set + Expiration
        return self.r.setex(key, ttl, json.dumps(songs))
    
    def close(self):
        self.r.close()
    
