const express = require("express");
const http = require("http");
const { Server } = require("socket.io");
const { setupWSConnection } = require("y-websocket/bin/utils");
const WebSocket = require("ws");

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"],
  },
});

// WebSocket server for Y.js
const wss = new WebSocket.Server({ noServer: true });

const PORT = process.env.PORT || 4000;

// Handle WebSocket connections for Y.js
wss.on("connection", setupWSConnection);

// Handle Socket.IO connections for cursor awareness
io.on("connection", (socket) => {
  console.log("User connected:", socket.id);

  socket.on("cursor-update", (data) => {
    // Broadcast cursor position to all other clients
    socket.broadcast.emit("cursor-update", {
      userId: socket.id,
      ...data,
    });
  });

  socket.on("disconnect", () => {
    console.log("User disconnected:", socket.id);
    io.emit("user-disconnected", socket.id);
  });
});

// Handle upgrade requests
server.on("upgrade", (request, socket, head) => {
  const pathname = request.url;

  if (pathname === "/yjs") {
    wss.handleUpgrade(request, socket, head, (ws) => {
      wss.emit("connection", ws, request);
    });
  }
});

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
