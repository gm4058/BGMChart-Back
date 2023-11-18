import subprocess
from SongMerge import SongMerge

genres = ['Ballade', "Dance", 'Folk', 'HipHop', 'Indie', 'RB', 'Rock', 'Trot']


""" # check 값을 파일에 저장하는 함수 --------------------------------> 스트리밍 서버가 플레이리스트로 메모리에 로드되어서 1번mp3가 변경되어도 기존의 mp3가 스트리밍되고 
def save_check_value(value):                                          1번 mp3가 끝나야 바뀐 2번 mp3가 로드되어서 스트리밍됨 따라서 체크 굳이 필요없을거같음 혹시몰라서 주석처리
    with open('/home/ubuntu/BGM_Back/Chatroom/check.txt', 'w') as f:
        f.write(str(value))

# 저장된 check 값을 읽어오는 함수
def load_check_value():
    try:
        with open('/home/ubuntu/BGM_Back/Chatroom/check.txt', 'r') as f:
            value = int(f.read())
        return value
    except FileNotFoundError:
        return 1

# 이전에 저장된 check 값을 읽어옴
check = load_check_value()

# check 값에 따라 다른 값으로 설정
if check == 2:
    check = 1
else:
    check = 2 """

# genres 리스트를 반복하여 SongMerge 함수 실행
for genre in genres:
    SongMerge(genre) # ---> , str(check)

# 프로그램이 끝난 후 check 값을 저장
# save_check_value(check)

