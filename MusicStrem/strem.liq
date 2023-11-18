#!/usr/bin/liquidsoap
Balladeplaylist = playlist("/home/ubuntu/BGM_Back/MusicStrem/Ballade")
Danceplaylist = playlist("/home/ubuntu/BGM_Back/MusicStrem/Dance")
Folkplaylist = playlist("/home/ubuntu/BGM_Back/MusicStrem/Folk")
HipHopplaylist = playlist("/home/ubuntu/BGM_Back/MusicStrem/HipHop")
Indieplaylist = playlist("/home/ubuntu/BGM_Back/MusicStrem/Indie")
RBplaylist = playlist("/home/ubuntu/BGM_Back/MusicStrem/RB")
Rockplaylist = playlist("/home/ubuntu/BGM_Back/MusicStrem/Rock")
Trotplaylist = playlist("/home/ubuntu/BGM_Back/MusicStrem/Trot")

# 각 플레이리스트의 볼륨 조절
Balladeplaylist = amplify(0.1, Balladeplaylist) # 0.5는 볼륨을 50%로 줄입니다.
Danceplaylist = amplify(0.1, Danceplaylist)
Folkplaylist = amplify(0.1, Folkplaylist)
HipHopplaylist = amplify(0.1, HipHopplaylist)
Indieplaylist = amplify(0.1, Indieplaylist)
RBplaylist = amplify(0.1, RBplaylist)
Rockplaylist = amplify(0.1, Rockplaylist)
Trotplaylist = amplify(0.1, Trotplaylist)

# Icecast에 스트리밍
output.icecast(%mp3, host = "localhost", port = 8000, password = "hackme", mount = "/Ballade.mp3", mksafe(Balladeplaylist))
output.icecast(%mp3, host = "localhost", port = 8000, password = "hackme", mount = "/Dance.mp3", mksafe(Danceplaylist))
output.icecast(%mp3, host = "localhost", port = 8000, password = "hackme", mount = "/Folk.mp3", mksafe(Folkplaylist))
output.icecast(%mp3, host = "localhost", port = 8000, password = "hackme", mount = "/HipHop.mp3", mksafe(HipHopplaylist))
output.icecast(%mp3, host = "localhost", port = 8000, password = "hackme", mount = "/Indie.mp3", mksafe(Indieplaylist))
output.icecast(%mp3, host = "localhost", port = 8000, password = "hackme", mount = "/RB.mp3", mksafe(RBplaylist))
output.icecast(%mp3, host = "localhost", port = 8000, password = "hackme", mount = "/Rock.mp3", mksafe(Rockplaylist))
output.icecast(%mp3, host = "localhost", port = 8000, password = "hackme", mount = "/Trot.mp3", mksafe(Trotplaylist))