from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@socketio.on('message')
def handle_message(data):
    print(f"[INFO] Received message: {data['msg']} from room: {data['room']}")
    socketio.send(data, room=data['room'])

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    narration_message = "{} has entered the room.{}".format(data['userName'], data['room'])
    socketio.send({'msg': narration_message}, room=room)


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    print(f"[INFO] {data['userName']} has left room: {room}")
    narration_message = "{} has left the room.{}".format(data['userName'], data['room'])
    socketio.send({'msg': narration_message}, room=room)

    leave_room(room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)