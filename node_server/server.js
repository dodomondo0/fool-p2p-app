// node_server/server.js
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
// Socket.IO сервер с настройками CORS
const io = socketIo(server, {
  cors: {
    origin: "*", // Для разработки. В продакшене лучше указать конкретный origin.
    methods: ["GET", "POST"]
  },
  transports: ['websocket', 'polling'] // Поддержка обоих транспортов
});

// Хранилище комнат в памяти (как в Python)
const rooms = {};

// --- Базовая страница ---
app.get('/', (req, res) => {
  res.send('Node.js Signaling Server for P2P Fool Game is running');
});

// --- Socket.IO Events ---

io.on('connection', (socket) => {
  console.log(`[Socket.IO] Client connected: ${socket.id}`);

  socket.on('disconnect', () => {
    console.log(`[Socket.IO] Client disconnected: ${socket.id}`);
    // Очистка комнат при отключении клиента
    let roomsToRemove = [];
    for (const roomName in rooms) {
      const roomData = rooms[roomName];
      if (roomData.clients) {
        const clientIndex = roomData.clients.indexOf(socket.id);
        if (clientIndex !== -1) {
          roomData.clients.splice(clientIndex, 1);
          console.log(`[Socket.IO] Client ${socket.id} removed from room ${roomName}`);
        }
        // Если хост отключился
        if (roomData.host_id === socket.id) {
          roomsToRemove.push(roomName);
          console.log(`[Socket.IO] Host ${socket.id} left room ${roomName}. Marking room for deletion.`);
        }
      }
    }
    // Удаление комнат без хоста
    roomsToRemove.forEach(roomName => {
      if (rooms[roomName]) {
        delete rooms[roomName];
        console.log(`[Socket.IO] Room ${roomName} deleted (host disconnected)`);
      }
    });
  });

  // --- Обработка присоединения к комнате ---
  socket.on('join', (data) => {
    const roomName = data.room;
    const password = data.password || '';
    const isHost = data.is_host || false;

    console.log(`[Socket.IO] Join request: room=${roomName}, is_host=${isHost}, has_password=${!!password}`);

    if (!roomName) {
      socket.emit('joined', { status: 'error', message: 'Room name is required' });
      return;
    }

    if (isHost) {
      if (rooms[roomName]) {
        socket.emit('joined', { status: 'error', message: 'Room already exists' });
        return;
      }

      rooms[roomName] = {
        host_id: socket.id,
        password: password,
        clients: [socket.id]
      };

      socket.join(roomName);
      socket.emit('joined', { status: 'success', message: 'Room created successfully', room: roomName });
      console.log(`[Socket.IO] Room ${roomName} created by ${socket.id}`);
    } else {
      if (!rooms[roomName]) {
        socket.emit('joined', { status: 'error', message: 'Room not found' });
        return;
      }

      const roomData = rooms[roomName];

      if (roomData.password && password !== roomData.password) {
        socket.emit('joined', { status: 'error', message: 'Invalid password' });
        return;
      }

      if (!roomData.clients.includes(socket.id)) {
        roomData.clients.push(socket.id);
      }

      socket.join(roomName);
      socket.emit('joined', { status: 'success', message: 'Joined room successfully', room: roomName });
      console.log(`[Socket.IO] Client ${socket.id} joined room ${roomName}`);
    }
  });

  // --- Обработка сигнальных сообщений (WebRTC) ---
  socket.on('signal', (data) => {
    const targetId = data.target;
    const roomName = data.room;

    if (roomName && rooms[roomName]) {
      const roomData = rooms[roomName];
      if (roomData.clients && roomData.clients.includes(targetId)) {
        console.log(`[Socket.IO] Forwarding signal from ${data.sender} to ${targetId}`);
        // Отправляем сигнал целевому клиенту
        socket.to(targetId).emit('signal', data);
      } else {
        console.log(`[Socket.IO] Target ${targetId} not found in room ${roomName} for signal forwarding`);
      }
    } else {
      console.log(`[Socket.IO] Room ${roomName} not found for signal forwarding`);
    }
  });

  // --- Объявление доступного хоста ---
  socket.on('host_available', (data) => {
    const roomName = data.room;
    const hostId = data.host_id;

    if (roomName && rooms[roomName]) {
      rooms[roomName].host_id = hostId;
      console.log(`[Socket.IO] Host ${hostId} available in room ${roomName}`);
      // Уведомляем всех в комнате о новом хосте
      io.to(roomName).emit('host_available', data);
    }
  });

});

// --- Запуск сервера ---
const PORT = process.env.PORT || 10000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`[Server] Node.js Signaling Server is running on port ${PORT}`);
});