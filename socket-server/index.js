require('dotenv').config()
const PORT = process.env.PORT
const HOST = process.env.HOST
const ALLOWED_ORIGIN = process.env.ALLOWED_ORIGIN

const express = require('express')
const http = require('http');
const app = express()
const server = http.createServer(app);
const {Server} = require("socket.io");
const cors = require("cors");
const BadRequest = require("./utils/classes/bad-request");
const {finpayOrderCheck} = require("./utils/finnet-check-order");
const io = new Server(server, {
   cors: {
      origin: '*' //'https://haddock-flexible-mouse.ngrok-free.app'
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

app.post('/hit_channel', async (req, res) => {
   try {
      if (!req.body.channel) return res.status(400).json({
         message: 'Bad request, invalid channel name'
      })
      const paymentData = await finpayOrderCheck(req.body.data?.order_id)
      if (paymentData && req.body.data?.status !== paymentData.result.payment.status) throw new BadRequest('Bad request, invalid status')

      io.emit(req.body.channel, {...req.body.data, ...paymentData})
      res.status(200).json({
         message: 'success'
      })
   } catch (e) {
      if (e instanceof BadRequest) return res.status(400).json({
         message: e.message
      })
      res.status(500).json({message: e.message})
   }
})


io.on('connection', (socket) => {
   console.log("Client connected: ", socket.id)
   socket.on('disconnect', () => console.log('Client dc', socket.id));
});


server.listen(PORT, HOST, () => {
   console.log(`Aplikasi berjalan di port ${PORT}`)
})