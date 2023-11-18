from pytube import YouTube
from pymongo import MongoClient
from pydub import AudioSegment
from dotenv import load_dotenv
import os

# MongoDB Connection
load_dotenv()

def SongMerge(allgenre):  # ---> , check
    mongo_connection_string = os.getenv('MONGO_CONNECTION_STRING')
    mongoClient = MongoClient(mongo_connection_string)

    # Connect to MongoDB
    mongoCollection = mongoClient['Genre'][allgenre] 

    # MongoDB에서 노래 정보 가져오기
    batch_size = 10
    total_songs = mongoCollection.count_documents({})
    processed_songs = 0

    while processed_songs < total_songs:
        # 추출한 음원들을 저장할 리스트 (while 루프 내에서 초기화)
        extracted_audios = []

        songs = mongoCollection.find().sort("_id").skip(processed_songs).limit(batch_size)
        
        # 유튜브 URL을 사용하여 오디오 추출
        for i, song in enumerate(songs):
            if 'video_link' not in song or song['video_link'] is None:
                continue
            if "youtube.com" not in song['video_link']:
                continue
                
            url = song['video_link']
            print(f"Current URL: {url}")
            try:
                yt = YouTube(url)
                if yt.age_restricted or yt.length > 420:
                    print(f"Skipping age-restricted video: {url}")
                    continue
                audio = yt.streams.filter(only_audio=True).first().download(output_path='/home/ubuntu/BGM_Back/Chatroom', filename=f'temp_audio_{i}')
                extracted_audios.append(audio)
            except Exception as e:
                print(f"Failed to extract audio from {url}: {str(e)}")
        
        print(f"Current extracted_audios: {extracted_audios}")
        
        # 추출한 음원들을 합치기
        combined_audio = AudioSegment.empty()
        for audio_file in extracted_audios:
            try:
                audio = AudioSegment.from_file(audio_file)
                combined_audio += audio
            except Exception as e:
                print(f"Failed to process audio file {audio_file}: {str(e)}")
        
        # 결과 파일로 저장
        output_dir = "/home/ubuntu/BGM_Back/MusicStrem/"+allgenre  # -----> +check
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{allgenre}_combined_audio_{processed_songs + 1}-{processed_songs + batch_size}.mp3") # ---->{check}
        combined_audio.export(output_file, format="mp3")
        
        
        # 임시 파일 삭제
        for audio_file in extracted_audios:
            try:
                os.remove(audio_file)
            except FileNotFoundError:
                pass
            
        processed_songs += batch_size
