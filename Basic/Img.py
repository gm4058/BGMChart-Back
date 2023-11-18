import spotipy
import pymongo
import os

from spotipy.oauth2 import SpotifyClientCredentials
from cachetools import cached, TTLCache
from dotenv import load_dotenv

cache = TTLCache(maxsize=1000, ttl=43200)
load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')
mongo_client = pymongo.MongoClient(mongo_connection_string)

def get_closest_image_size(images, desired_width, desired_height):
    closest_image = None
    closest_size_difference = None

    for image in images:
        size_difference = abs(image['width'] - desired_width) + abs(image['height'] - desired_height)

        if closest_size_difference is None or size_difference < closest_size_difference:
            closest_image = image
            closest_size_difference = size_difference

    return closest_image

@cached(cache)
def get_artwork_url(title, singer):
    results = sp.search(q=title + ' ' + singer, type='track', market="KR", limit=1)
    items = results['tracks']['items']
    if len(items) > 0:
        images = items[0]['album']['images']
        closest_image = get_closest_image_size(images, 50, 50)
        return closest_image['url']
    else:
        return ''

test_collection = mongo_client.Music.Merge
documents = test_collection.find()

for document in documents:
    title = document['title']
    singer = document['singer']

    artwork_url = get_artwork_url(title, singer)

    test_collection.update_one(
        {'_id': document['_id']},
        {'$set': {'imgurl': artwork_url}}
    )

mongo_client.Music.Melon.drop()
mongo_client.Music.Bugs.drop()
mongo_client.Music.Genie.drop()
