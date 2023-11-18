import spotipy
import pymongo
import os
import random
import subprocess

from video import updateSong_bing
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

# Spotify API 인증 정보
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Spotify API 클라이언트 인증
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# 플레이리스트 검색
playlist_name = "트로트"
results = sp.search(q=playlist_name, type="playlist", market="KR")

# MongoDB 연결
mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')
mongo_client = pymongo.MongoClient(mongo_connection_string)

test_collection = mongo_client.Genre.Trot
test_collection.delete_many({})

if results["playlists"]["total"] > 0:
    playlists = results["playlists"]["items"]
    random_playlist = random.choice(playlists)

    playlist_name = random_playlist["name"]

    # 플레이리스트의 트랙 목록 가져오기
    playlist_tracks = sp.playlist_tracks(random_playlist["id"], market="KR")
    total_tracks = min(200, playlist_tracks["total"])

    for offset in range(0, total_tracks, 100):
        tracks = sp.playlist_tracks(random_playlist["id"], offset=offset, limit=100)
        for track in tracks["items"]:
            track_name = track["track"]["name"]
            artist_name = track["track"]["artists"][0]["name"]

            # MongoDB에 데이터 저장
            test_collection.insert_one({
                "track_name": track_name,
                "artist_name": artist_name,
            })

updateSong_bing(test_collection) # WebDriver 인스턴스 사용

# 연결 종료
mongo_client.close()
subprocess.Popen(['python3', '/home/ubuntu/BGM_Back/Chatroom/SongMergeRun.py'])
