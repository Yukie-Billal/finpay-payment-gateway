const axios = require('axios')

const FINNET_AUTH_KEY = process.env.FINNET_AUTH_KEY

const finpayOrderCheck = async orderId => {
  const res = await axios.get(`https://devo.finnet.co.id/pg/payment/card/check/${orderId}`, {
    headers: {
      Authorization: `Basic ${FINNET_AUTH_KEY}`
    }
  })
  if (res.status >= 400) throw new Error('Request check order error')
  return res.data.data
}

module.exports = { finpayOrderCheck }
