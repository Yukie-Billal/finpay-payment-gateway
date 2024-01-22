require('dotenv').config()
const PORT = process.env.PORT
const HOST = process.env.HOST
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN

const express = require('express')
const http = require('http');
const app = express()
const server = http.createServer(app);
const { Server } = require("socket.io");
const cors = require("cors");
const io = new Server(server, {
  cors: {
    origin: ALLOWED_ORIGIN
  }
});

app.use(cors({
  origin: [ALLOWED_ORIGIN]
}))
app.use(express.json());
app.use((req, res, next) => {
  if (req.header('API_KEY') !== 'socket-apikey') return res.status(403).json({message: 'Unauthorized'})
  next()
})

app.get('/', (req, res) => {
  res.send('Hello world')
})

app.post('/hit_channel', (req, res) => {
  try {
    io.emit(req.body.channel, req.body.data)
    res.status(200).json({
      message: 'success'
    })
  } catch (e) {
    res.status(500).json({message: e.message})
  }
})


io.on('connection', (socket) => {
  socket.on('client_connection', data => {
    console.log("Client connected: ", data)
  });
  socket.on('disconnect', () => {});
});


server.listen(PORT, HOST, () => {console.log(`Aplikasi berjalan di port ${PORT}`)})