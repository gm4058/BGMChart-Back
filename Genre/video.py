from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib.parse import quote

def init_webdriver():
    # WebDriver 설정
    webdriver_options = Options()
    webdriver_options.add_argument('--headless')  # 헤드리스 모드 설정
    webdriver_options.add_argument('--no-sandbox')
    webdriver_options.add_argument('--disable-dev-shm-usage')

    # WebDriver 초기화
    wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=webdriver_options)

    return wd

def close_webdriver(wd):
    wd.quit()

def process_song_google(song, collection):
    wd = init_webdriver()
    title = song.get('track_name')
    singer = song.get('artist_name')
    
    # Google 검색 URL
    search_query = f"{title} {singer}"
    search_url = f"https://www.google.com/search?q={quote(search_query)}&tbm=vid"
    
    print("검색 URL:", search_url)

    # 검색결과 가져오기
    wd.get(search_url)
    wait = WebDriverWait(wd, 10)
    a_tag = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.xe8e1b > div > div > span > a')))
    video_link = a_tag.get_attribute('href') if a_tag else None

    for i in range(1, 10, 1):
        if "https://www.youtube.com" not in video_link:
            a_tags = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.xe8e1b > div > div > span > a')))
            if len(a_tags) > 1:
                video_link = a_tags[i].get_attribute('href')
            else:
                video_link = None
        else:
            break
    
    if "https://www.youtube.com" not in video_link:
        filter = {'_id': song['_id']}
        collection.delete_one(filter)
        video_link = None
        
    if video_link:
        collection.update_one(
            {'_id': song['_id']},
            {'$set': {'video_link': video_link}}
        )
    else:
        collection.delete_one({'_id': song['_id']})
    
    close_webdriver(wd)

def updateSong_google(collection):
    songs = collection.find()
    num_threads = 4

    # ThreadPoolExecutor를 생성합니다
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 곡 리스트를 각 스레드에 분배하여 병렬 처리합니다
        for song in songs:
            executor.submit(process_song_google, song, collection)

def process_song_bing(song, collection):
    wd = init_webdriver()
    title = song.get('track_name')
    singer = song.get('artist_name')

    # Bing 검색 URL
    search_query = f"{title} {singer} youtube"
    search_url = f"https://www.bing.com/videos/search?q={quote(search_query)}"
    
    print("검색 URL:", search_url)

    # 검색결과 가져오기
    wd.get(search_url)
    wait = WebDriverWait(wd, 10)
    a_tag = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[3]/div[2]/div/div[2]/div[1]/div[1]/div/a/div')))    
    video_link = a_tag.get_attribute('ourl') if a_tag else None
    
    for i in range(2, 10, 1):
        if "https://www.youtube.com" not in video_link:
            a_tag = wait.until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[4]/div[3]/div[2]/div/div[2]/div[1]/div[{i}]/div/a/div')))
            video_link = a_tag.get_attribute('ourl') if a_tag else None
        else:
            break
    
    if video_link:
        collection.update_one(
            {'_id': song['_id']},
            {'$set': {'video_link': video_link}}
        )
    else:
        collection.delete_one({'_id': song['_id']})

    close_webdriver(wd)

def updateSong_bing(collection):
    songs = collection.find()
    num_threads = 4

    # ThreadPoolExecutor를 생성합니다
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # 곡 리스트를 각 스레드에 분배하여 병렬 처리합니다
        for song in songs:
            executor.submit(process_song_bing, song, collection)
