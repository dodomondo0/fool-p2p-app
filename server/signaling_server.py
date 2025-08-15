from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

# Явно указываем eventlet как async_mode
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   transports=['websocket', 'polling'],
                   ping_timeout=60,
                   ping_interval=25,
                   async_mode='eventlet')

rooms = {}

@app.route('/')
def index():
    return "Signaling Server is running"

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")
    rooms_to_remove = []
    for room_name, room_data in list(rooms.items()):
        if request.sid in room_data.get('clients', []):
            room_data['clients'].remove(request.sid)
            if room_data.get('host_id') == request.sid:
                rooms_to_remove.append(room_name)
                print(f"Room {room_name} deleted (host disconnected)")
    
    for room_name in rooms_to_remove:
        if room_name in rooms:
            del rooms[room_name]

@socketio.on('join')
def handle_join(data):
    room_name = data.get('room')
    password = data.get('password', '')
    is_host = data.get('is_host', False)
    
    print(f"Join request: room={room_name}, is_host={is_host}, has_password={bool(password)}")
    
    if not room_name:
        emit('joined', {'status': 'error', 'message': 'Room name is required'})
        return
    
    if is_host:
        if room_name in rooms:
            emit('joined', {'status': 'error', 'message': 'Room already exists'})
            return
        
        rooms[room_name] = {
            'host_id': request.sid,
            'password': password,
            'clients': [request.sid]
        }
        join_room(room_name)
        emit('joined', {'status': 'success', 'message': 'Room created successfully', 'room': room_name})
        print(f"Room {room_name} created by {request.sid}")
        
    else:
        if room_name not in rooms:
            emit('joined', {'status': 'error', 'message': 'Room not found'})
            return
        
        room_data = rooms[room_name]
        
        required_password = room_data.get('password', '')
        if required_password and password != required_password:
            emit('joined', {'status': 'error', 'message': 'Invalid password'})
            return
        
        if request.sid not in room_data['clients']:
            room_data['clients'].append(request.sid)
        join_room(room_name)
        emit('joined', {'status': 'success', 'message': 'Joined room successfully', 'room': room_name})
        print(f"Client {request.sid} joined room {room_name}")

@socketio.on('signal')
def handle_signal(data):
    target = data['target']
    room = data.get('room')
    
    if room and room in rooms:
        room_data = rooms[room]
        if target in room_data.get('clients', []):
            print(f"Forwarding signal from {data['sender']} to {target}")
            emit('signal', data, room=target)
        else:
            print(f"Target {target} not found in room {room}")
    else:
        print(f"Room {room} not found or invalid")

@socketio.on('host_available')
def handle_host_available(data):
    room = data['room']
    host_id = data['host_id']
    
    if room in rooms:
        rooms[room]['host_id'] = host_id
        print(f"Host {host_id} available in room {room}")
        emit('host_available', data, room=room)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting signaling server on port {port}...")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)